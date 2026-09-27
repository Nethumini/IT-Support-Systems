# Restructured Thesis Working Draft

This directory contains the editable thesis produced from the reviewed PDF and the final project implementation. The original PDF remains unchanged.

## Current writing status

| Part | Status | Notes |
| --- | --- | --- |
| Chapter 1 - Introduction | Content-complete draft | Problem, gap, questions, significance, scope, solution overview, and figure completed |
| Chapter 2 - Objectives | Content-complete draft | General objective, four measurable objectives, and objective-to-evidence mapping completed |
| Chapter 3 - Literature Review | Content-complete draft | Search approach, comparison, design traceability, gap synthesis, and citations completed |
| Chapter 4 - Methodology | Content-complete draft | Past-tense procedure, frozen configuration, input hashes, endpoint method, and three methodology figures completed |
| Chapter 5 - Results | Content-complete draft | Frozen offline, live-retrieval, comparative, and real-Windows results completed |
| Chapter 6 - Discussion and Conclusions | Content-complete draft | RQ1-RQ4, literature comparison, contribution, limitations, conclusions, and future work completed |
| Abstract | Content-complete draft | Problem, method, principal results, contribution boundary, limitations, and keywords completed |
| Appendix A - Evaluation scenarios | First evidence draft | Contains all 32 author labels and justifications; independent expert validation remains optional but desirable |
| Appendix B - Evidence register | Content-complete draft | Identifies the final evidence packages, frozen inputs, hashes, and privacy/integrity boundaries |
| Abbreviations | Content-complete draft | Defines the technical abbreviations used in the thesis |

## Drafting conventions

- Use only result values regenerated from frozen commit `cc655c3` and verified against the retained evidence manifests.
- Use **AutoOps AI** for the artefact and **the framework** for the research contribution.
- Use **context-aware**, **risk-adaptive**, and **post-action verification** consistently.
- The novelty is the integrated remediation workflow, not any individual use of RAG, agents, approval, risk scoring, or rollback.

## Source-of-truth documents

- `../THESIS_RESTRUCTURING_PLAN.md` - chapter design and research-positioning plan
- `../THESIS_COMPLETION_CHECKLIST.md` - completion gates
- `../THESIS_CORRECTIONS.md` - detailed factual corrections to the old PDF
- `../novelty.md` - original implementation brief; not evidence that every requested feature was implemented exactly as described
- `literature_search_record.md` - search scope, inclusion/exclusion rules, and limitations
- `references.md` - consolidated IEEE reference list used by the chapter drafts
- `abstract.md` - completed abstract and keywords
- `abbreviations.md` - abbreviation list for the front matter
- `lists_of_figures_and_tables.md` - verified caption register for regenerating the two Word lists
- `appendix_b_evidence_register.md` - reproducibility and evidence index for the final evaluation
- `../backend/evaluation/results/test-suite-20260926.xml` - retained interim full-suite evidence; regenerate after the final implementation commit is frozen
- `../backend/evaluation/results/test-suite-interim-20260926.md` - latest interim full-suite result: 501/501 tests passed after strengthening startup rollback verification and diagnostic privacy; regenerate after the final implementation commit is frozen
- `../backend/evaluation/results/end-to-end-safety-20260926.md` - controlled end-to-end and prompt/tool-safety cases, outcomes, evidence scope, and interpretation boundary
- `appendix_a_evaluation_scenarios.md` - inspectable register of all 32 comparative scenarios and author-label justifications
- `../backend/evaluation/retrieval_queries.json` - versioned 30-query retrieval label set, covering every fixed knowledge article
- `../backend/evaluation/run_retrieval_evaluation.py` - live Hit@1, Hit@3, MRR, timing, and structured-error runner; it requires explicit confirmation before sending query and article text to the configured embedding API
- `../backend/evaluation/results/retrieval-analysis-20260926.md` - interim live retrieval result and interpretation limits; this pilot must be rerun after the implementation commit is frozen
- `chapter_05_results.md` - factual results from the final frozen-commit offline, retrieval, and Windows evidence packages
- `autoops-final-evidence-cc655c3-20260927` - external integrity-checked final automated-test and comparative evidence package
- `autoops-final-retrieval-cc655c3-20260927` - external integrity-checked final live-retrieval evidence package
- `autoops-final-windows-cc655c3-20260927` - external integrity-checked final real-Windows evidence package

## Next writing sequence

The final six-chapter main text must remain within **10,000-13,000 words**. Chapters 1-6 currently contain approximately **12,286 words**, excluding the references, search record, planning documents, and appendices. Including the 338-word abstract gives **12,624 words**, which also remains within the stated range if the faculty counts the abstract. Final revisions must preserve this range and remove repetition before adding any substantial main-text material.

1. Review and approve the Chapter 1 problem, gap, questions, significance, and scope.
2. Confirm that the Chapter 2 objectives match the approved proposal.
3. Obtain supervisor approval for the research wording and contribution boundary.
4. Transfer the completed Markdown content into the Word document.
5. Complete the remaining front matter, faculty formatting, lists of figures and tables, and final PDF review.
