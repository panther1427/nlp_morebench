import os
import unittest
from unittest.mock import Mock, patch

import numpy as np

from morebench_retrieve import (
    DEFAULT_MODEL,
    DilemmaRetriever,
    _resolve_hf_token,
    build_morebench_retriever,
)


class FakeEncoder:
    vectors = {
        "animal": [1.0, 0.0],
        "people": [0.0, 1.0],
        "both": [1.0, 1.0],
        "query": [0.9, 0.1],
    }

    def encode(self, sentences, **kwargs):
        return np.asarray([self.vectors[text.strip().casefold()] for text in sentences])


class DilemmaRetrieverTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"DILEMMA": "animal", "RUBRIC": "[{'id': 1, 'title': 'Animal welfare'}]"},
            {"DILEMMA": "people", "RUBRIC": [{"id": 2, "title": "Human welfare"}]},
            {"DILEMMA": "both", "RUBRIC": "[]"},
        ]
        self.retriever = DilemmaRetriever(self.rows, FakeEncoder())

    def test_returns_closest_dilemmas_and_parsed_rubrics(self):
        results = self.retriever.search("query", k=2)

        self.assertEqual([result["dilemma"] for result in results], ["animal", "both"])
        self.assertEqual(results[0]["rubric"][0]["title"], "Animal welfare")
        self.assertGreater(results[0]["cosine_similarity"], results[1]["cosine_similarity"])

    def test_k_is_capped_at_dataset_size(self):
        self.assertEqual(len(self.retriever.search("query", k=20)), 3)

    def test_exact_query_is_excluded_by_default_to_prevent_rubric_leakage(self):
        results = self.retriever.search("  ANIMAL  ", k=3)

        self.assertNotIn("animal", [result["dilemma"] for result in results])
        self.assertEqual(len(results), 2)

    def test_exact_query_can_be_included_explicitly(self):
        results = self.retriever.search(
            "animal", k=1, exclude_exact_match=False
        )

        self.assertEqual(results[0]["dilemma"], "animal")
        self.assertAlmostEqual(results[0]["cosine_similarity"], 1.0)

    def test_rejects_invalid_input(self):
        with self.assertRaises(ValueError):
            self.retriever.search("", k=1)
        with self.assertRaises(ValueError):
            self.retriever.search("query", k=0)

    def test_rejects_invalid_reference_embeddings(self):
        with self.assertRaisesRegex(ValueError, "non-finite"):
            DilemmaRetriever(
                self.rows,
                FakeEncoder(),
                embeddings=[[1.0, 0.0], [np.nan, 1.0], [1.0, 1.0]],
            )

    def test_rejects_mismatched_query_dimension(self):
        class WrongQueryDimensionEncoder(FakeEncoder):
            def encode(self, sentences, **kwargs):
                if sentences == ["query"]:
                    return np.asarray([[1.0, 0.0, 0.0]])
                return super().encode(sentences, **kwargs)

        retriever = DilemmaRetriever(self.rows, WrongQueryDimensionEncoder())
        with self.assertRaisesRegex(ValueError, "different dimensions"):
            retriever.search("query")


class HuggingFaceAuthenticationTests(unittest.TestCase):
    def test_explicit_token_takes_precedence_over_environment(self):
        with patch.dict(os.environ, {"HF_TOKEN": "hf_environment"}):
            self.assertEqual(_resolve_hf_token("hf_explicit"), "hf_explicit")

    def test_token_is_read_from_environment(self):
        with patch.dict(os.environ, {"HF_TOKEN": "hf_environment"}, clear=True):
            self.assertEqual(_resolve_hf_token(None), "hf_environment")

    def test_token_is_passed_to_dataset_and_embedding_model(self):
        rows = [{"DILEMMA": "animal", "RUBRIC": "[]"}]
        encoder = Mock()
        sentinel_retriever = object()

        with (
            patch("morebench_retrieve.load_morebench", return_value=rows) as load,
            patch(
                "sentence_transformers.SentenceTransformer", return_value=encoder
            ) as sentence_transformer,
            patch(
                "morebench_retrieve.DilemmaRetriever",
                return_value=sentinel_retriever,
            ),
        ):
            result = build_morebench_retriever(
                token="hf_test", cache_dir=None
            )

        self.assertIs(result, sentinel_retriever)
        load.assert_called_once_with(token="hf_test", split="train")
        sentence_transformer.assert_called_once_with(DEFAULT_MODEL, token="hf_test")


if __name__ == "__main__":
    unittest.main()
