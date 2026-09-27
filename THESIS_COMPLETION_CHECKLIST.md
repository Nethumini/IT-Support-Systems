# Thesis Completion Checklist

## How to use this file

This is the living source of truth for determining whether the thesis is complete. Check an item only when the deliverable and its supporting evidence both exist. A paragraph that merely promises future work does not complete an item.

Status reviewed: **27 September 2026**\
Detailed plan: `THESIS_RESTRUCTURING_PLAN.md`\
Detailed factual corrections: `THESIS_CORRECTIONS.md`

## Gate 1 - Research definition

- [ ] Final title approved and used consistently.
- [x] General aim finalized in the thesis content.
- [x] Specific objectives finalized, measurable, and mapped to evidence.
- [x] Research questions finalized and aligned with the objectives and Chapter 6 answers.
- [x] Scope and exclusions explicitly stated.
- [x] Integration-based novelty statement used consistently.
- [x] Research gap supported by a documented structured search, comparison matrix, and bounded synthesis.
- [x] No unsupported "first," "none exists," or universal novelty claim remains in the six-chapter draft.

## Gate 2 - Final project implementation

- [x] Evidence retrieval is implemented.
- [x] Deterministic risk classification is implemented.
- [x] Risk-dependent authorization states are implemented.
- [x] Controlled action catalogue and parameter validation are implemented.
- [x] Preconditions and postconditions are implemented.
- [x] Rollback/escalation flow is implemented.
- [x] Audit records are implemented.
- [x] Approved knowledge-learning boundary is implemented.
- [x] Simulator and endpoint execution drivers are implemented.
- [x] Medium-risk approval endpoint enforces ownership or explicit `troubleshoot:auto_resolve` authorization and has negative authorization tests.
- [x] Final implementation commit is frozen and recorded. Commit `cc655c3411ea96e67740e04b9c36df47cdfba064` (`cc655c3`) is the evaluation baseline.
- [x] Final dependency/version table is verified against the frozen commit. The final offline metadata records the requirements hash, declared dependencies, installed packages, Python 3.12.13, and Pytest 8.3.3.
- [x] Complete automated test suite finishes cleanly and its output is retained. The frozen-commit offline run passed 518/518 tests with zero failures, errors, or skips; JUnit XML, console output, metadata, integrity recalculation, and hashes are retained.

## Gate 3 - Evaluation evidence

- [x] Comparative simulator harness exists.
- [x] Thirty-two unique scenarios exist, including recovery cases.
- [x] Three repeatability runs are supported.
- [x] Scenario labels and justifications are included in an appendix. `thesis_restructured/appendix_a_evaluation_scenarios.md` records all 32 author-labelled cases, their fixed inputs, special controls, expected routes, and label reasons.
- [x] Independent expert review of labels is recorded, or the author-labelled limitation is stated everywhere relevant. No expert review was conducted; the author-labelled specification-conformance limitation is stated in Chapters 3-6.
- [x] Final comparative run is generated from the frozen implementation commit. It contains 32 scenarios, three conditions, three repeats, and 288 records.
- [x] Counts per unique scenario are separated from repeated-run totals.
- [x] Every percentage reports its numerator and denominator.
- [x] Condition B is described as an approval-all/rubber-stamp simulation, not real human behaviour.
- [x] Paired/comparable scenario analysis is used for success-rate comparisons. Nineteen unique scenarios executed under both B and C and produced the same verification and final status.
- [x] Fault-detection denominator is explicitly defined as injected faults that reached execution.
- [x] Retrieval evaluation includes labelled queries, Hit@1, Hit@3, suitable ranking metrics, and error analysis. The frozen-commit live run produced Hit@1 30/30, Hit@3 30/30, MRR 1.000, and no error or no-result case; its raw and derived evidence is retained.
- [x] End-to-end cases exercise retrieval, proposal, risk, approval, execution, verification, and recovery/escalation. Controlled cases E2E-01 and E2E-02 traverse the authenticated HTTP and service path; the external model and retriever are fixed to isolate controller behaviour. Evidence is retained in `backend/evaluation/results/end-to-end-safety-20260926.xml` and its companion Markdown summary.
- [x] Prompt/tool-injection behaviour is tested through the real path. PI-01 to PI-03 cover claimed approval in user text, malicious retrieved instructions, and unknown model-produced action identifiers. The demonstrated property is deterministic effect containment, not universal model immunity.
- [x] Real Windows evidence is retained with device/OS, timestamp, configuration, trace, and result. It records names-only diagnostics, observed failure, fingerprint-verified rollback, cleanup, and audit events on Windows 11 build 26200.
- [x] Latency is measured end to end or clearly labelled as simulator/controller latency only. Simulator and retrieval-function timings are explicitly not described as user-facing end-to-end latency.
- [x] Raw evaluation files and calculation procedure are retained. Separate SHA-256 manifests cover the final offline, live-retrieval, and real-Windows evidence packages.
- [x] Limitations and threats to validity are derived from the actual evaluation in Section 6.4.

