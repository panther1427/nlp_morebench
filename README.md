# Can Retrieval Help Models Identify Moral Considerations?
## A Controlled Study Using MoReBench
## Abstract

MoReBench evaluates moral reasoning by checking model responses against expert-written rubric criteria. This project tests whether retrieving information from other moral dilemmas helps a LLM identify relevant considerations in a new dilemma. We will use the 500 public MoReBench cases and divide them into retrieval and test sets. Using SBERT embeddings, we will retrieve the three most similar, three least similar, and a mix of dilemmas from the retrieval set. We will compare direct answers with answers supported by random examples and dilemma texts from similar, dissimilar, or mixed examples. The model will never receive the expert criteria belonging to the dilemma it is answering, to prevent data leakage . We will evaluate responses using the benchmarks existing judging and scoring pipeline, where we will compare the MoReBench-Regular and MoReBench-Hard benchmark. Our goal is to test whether useful moral considerations transfer between dilemmas, and whether similarity and/or dissimilarity makes retrieved information helpful in practice.

## Contributions

- Test whether retrieval from other dilemmas improves MoReBench scores, including MoReBench-Hard.
- Compare the three most similar, three least similar and a  mix of these dilemmas to study whether similarity, diversity or mix provides more useful guidance.
- Provide the data splits, prompts, retrieval code, and evaluation steps so others can repeat the study.

Our contribution is a controlled comparison of retrieval methods for moral reasoning using MoReBench.

## Proposed additional datasets

We plan to use only MoReBench. The [paper](https://arxiv.org/abs/2510.16380) describes 1,000 scenarios overall, with 500 public scenarios and 500 reserved for private evaluation. We will use the public set from the [Hugging Face dataset page](https://huggingface.co/datasets/morebench/morebench).

The public dataset is available as CSV. Its fields include `DILEMMA`, `DILEMMA_SOURCE`, `DILEMMA_TYPE`, `THEORY`, `ROLE_DOMAIN`, `CONTEXT`, and `RUBRIC`. Each rubric contains criterion titles, weights, and dimension labels. The five dimensions are Identifying, Logical Process, Clear Process, Helpful Outcome, and Harmless Outcome. For example, a search-and-rescue dilemma could include a criterion about recognizing the importance of saving lives regardless of the rescue method.

We will target a 400/100 split for retrieval and testing, using a fixed seed. The retrieval set provides dilemma texts and their expert criteria as additional context. We will not train the response model, only run inference. Depending on the condition, the model will receive retrieved dilemmas and their criteria, alongside the test dilemma text. The test dilemma’s criteria will remain separate for evaluation.

## Methods

1. **Load and prepare cases.** Load the public dataset, parse the expert criterion, and check for duplicates before splitting. Keep development and test expert criterion separate from the retrieval index and response-generation code.

2. **Build the retrieval system.** Use a pretrained SBERT model to embed dilemma texts and rank retrieval-set cases by cosine similarity. Select the three highest-scoring, three lowest-scoring cases or a mix. “Least similar” means lowest embedding similarity, which may differ from moral similarity. We will manually inspect a few development examples to check what the rankings capture.

3. **Compare answer conditions.** Generate one final response per dilemma under five conditions:
   - **Direct:** the dilemma without retrieved information, serves as baseline.
   - **Random dilemma RAG:** criteria from three randomly selected retrieval-set dilemmas. Will serve as control.
   - **Similar dilemma RAG:** texts of the three most similar dilemmas.
   - **Least-similar dilemma RAG:** texts from the three least similar dilemmas.
   - **Mixed dilemma RAG:** texts from the three most similar and three least similar dilemmas.

We will select retrieved examples using only dilemma-text embeddings. After selection, we will include their dilemma descriptions and expert criteria in the prompt. The test dilemmas expert criteria will never be used for retrieval or response generation. After generation, the judge will evaluate every answer using the test dilemma’s complete original criteria and weights.

4. **Tune and judge.** Use retrieval cases to choose the embedding model, criteria limit, and prompts. Choose a LLM judge based on access, cost, and a small pilot. We aim to use Deepseek 4.1 Flash. Adapt the [existing evaluation code](https://github.com/morebench/morebench) to our splits and answer conditions. Freeze settings before testing. Score each response against its own dilemma’s rubric.

5. **Analyze.** Report MoReBench-Regular and MoReBench-Hard as defined in the paper, answer lengths, and results across all five rubric dimensions/subjects. Compare conditions on the same test dilemmas using paired score differences and bootstrap confidence intervals. Focus on whether relevant retrieval improves  scores over direct and random conditions, and whether dissimilar examples help or distract.

With 100 test cases and 5 answer conditions, the main experiment produces 500 responses. At roughly 23 criteria per case, this means about 11500 criterion judgments per judge, excluding development runs. We will confirm the exact count and estimate costs during the pilot.

## Proposed timeline

- **Week 1:** Load the dataset, inspect examples, check related cases, and create the splits.
- **Week 2:** Build retrieval and prompts; run a small development pilot to check quality, runtime, and cost.
- **Week 3:** Finalize settings and run generation and judging.
- **Week 4:** Analyze results, review examples, and prepare the P2 submission.

This tentative schedule will be adjusted to the course’s P2 deadline.

## Organization within the team

We will divide responsibilities across data preparation, retrieval, generation and evaluation, and analysis. Names will be assigned within the team, and each part will be reviewed by another member.

Tentative internal milestones before P2:

- **M1:** Data splits and duplicate checks completed.
- **M2:** All six conditions working on development cases.
- **M3:** Pilot reviewed; prompts, settings, and budget finalized.
- **M4:** Test responses and judgments completed.
- **M5:** Results checked and P2 material prepared together.

# Appendix

## Repo organisation

Our repository is [nlp_morebench](https://github.com/panther1427/nlp_morebench).

Planned structure:

- `README.md`: project proposal and setup instructions.
- `data/`: dataset preparation notes and split IDs.
- `src/`: preparation, embedding, retrieval, generation, judging, and analysis code.
- `prompts/`: prompts for all answer conditions.
- `configs/`: model settings, seeds, and experiment settings.
- `outputs/`: retrieved examples, responses, judgments, and scores.
- `results/`: tables, figures, and selected examples.
- `requirements.txt`: project dependencies.

API keys will be kept outside the repository.

## Questions for TAs

We have no questions at the moment.

## References

- [MoReBench paper](https://arxiv.org/abs/2510.16380)
- [MoReBench dataset](https://huggingface.co/datasets/morebench/morebench)
- [MoReBench code and README](https://github.com/morebench/morebench)
- [Sentence Transformers similarity documentation](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)

