# Restructured Thesis Working Draft

This directory contains the editable thesis produced from the reviewed PDF and the final project implementation. The original PDF remains unchanged.

## Current writing status

| Part | Status | Notes |
| --- | --- | --- |
| Chapter 1 - Introduction | First structural draft | Requires citation resolution and supervisor review |
| Chapter 2 - Objectives | First structural draft | Aim, objectives, and research questions must be confirmed together |
| Chapter 3 - Literature Review | First evidence-based draft | Search record, comparison matrix, design traceability, and working references created; final academic review remains |
| Chapter 4 - Methodology | First implementation-grounded draft | Final evaluation procedure, frozen versions, figures, and past-tense revision remain |
| Chapter 5 - Results | Blocked pending final evidence | Do not copy the existing illustrative values |
| Chapter 6 - Discussion and Conclusions | Blocked pending Chapter 5 | Must answer the research questions using final results |
| Abstract | Deferred | Write after Chapters 5 and 6 |
| Appendix A - Evaluation scenarios | First evidence draft | Contains all 32 author labels and justifications; independent expert validation remains optional but desirable |

## Drafting conventions

- `[CITATION: topic]` marks a claim that needs a verified academic or authoritative source. These tokens must be replaced with the final IEEE citation numbers.
- `[CONFIRM: item]` marks a decision requiring confirmation against the approved proposal, faculty template, or supervisor direction.
- Do not insert final result values until they have been regenerated from the frozen implementation commit.
- Use **AutoOps AI** for the artefact and **the framework** for the research contribution.
- Use **context-aware**, **risk-adaptive**, and **post-action verification** consistently.
- The novelty is the integrated remediation workflow, not any individual use of RAG, agents, approval, risk scoring, or rollback.

## Source-of-truth documents

- `../THESIS_RESTRUCTURING_PLAN.md` - chapter design and research-positioning plan
- `../THESIS_COMPLETION_CHECKLIST.md` - completion gates
- `../THESIS_CORRECTIONS.md` - detailed factual corrections to the old PDF
- `../novelty.md` - original implementation brief; not evidence that every requested feature was implemented exactly as described
- `literature_search_record.md` - search scope, inclusion/exclusion rules, and limitations
- `references_working.md` - provisional IEEE reference register used by the chapter drafts
- `../backend/evaluation/results/test-suite-20260926.xml` - retained interim full-suite evidence; regenerate after the final implementation commit is frozen
- `../backend/evaluation/results/test-suite-interim-20260926.md` - latest interim full-suite result: 501/501 tests passed after strengthening startup rollback verification and diagnostic privacy; regenerate after the final implementation commit is frozen
- `../backend/evaluation/results/end-to-end-safety-20260926.md` - controlled end-to-end and prompt/tool-safety cases, outcomes, evidence scope, and interpretation boundary
- `appendix_a_evaluation_scenarios.md` - inspectable register of all 32 comparative scenarios and author-label justifications
- `../backend/evaluation/retrieval_queries.json` - versioned 30-query retrieval label set, covering every fixed knowledge article
- `../backend/evaluation/run_retrieval_evaluation.py` - live Hit@1, Hit@3, MRR, timing, and structured-error runner; it requires explicit confirmation before sending query and article text to the configured embedding API
- `../backend/evaluation/results/retrieval-analysis-20260926.md` - interim live retrieval result and interpretation limits; this pilot must be rerun after the implementation commit is frozen

## Next writing sequence

The final six-chapter main text must remain within **10,000-13,000 words**. Chapters 1-4 currently contain approximately **9,324 words**. Chapters 5 and 6 should add approximately **2,200-2,700 words** before the final removal of repetition, with the complete thesis targeting roughly **11,500-12,000 words** after editing.

1. Review and approve the Chapter 1 problem, gap, questions, significance, and scope.
2. Confirm that the Chapter 2 objectives match the approved proposal.
3. Build the literature-search record and comparison matrix before drafting Chapter 3.
4. Draft Chapter 4 from the final code, clearly separating actual implementation from conceptual design.
5. Complete the mandatory implementation and evaluation items before writing Chapters 5 and 6.
