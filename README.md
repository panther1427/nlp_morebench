# Can MoreBench Be Gamed by Verbosity?
## A Controlled Robustness Study

## Abstract

MoreBench evaluates moral reasoning by checking model responses against expert-written rubric criteria. The paper reports that longer answers can satisfy more criteria due to more text and introduces MoreBench-Hard, a length-corrected score, to fix this. This project tests whether that correction makes the adjusted score less sensitive to extra wording. We will start from a fixed set of model responses to public moral dilemmas, then create concise, expanded, and irrelevant-padding versions while keeping each response's moral position and core reasons stable. We will score versions with the benchmark's standard rubrics, compare raw and length-corrected scores, and compare different judges. Our goal is not to decide whether a model is morally good but its if making an answer longer or shorter change its benchmark score, even when the moral position is the same? We will test how much scores change when answers become longer or shorter whether this happens across different dilemmas, and which parts of the rubric are most affectedy.

## Contributions
- Test whether making answers longer or shorter changes MoreBench scores while keeping the moral position and main reasons the same.
- Measure how irrelevant padding affects raw scores and how MoreBench-Hard’s length correction changes those results.
- Compare results across dilemmas, rubric dimensions, and judges to see where score changes are largest and whether they follow a consistent pattern.
- Provide the prompts, code, and evaluation steps so others can repeat the study.

Our contribution is a controlled study of how answer length affects MoreBench scores, including its existing length correction.

## Proposed additional datasets

We plan on only using the MoReBench dataset. We will use the theory-neutral public MoReBench split. The [paper](https://arxiv.org/abs/2510.16380) describes 1,000 scenarios overall and reserves 500 as the public evaluation set, with the remainder being private. We will use only public scenarios.

The dataset is available through the [Hugging Face dataset page](https://huggingface.co/datasets/morebench/morebench). Its rows include the dilemma text, source and type, theory, role, context, and a RUBRIC field containing expert-written criteria. Criteria include a title, weight, and category. The repository's inference scripts load the CSV through Hugging Face Datasets and write model outputs to JSONL; its README documents separate response-generation, judging, and score-calculation steps ([code and usage](https://github.com/morebench/morebench)). We will use the existing code to load the public dataset and check that it works as intended. We will use all 500 public cases, each with roughly 20–49 criteria for scoring answers. For each case, we intend to create four answer versions, original, concise, expanded, and padded with irrelevant text. As we have on average of 23 criteria per case, each judge will either make a yes or a no descision. It will come out to a total of 46.000 decisions in total.  We will keep the original dataset unchanged and save the answer versions in JSONL, with one record per line. We intend that record will include the case ID, answer version, answer text, character count, and details of the prompt and model used.

## Methods

1. **Load cases and generate answers.** Use the existing code to load all 500 public theory-neutral cases. Generate one final answer per case using the same model and prompt settings. Save these original answers as the starting point for all versions.
2. **Create answer versions.** For each original answer, create a shorter version, a longer version explaining the same reasons in more words, and a padded version with extra text unrelated to the moral dilemma. Keep the moral position and main reasons the same, OBS VI SKAL OGSÅ SIGE VI SKAL BRUGE BERTSCORE. Save the prompts and character counts. 
3. **Judge and score.** We have not yet decided which judge model to use. We will choose one based on access, cost, and results from a small test run. Use the benchmark’s existing evaluation code to score every answer against the same criteria for its case, using the same judge settings. Shuffle the answer order and hide the version labels from the judge, so there is no bias in the results
4. **Analyze.** Calculate MoreBench-Regular and MoreBench-Hard as defined in the paper. Compare each changed answer with its original and measure the change. 
Check which individual criteria receive different judgments. Focus first on whether irrelevant padding changes the raw score, then examine how the length correction affects the result. Use the shorter and longer versions to study the wider relationship between length and score

The study tests how answer length affects benchmark scores
## Proposed timeline

xxxx

## Organization within the team

xxxx


# Appendix

xxxx

## Repo organisation

xxxxx

## Questions for TAs

