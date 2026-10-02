# Project P1: Retrieval-Augmented Moral Reasoning for MoReBench

## Proposal summary

This project investigates whether retrieval-augmented generation (RAG) can improve a language model's performance on MoReBench. For each new moral dilemma, the system retrieves the `k` most semantically similar dilemmas from a reference set, together with their rubric criteria. These examples are added to the model's prompt as structured context before it produces an answer to the new dilemma.

The central hypothesis is that relevant precedents and their evaluation criteria will help the model identify more morally important considerations, reason more systematically, and produce responses that better satisfy the MoReBench rubric. This approach provides task-specific guidance at inference time without fine-tuning the language model.

## Motivation

MoReBench evaluates the quality of moral reasoning rather than whether a model selects one predetermined moral answer. A response is assessed using multiple criteria that cover dimensions such as identifying relevant moral factors, following a logical and clear process, and reaching helpful and harmless outcomes.

A model answering a dilemma without additional context must infer both the morally relevant issues and the expected depth of analysis. Similar dilemmas in MoReBench already contain useful information about these expectations through their rubrics. Retrieving them can therefore serve two purposes:

1. **Provide analogous cases.** Similar dilemmas can help the model recognize stakeholders, obligations, risks, value conflicts, and possible actions that might otherwise be overlooked.
2. **Expose relevant evaluation criteria.** Rubrics from comparable cases provide a structured description of what high-quality reasoning should address.

This idea is inspired by Boraske and Burns' case-based RAG approach for moral judgments. Their system retrieved related interpersonal conflicts and used them as context to improve alignment with human judgments. Project P1 transfers the general idea to MoReBench, but changes the retrieved evidence from judgment labels and comments to dilemmas and their multidimensional rubric criteria.

## Research question

> Does adding the dilemmas and rubric criteria from the `k` most similar MoReBench cases improve model responses compared with the standard MoReBench prompt?

Secondary questions include:

- Which value of `k` gives the best balance between useful coverage and irrelevant context?
- Which MoReBench scoring dimensions benefit most from retrieval?
- Does RAG help smaller or less capable models more than stronger reasoning models?
- How sensitive are the results to the embedding model and similarity threshold?
- How well does generic semantic similarity correspond to moral-structural similarity and rubric transferability?
- Can irrelevant retrieval distract the model or cause it to copy case-specific criteria?

## Proposed method

### 1. Build the reference index

Each reference item consists of:

- the text in `DILEMMA`;
- the associated criteria in `RUBRIC`; and
- a stable identifier for analysis and deduplication.

The dilemma text is converted into a dense vector with a sentence-embedding model. The current prototype uses `BAAI/bge-small-en-v1.5`. Each vector is L2-normalized and stored in a reusable local index. Rubrics are retained as metadata and are not included in the retrieval embedding. Consequently, the initial retriever measures generic semantic similarity between dilemma texts as an inexpensive approximation of similarity between moral situations; it should not be assumed to capture moral similarity directly.

A single vector can encode broad topic, setting, and vocabulary, but it compresses several potentially independent features: stakeholders and their relationships, available actions, intentions, competing values, possible harms, uncertainty, consent, power, fairness, responsibility, and situational constraints. This creates two important failure modes. Dilemmas from the same domain may be textually similar while presenting different moral conflicts, whereas cases from different domains may instantiate the same underlying conflict despite sharing little vocabulary. Small details such as consent, coercion, urgency, or negation may also change the moral analysis without greatly changing the embedding. Whole-text pooling can further dilute a short but decisive clause in a long dilemma.

The reference index must contain only examples that are permitted as retrieval context. Evaluation dilemmas must be excluded from the index, including exact duplicates and close variants, to prevent benchmark leakage.

### 2. Retrieve similar dilemmas

For a new dilemma, the same embedding model produces a query vector. Its similarity to every indexed dilemma is calculated using cosine similarity:

$$
\operatorname{cosine}(q, d_i) = \frac{q \cdot d_i}{\lVert q \rVert\lVert d_i \rVert}.
$$

