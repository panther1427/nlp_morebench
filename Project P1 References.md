# Project P1: Additional References

This note collects potential references for the MoReBench retrieval-augmented generation project. The references are grouped by their role in the project, with a short explanation of why each may be useful.

## RAG and semantic retrieval

### Lewis et al. (2020): Retrieval-Augmented Generation

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. Advances in Neural Information Processing Systems, 33, 9459–9474.

- **Relevance:** The foundational RAG paper. It defines the combination of a language model's parametric knowledge with an external, retrievable memory.
- **Project connection:** Provides the general methodological basis for retrieving MoReBench cases before generating a response.
- **Links:** [arXiv](https://arxiv.org/abs/2005.11401) · [NeurIPS proceedings](https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html)

### Reimers and Gurevych (2019): Sentence-BERT

Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing, 3982–3992.

- **Relevance:** Introduces semantically meaningful sentence embeddings that can be compared efficiently using cosine similarity.
- **Project connection:** Supports the decision to embed complete dilemma descriptions and rank related cases by cosine similarity.
- **Links:** [ACL Anthology](https://aclanthology.org/D19-1410/) · [DOI](https://doi.org/10.18653/v1/D19-1410)

### Thakur et al. (2021): BEIR

Thakur, N., Reimers, N., Rücklé, A., Srivastava, A., & Gurevych, I. (2021). *BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models*. Advances in Neural Information Processing Systems, 34.

- **Relevance:** Compares lexical, sparse, dense, late-interaction, and reranking retrieval systems across diverse domains.
- **Project connection:** Motivates evaluating the chosen embedding retriever against a lexical baseline such as BM25 instead of assuming dense retrieval is optimal for moral dilemmas.
- **Links:** [arXiv](https://arxiv.org/abs/2104.08663) · [OpenReview](https://openreview.net/forum?id=wCu6T5xFjeJ)

## Case-based reasoning

### Sourati et al. (2023): Case-Based Reasoning with Language Models

Sourati, Z., Ilievski, F., Sandlin, H.-Â., & Mermoud, A. (2023). *Case-Based Reasoning with Language Models for Classification of Logical Fallacies*. Proceedings of the Thirty-Second International Joint Conference on Artificial Intelligence, 5188–5196.

- **Relevance:** Combines retrieval of similar historical cases with language-model reasoning on a task that requires analysis rather than simple factual recall.
- **Project connection:** Project P1 can be framed as case-based moral reasoning. The paper also motivates studying case representation, retrieval quality, and whether fewer high-quality cases outperform a larger context.
- **Links:** [IJCAI proceedings](https://www.ijcai.org/proceedings/2023/0576.pdf) · [arXiv](https://arxiv.org/abs/2301.11879)

## RAG evaluation and robustness

### Chen et al. (2024): Benchmarking RAG

Chen, J., Lin, H., Han, X., & Sun, L. (2024). *Benchmarking Large Language Models in Retrieval-Augmented Generation*. Proceedings of the AAAI Conference on Artificial Intelligence, 38(16), 17754–17762.

- **Relevance:** Evaluates noise robustness, negative rejection, information integration, and counterfactual robustness in RAG systems.
- **Project connection:** Supports testing irrelevant and misleading retrievals, including the proposed random-retrieval control and a minimum similarity threshold.
- **Links:** [AAAI](https://doi.org/10.1609/aaai.v38i16.29728) · [arXiv](https://arxiv.org/abs/2309.01431)

### Liu et al. (2024): Lost in the Middle

Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. Transactions of the Association for Computational Linguistics, 12, 157–173.

- **Relevance:** Shows that language models do not use every part of a long context equally and may struggle when relevant information is positioned in the middle.
- **Project connection:** Justifies tuning `k`, limiting unnecessary context, and testing the ordering of retrieved dilemmas and rubric criteria.
- **Links:** [TACL](https://doi.org/10.1162/tacl_a_00638) · [arXiv](https://arxiv.org/abs/2307.03172)

### Es et al. (2024): RAGAs

Es, S., James, J., Espinosa Anke, L., & Schockaert, S. (2024). *RAGAs: Automated Evaluation of Retrieval Augmented Generation*. Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations, 150–158.

- **Relevance:** Separates RAG evaluation into dimensions such as context relevance, answer faithfulness, and answer relevance.
- **Project connection:** Offers a framework for diagnosing whether a failure originated in retrieval or generation. These measures could supplement, but should not replace, MoReBench's domain-specific rubric scores.
- **Links:** [ACL Anthology](https://aclanthology.org/2024.eacl-demo.16/) · [DOI](https://doi.org/10.18653/v1/2024.eacl-demo.16)

## Moral reasoning and ethical NLP

### Hendrycks et al. (2021): ETHICS

Hendrycks, D., Burns, C., Basart, S., Critch, A., Li, J., Song, D., & Steinhardt, J. (2021). *Aligning AI With Shared Human Values*. International Conference on Learning Representations.

- **Relevance:** Introduces the ETHICS benchmark, covering justice, well-being, duties, virtues, and commonsense morality.
- **Project connection:** Provides background for assessing morality across multiple dimensions rather than treating moral reasoning as a single binary prediction.
- **Links:** [OpenReview](https://openreview.net/forum?id=dNy_RKzJacY) · [arXiv](https://arxiv.org/abs/2008.02275)

### Lourie, Le Bras, and Choi (2021): SCRUPLES

Lourie, N., Le Bras, R., & Choi, Y. (2021). *SCRUPLES: A Corpus of Community Ethical Judgments on 32,000 Real-Life Anecdotes*. Proceedings of the AAAI Conference on Artificial Intelligence, 35(15), 13470–13479.

- **Relevance:** Presents real-life moral situations with distributions of community judgments and emphasizes that moral cases are often inherently divisive.
- **Project connection:** Supports retrieving multiple analogous cases while avoiding the assumption that one retrieved precedent represents a uniquely correct moral conclusion.
- **Links:** [AAAI](https://doi.org/10.1609/aaai.v35i15.17589) · [Dataset and code](https://github.com/allenai/scruples)

### Talat et al. (2022): Ethical Judgments from Natural Language

Talat, Z., Blix, H., Valvoda, J., Ganesh, M. I., Cotterell, R., & Williams, A. (2022). *On the Machine Learning of Ethical Judgments from Natural Language*. Proceedings of the 2022 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, 769–779.

- **Relevance:** Critically examines computational moral-judgment systems, including decontextualization and the distinction between descriptive and normative ethical claims.
- **Project connection:** Helps frame the limitations of treating retrieved rubrics as moral authority. The retrieved material should guide analysis without being presented as a definitive moral answer.
- **Links:** [ACL Anthology](https://aclanthology.org/2022.naacl-main.56/) · [DOI](https://doi.org/10.18653/v1/2022.naacl-main.56)

## Suggested reading order

1. Lewis et al. for the RAG foundation.
2. Boraske and Burns from the main proposal for moral case-based RAG.
3. Sourati et al. for case-based reasoning methodology.
4. Reimers and Gurevych for cosine-similarity retrieval.
5. Chen et al. and Liu et al. for retrieval risks and experimental design.
6. The MoReBench paper, Hendrycks et al., and Lourie et al. for benchmark context.
7. Talat et al. for conceptual and ethical limitations.
8. Thakur et al. and Es et al. when designing retrieval-specific evaluation.

## How these references map to Project P1

| Project component | Most relevant references |
|---|---|
| General RAG architecture | Lewis et al. (2020) |
| Embeddings and cosine similarity | Reimers & Gurevych (2019) |
| Case-based reasoning | Sourati et al. (2023); Boraske & Burns (2025) |
| Choosing and ordering `k` cases | Liu et al. (2024); Sourati et al. (2023) |
| Noise and irrelevant retrieval controls | Chen et al. (2024) |
| Comparing retrieval approaches | Thakur et al. (2021) |
| Retrieval-specific evaluation | Es et al. (2024) |
| Multidimensional moral evaluation | Hendrycks et al. (2021); MoReBench (2026) |
| Moral ambiguity and disagreement | Lourie et al. (2021) |
| Conceptual and ethical limitations | Talat et al. (2022) |