## Gate 4 - Six-chapter restructuring

- [x] Chapter 1 contains background, problem, gap, questions, significance, scope, short solution overview, figure, and summary.
- [x] Chapter 2 contains the general and specific objectives and an objective-to-evidence mapping.
- [x] Chapter 3 compares literature and finishes with the synthesised gap and design implications.
- [x] Chapter 4 merges the research-relevant Methodology, SRS, and Implementation/Design material. Its past-tense evaluation procedure, frozen configuration, and figure artwork are complete.
- [x] Chapter 4 defines all risk inputs according to the actual code and records their limitations.
- [x] Chapter 4 contains the completed evaluation procedure without reporting outcomes. It records the final retrieval set, end-to-end and adversarial cases, endpoint procedure, frozen configuration, input hashes, and retained evidence.
- [x] Chapter 5 reports the final artefact and factual results without broad interpretation.
- [x] Chapter 5 reports a result for every specific objective in Table 5.3.
- [x] Chapter 6 interprets findings against the research questions, objectives, and literature.
- [x] Chapter 6 contains contribution, implications, limitations, direct conclusions, and future work.
- [x] Long scenarios and the evidence register are separated into Appendices A and B; raw machine-readable evidence remains in integrity-checked packages rather than the main text.

## Gate 5 - Implementation accuracy

- [x] Retrieval is described as the implemented in-process Gemini-embedding comparison, not ChromaDB/LangChain.
- [x] The model is identified as `gemini-embedding-001` and agrees with the frozen live-retrieval evidence.
- [x] No document-chunking or environment-metadata-filter claim remains unless implemented.
- [x] Diagnosis confidence is identified as an LLM-provided input to a deterministic risk calculation.
- [x] Evidence quality is described as similarity-based unless richer assessment is implemented.
- [x] Impact and affected-resource signals are described according to their catalogue/configuration derivation.
- [x] Low-risk execution is not described as entirely automatic while the interface still requires a Run action.
- [x] Audit logging is not called tamper-proof or tamper-evident unless strengthened and tested.
- [x] Conceptual agents are distinguished from concrete services and endpoint orchestration.
- [x] Approval-token scope and approver identity are described separately and accurately.
- [x] Logical architecture is not misrepresented as physically isolated deployment zones.
- [x] Action, verification-contract, knowledge-article, and test counts are regenerated from the frozen commit.

## Gate 6 - Front matter and presentation

- [ ] Faculty title page is correct.
- [ ] Declaration and approval pages are included if required.
- [x] Abstract reports the problem, method, main results, contribution, and principal limitations.
- [ ] Table of contents is regenerated.
- [ ] List of figures is complete and regenerated.
- [ ] List of tables is complete and regenerated.
- [x] Abbreviation list is included; abbreviations are expanded at first substantive use in the chapters.
- [x] Figure and table captions and numbering are unique and correct in the six chapter drafts.
- [x] Every figure and table in the six chapter drafts is referenced and explained in the text.
- [ ] Tense, terminology, spelling, and academic tone are consistent.
- [x] Main-text word count is between 10,000 and 13,000 words. Chapters 1-6 contain approximately 12,286 words; including the 338-word abstract gives 12,624. References, search records, planning files, and appendices are excluded.
- [ ] Faculty rules are confirmed for whether tables, captions, quotations, front matter, references, and appendices count toward the word limit.
- [ ] Faculty formatting and submission rules are checked.

## Gate 7 - References and integrity

- [x] One IEEE reference style is used consistently in the consolidated reference list.
- [x] All numbered in-text citations have matching reference-list entries.
- [x] All reference-list entries are cited in the thesis.
- [x] Primary publication or authoritative standards sources replace inappropriate product/GitHub references where available.
- [x] URLs, DOI values, authors, venues, years, and available page ranges are verified; any faculty-specific access-date requirement remains a formatting decision.
- [x] The exact external embedding model is cited; thesis figures are original, and the evaluation datasets are identified as researcher-created.
- [x] No direct quotations are used; research paraphrases are accompanied by the relevant citations.
- [ ] The final document passes the institution's originality and research-integrity process.

## Final acceptance gate

- [x] Every objective has a method, result, discussion, and conclusion.
- [x] Every quantitative claim is reproducible from retained evidence.
- [x] Every implementation claim agrees with the frozen code.
- [x] Limitations are stated without hiding negative or inconclusive results.
- [ ] Supervisor feedback has been applied.
- [ ] Final PDF has been reviewed page by page after export.
- [ ] Thesis is ready for submission.

## Current overall assessment

**Core implementation:** complete for the evaluated research scope\
**Novelty:** defensible as an integration contribution\
**Evaluation:** final frozen-commit offline, retrieval, and real-Windows evidence retained\
**Content:** abstract, abbreviations, six chapters, references, figures, tables, and two appendices are complete as an evidence-aligned draft\
**Submission status:** content complete; supervisor approval, Word formatting/front matter, institutional checks, and final PDF review remain
