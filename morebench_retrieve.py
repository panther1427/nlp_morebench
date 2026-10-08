#!/usr/bin/env python3
"""Retrieve MoReBench dilemmas and rubrics using cosine similarity."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Protocol
from sentence_transformers import SentenceTransformer

import numpy as np


DATASET_ID = "morebench/morebench"
DATASET_FILE = "morebench_public.csv"
DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
DEFAULT_CACHE_DIR = Path(".morebench_cache")


class Encoder(Protocol):
    """The part of SentenceTransformer used by the retriever."""

    def encode(self, sentences: Sequence[str], **kwargs: Any) -> Any: ...


def _resolve_hf_token(token: str | None) -> str | None:
    """Use an explicit Hugging Face token, then fall back to standard env vars."""
    candidates = (token, os.getenv("API_HUGGING_FACE"))
    return next((value.strip() for value in candidates if value and value.strip()), None)


def _parse_rubric(value: Any) -> Any:
    """Convert the CSV representation of a rubric to Python objects."""
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            # Keeping the original value is more useful than dropping a malformed
            # rubric from an otherwise valid retrieval result.
            return value


def _normalise_rows(rows: Any) -> list[dict[str, Any]]:
    """Accept a HF Dataset, pandas DataFrame, or sequence of mappings."""
    if hasattr(rows, "to_dict") and hasattr(rows, "columns"):
        rows = rows.to_dict(orient="records")

    result = [dict(row) for row in rows]
    if not result:
        raise ValueError("at least one reference dilemma is required")
    return result


def _normalise_embeddings(embeddings: Any) -> np.ndarray:
    """L2-normalise a two-dimensional embedding matrix."""
    matrix = np.asarray(embeddings, dtype=np.float32)
    if matrix.ndim != 2:
        raise ValueError("the encoder must return a 2D embedding matrix")
    if matrix.shape[1] == 0:
        raise ValueError("embeddings must contain at least one dimension")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("the encoder returned a non-finite embedding")
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("the encoder returned a zero-length embedding")
    return matrix / norms


class DilemmaRetriever:
    """Cosine-similarity index over dilemmas and their rubric criteria.

    ``rows`` may be a Hugging Face Dataset, pandas DataFrame, or any sequence of
    mappings. The encoder only needs a SentenceTransformer-compatible ``encode``
    method, which also makes the class straightforward to test.
    """

    def __init__(
        self,
        rows: Any,
        encoder: Encoder,
        *,
        dilemma_column: str = "DILEMMA",
        rubric_column: str = "RUBRIC",
        embeddings: Any | None = None,
    ) -> None:
        self.rows = _normalise_rows(rows)
        self.encoder = encoder
        self.dilemma_column = dilemma_column
        self.rubric_column = rubric_column

        for row_index, row in enumerate(self.rows):
            missing = [
                column
                for column in (dilemma_column, rubric_column)
                if column not in row
            ]
            if missing:
                raise ValueError(
                    f"row {row_index} is missing required column(s): "
                    f"{', '.join(missing)}"
                )

        self.dilemmas = [str(row[dilemma_column]) for row in self.rows]
        if embeddings is None:
            embeddings = encoder.encode(self.dilemmas, show_progress_bar=False)
        self.embeddings = _normalise_embeddings(embeddings)
        if len(self.embeddings) != len(self.rows):
            raise ValueError("there must be exactly one embedding per dilemma")

    def search(
        self,
        dilemma: str,
        k: int = 5,
        *,
        exclude_exact_match: bool = True,
    ) -> list[dict[str, Any]]:
        """Return the ``k`` closest dilemmas, rubrics, and cosine scores.

        Exact text matches are excluded by default. This prevents a benchmark
        dilemma from retrieving itself and leaking its own evaluation rubric.
        Set ``exclude_exact_match=False`` when retrieving the indexed item itself
        is intentional.
        """
        if not isinstance(dilemma, str) or not dilemma.strip():
            raise ValueError("dilemma must be a non-empty string")
        if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
            raise ValueError("k must be a positive integer")
        if not isinstance(exclude_exact_match, bool):
            raise TypeError("exclude_exact_match must be a boolean")

        dilemma = dilemma.strip()
        query = _normalise_embeddings(
            self.encoder.encode([dilemma], show_progress_bar=False)
        )[0]
        if self.embeddings.shape[1] != query.shape[0]:
            raise ValueError(
                "query and reference embeddings have different dimensions: "
                f"{query.shape[0]} and {self.embeddings.shape[1]}"
            )
        # Both operands are unit vectors, so the dot product is cosine similarity.
        scores = np.clip(self.embeddings @ query, -1.0, 1.0)
        candidate_indices = np.arange(len(scores))
        if exclude_exact_match:
            query_text = dilemma.casefold()
            candidate_indices = candidate_indices[
                np.asarray(
                    [text.strip().casefold() != query_text for text in self.dilemmas],
                    dtype=bool,
                )
            ]

        result_count = min(k, len(candidate_indices))
        # A stable full sort gives deterministic ordering when scores are equal.
        order = np.argsort(-scores[candidate_indices], kind="stable")[:result_count]
        indices = candidate_indices[order]

        return [
            {
                "rank": rank,
                "index": int(index),
                "cosine_similarity": float(scores[index]),
                "dilemma": self.rows[index][self.dilemma_column],
                "rubric": _parse_rubric(self.rows[index][self.rubric_column]),
            }
            for rank, index in enumerate(indices, start=1)
        ]


def load_morebench(*, token: str | None = None, split: str = "train") -> Any:
    """Load the public MoReBench CSV from Hugging Face."""
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise ImportError("Install project requirements to load MoReBench") from exc

    return load_dataset(
        DATASET_ID,
        token=_resolve_hf_token(token),
        data_files=DATASET_FILE,
        split=split,
    )


def _cache_key(model_name: str, dilemmas: Sequence[str]) -> str:
    digest = hashlib.sha256()
    digest.update(model_name.encode("utf-8"))
    for dilemma in dilemmas:
        digest.update(b"\0")
        digest.update(dilemma.encode("utf-8"))
    return digest.hexdigest()[:16]


def build_morebench_retriever(
    *,
    model_name: str = DEFAULT_MODEL,
    token: str | None = None,
    split: str = "train",
    cache_dir: str | Path | None = DEFAULT_CACHE_DIR,
) -> DilemmaRetriever:
    """Load MoReBench and build (or reuse) its embedding index."""
    # try:
    #     from sentence_transformers import SentenceTransformer
    # except ImportError as exc:
    #     raise ImportError("Install sentence-transformers to build the index") from exc

    token = _resolve_hf_token(token)
    rows = load_morebench(token=token, split=split)
    # The embedding model is a separate Hub download from the dataset and must
    # receive the token as well. Omitting it causes an unauthenticated request.
    encoder = SentenceTransformer(model_name, token=token)
    embeddings = None

    if cache_dir is not None:
        dilemmas = [str(value) for value in rows["DILEMMA"]]
        directory = Path(cache_dir)
        directory.mkdir(parents=True, exist_ok=True)
        cache_path = directory / f"embeddings-{_cache_key(model_name, dilemmas)}.npy"
        if cache_path.exists():
            embeddings = np.load(cache_path, allow_pickle=False)
        else:
            embeddings = encoder.encode(dilemmas, show_progress_bar=True)
            np.save(cache_path, np.asarray(embeddings, dtype=np.float32))

    return DilemmaRetriever(rows, encoder, embeddings=embeddings)


def retrieve_similar_dilemmas(
    dilemma: str,
    k: int = 5,
    **retriever_options: Any,
) -> list[dict[str, Any]]:
    """Convenience function returning MoReBench's ``k`` nearest dilemmas.

    For repeated queries, create one retriever with
    :func:`build_morebench_retriever` and call its ``search`` method instead so
    that the dataset and embedding model are loaded only once.
    """
    return build_morebench_retriever(**retriever_options).search(dilemma, k=k)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--dilemma", help="Dilemma text")
    source.add_argument("--dilemma-file", type=Path, help="UTF-8 text file")
    parser.add_argument("-k", type=int, default=5)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--hf-token",
        help="Hugging Face token (defaults to HF_TOKEN or HUGGING_FACE_HUB_TOKEN)",
    )
    parser.add_argument("--split", default="train")
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    if args.dilemma is not None:
        dilemma = args.dilemma
    elif args.dilemma_file is not None:
        dilemma = args.dilemma_file.read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        dilemma = sys.stdin.read()
    else:
        parser.error("provide --dilemma, --dilemma-file, or pipe text via stdin")

    results = retrieve_similar_dilemmas(
        dilemma,
        k=args.k,
        model_name=args.model,
        token=args.hf_token,
        split=args.split,
        cache_dir=None if args.no_cache else DEFAULT_CACHE_DIR,
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