Because the vectors are normalized, the implementation can compute cosine similarity efficiently as a dot product. The dilemmas are ranked by score, and the top `k` results are returned with their rubric criteria. The initial experiment should test `k \in \{1, 3, 5, 10\}` rather than assuming one value is optimal.

The repository implementation in `morebench_retrieve.py` already supports this stage through `DilemmaRetriever.search(dilemma, k)` and returns the rank, dataset index, cosine score, dilemma, and parsed rubric.

The whole-dilemma, single-vector method should be treated as the primary retrieval baseline. If resources permit, a moral-structure retrieval ablation should retrieve a larger candidate pool, such as the top 20 cases, and rerank it before selecting the final `k`. A structured representation could identify:

- stakeholders and relationships;
- the decision or action under consideration;
- competing values, duties, or rights;
- potential harms and benefits;
- intentions, uncertainty, and relevant obligations; and
- constraints such as consent, coercion, urgency, and power differences.

These facets could be embedded separately and combined with explicit weights, or supplied to a cross-encoder or language-model reranker that estimates whether two cases share an underlying moral conflict. The original dilemma should remain available during reranking so that an imperfect abstraction does not discard decisive facts. A hybrid lexical score may also help preserve concrete entities and details that dense embeddings miss.

### 3. Construct the augmented prompt

The generation prompt should contain:

1. the existing MoReBench reasoning instructions;
2. a clearly delimited section containing each retrieved dilemma and its rubric criteria;
3. an instruction to use the retrieved material only as guidance about relevant considerations;
4. the new target dilemma; and
5. an instruction to answer the target independently rather than deciding or evaluating the retrieved cases.

Only dilemmas and rubric criteria should be retrieved in the first experiment. Model responses, judge scores, and hidden evaluation outputs should not be supplied. This isolates the value of analogous cases and rubric guidance while reducing answer leakage.

An abbreviated prompt structure is:

```text
Use the following related cases as reasoning guidance. Their criteria may reveal
relevant considerations, but not every criterion applies to the target case.

Related case 1:
<retrieved dilemma>

Relevant rubric criteria:
<retrieved criteria>

Target dilemma:
<new dilemma>

Respond to the target dilemma using the standard MoReBench instructions.
```

### 4. Generate and evaluate responses

The same model and decoding settings should be used for the baseline and RAG conditions. Responses can then be evaluated with the existing MoReBench judge and score-calculation pipeline.

The primary comparison is:

| Condition | Context supplied to the model |
|---|---|
| Baseline | Standard prompt and target dilemma |
| RAG | Standard prompt, retrieved dilemmas and rubrics, and target dilemma |
| Random-control | Standard prompt, randomly selected dilemmas and rubrics, and target dilemma |

The random-retrieval control is important because it distinguishes gains caused by semantically relevant cases from gains caused merely by a longer prompt or additional rubric text.

Recommended evaluation measures are:

- overall MoReBench score;
- score for each rubric dimension;
- proportion of applicable positive criteria satisfied;
- frequency of negative or harmful criteria triggered;
- input and output token usage;
- generation latency and estimated cost; and
- mean improvement with confidence intervals across dilemmas.

Downstream response quality alone cannot establish that retrieval captured moral similarity: an improvement might instead result from additional rubric language or prompt length. Retrieval should therefore also be evaluated intrinsically on a manually annotated, representative sample. Pair or query-candidate annotations should distinguish at least:

- topical or surface similarity;
- similarity of the underlying moral conflict; and
- whether the retrieved rubric is transferable to the target dilemma.

The whole-text embedding baseline can then be compared with moral-summary embeddings, facet-level multi-vector retrieval, hybrid retrieval, and reranking using measures such as precision at `k`, recall at `k`, or nDCG. Manual error analysis should specifically examine topically similar but morally different cases, cross-domain moral analogies, and cases in which one decisive detail changes applicability.

If resources permit, results should be reported across multiple models and random seeds. Statistical analysis should use paired comparisons because baseline and RAG responses are generated for the same dilemmas.

## Expected result

The expected result is a measurable increase in the overall MoReBench score relative to direct prompting. The largest improvements are expected in **identifying moral factors**, **logical process**, and **clear process**, because the retrieved rubrics explicitly surface considerations and reasoning structures from related cases. Smaller improvements may occur for **helpful outcome** and **harmless outcome**, especially when retrieval highlights stakeholders or risks absent from the model's initial framing.

