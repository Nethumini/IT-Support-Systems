# Interim Retrieval Evaluation Analysis

## Status and configuration

This is an **interim pilot result**, not the final frozen-commit thesis result. It was generated on 26 September 2026 from a working tree containing uncommitted changes. The summary records Git HEAD `1bb37a5`, but that identifier alone does not contain the new label set and evaluation harness. The final thesis run must therefore be repeated after the implementation and evaluation materials are frozen in version control.

- Embedding model: `models/gemini-embedding-001`
- Production method: `DatasetAnalyzer.find_similar_issues`
- Knowledge base: 30 fixed articles
- Label set: version 1.0, 30 author-labelled paraphrased queries
- Similarity inclusion rule: strictly greater than 0.70
- Category-match bonus: 0.05
- Maximum returned results: 3
- Raw records: `retrieval-runs-20260926-214743.csv`
- Machine-readable summary: `retrieval-summary-20260926-214743.json`

## Observed results

| Measure | Numerator / denominator | Result |
| --- | ---: | ---: |
| Hit@1 | 30 / 30 | 1.000 |
| Hit@3 | 30 / 30 | 1.000 |
| Mean reciprocal rank | reciprocal-rank sum 30.0 / 30 | 1.000 |
| Queries with no correct rank-1 result | 0 / 30 | 0.000 |

The relevant article was ranked first for every labelled query, so there were no observed misses or lower-rank correct results to classify. Top-result similarity values ranged from 0.799 to 0.890, with a median of 0.854 and mean of 0.850. Fifteen queries returned one result above the threshold, four returned two, and eleven returned three. Among the 15 queries with a second returned result, the top-one minus top-two score margin ranged from 0.041 to 0.163, with a median of 0.124.

The run took 33,833.397 ms inside the retrieval function. The first query took 15,555.781 ms because it also generated and cached embeddings for all 30 documents. The remaining queries averaged 630.263 ms. These values are embedding/retrieval wall times on this run, not end-to-end application latency or a production performance benchmark.

## Error analysis and interpretation boundary

No ranking errors occurred in this set, so there is no observed miss-specific causal analysis to report. This absence must not be interpreted as universal retrieval accuracy. The set is closed-world and deliberately contains one realistic paraphrase for each known article. The same author created the queries and relevance labels from the articles' intended meanings, and no independent expert judged relevance. Each query was also supplied with its expected category, allowing the implemented 0.05 category bonus to contribute to ranking. The experiment therefore measures whether the configured retriever can recover clearly represented known issues under correct category input; it does not measure novel issues, ambiguous requests, incorrect category classification, stale articles, multilingual input, production user language, or knowledge-base growth.

The free Gemini tier also permits provider use of submitted content for product improvement. Only the project's synthetic evaluation text was used in this run; credentials were not included in retained evidence.

## Required final action

After the implementation is frozen, rerun the same versioned set and preserve the dirty-tree indicator as `false`. For a stronger robustness result, create and pre-register a separate challenge set covering ambiguous issue pairs, noisy wording, incorrect or absent category labels, and out-of-knowledge-base queries. Results from such a later set must be reported separately because it would be designed after observing this pilot.