RAG is also expected to reduce omissions and response variance by grounding the model in concrete precedents. The benefit may be larger for models that have weaker unaided moral reasoning, while already strong reasoning models may show smaller gains. These are hypotheses rather than guaranteed effects: low-similarity cases, excessive values of `k`, or over-reliance on retrieved criteria could reduce performance.

The attached study provides encouraging precedent. Its moral-judgment RAG system retrieved five similar cases and improved GPT-4o accuracy by six percentage points over direct prompting, while also improving Matthews correlation and reducing toxic output. Those results are not directly transferable to MoReBench because the task, corpus, retrieved evidence, and evaluation measures differ. Project P1 should therefore establish its own controlled baseline and ablations.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Evaluation leakage | Use a reference/evaluation split and remove duplicates or near-duplicates before indexing. |
| Irrelevant cases distract the model | Tune `k`, inspect similarity distributions, and test a minimum similarity threshold. |
| Generic semantic similarity does not reflect moral structure | Treat single-vector retrieval as a baseline; evaluate moral-structure representations and reranking, and measure retrieval relevance directly. |
| Model copies non-applicable criteria | Explicitly instruct it to assess applicability and solve the target independently. |
| Longer prompts alone affect scores | Include a random-retrieval control with a comparable context length. |
| Rubrics expose benchmark-specific wording | Report this as an inference-time, rubric-aware condition rather than a standard closed-book score. |
| Retrieval adds cost and latency | Cache reference embeddings and record tokens, runtime, and monetary cost. |
| Judge bias favors rubric terminology | Add blinded human review on a representative subset where feasible. |

## Success criteria

Project P1 will be considered successful if:

- the RAG condition improves the mean MoReBench score over both the baseline and random-retrieval control;
- the improvement is consistent across a substantial portion of dilemmas rather than driven by a few outliers;
- retrieved cases are demonstrably relevant on manual inspection;
- gains remain after accounting for prompt length, token cost, and judge sensitivity; and
- the experiment is reproducible from a fixed index, model configuration, prompt template, and random seed.

Even if the aggregate score does not improve, the project will still provide useful findings if it identifies which dilemma types, rubric dimensions, similarity ranges, or model families benefit from retrieval and which are harmed by it.

## Planned deliverables

1. A leakage-safe MoReBench reference index with cached embeddings.
2. Integration of retrieval into the inference pipeline behind an optional RAG flag.
3. A prompt template for retrieved dilemmas and rubrics.
4. Baseline, RAG, random-retrieval, and `k`-value experiments.
5. If resources permit, a moral-structure retrieval or reranking ablation.
6. An intrinsic retrieval evaluation on annotated examples, distinguishing topical similarity, moral-structural similarity, and rubric transferability.
7. A results table covering quality, rubric dimensions, retrieval relevance, tokens, latency, and cost.
8. An error analysis of successful, irrelevant, and misleading retrievals.

## References

Boraske, M., & Burns, R. (2025). *Context is Key: Aligning Large Language Models with Human Moral Judgments through Retrieval-Augmented Generation*. Proceedings of the 38th International Florida Artificial Intelligence Research Society Conference. [Attached article](Resources/FLAIRS_38_103.pdf). https://doi.org/10.32473/flairs.38.1.138947

Chiu, Y. Y., Lee, M. S., Calcott, R., Handoko, B., de Font-Reaulx, P., Millière, R., Rodriguez, P., Zhang, C. B. C., Han, Z., Sehwag, U. M., Maurya, Y., Knight, C. Q., Lloyd, H. R., Bacus, F., Downey, C., Mazeika, M., Liu, B., Choi, Y., Gordon, M. L., & Levine, S. (2026). *MoReBench: Evaluating Procedural and Pluralistic Moral Reasoning in Language Models, More than Outcomes*. International Conference on Learning Representations (ICLR). [Attached article](Resources/MoreBench_article.pdf). https://doi.org/10.48550/arXiv.2510.16380
