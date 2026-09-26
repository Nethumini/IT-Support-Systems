# Thesis Completion Checklist

## How to use this file

This is the living source of truth for determining whether the thesis is complete. Check an item only when the deliverable and its supporting evidence both exist. A paragraph that merely promises future work does not complete an item.

Status reviewed: **26 September 2026**\
Detailed plan: `THESIS_RESTRUCTURING_PLAN.md`\
Detailed factual corrections: `THESIS_CORRECTIONS.md`

## Gate 1 - Research definition

- [ ] Final title approved and used consistently.
- [ ] General aim finalized.
- [ ] Specific objectives finalized and measurable.
- [ ] Research questions finalized and aligned with the objectives.
- [ ] Scope and exclusions explicitly stated.
- [ ] Integration-based novelty statement used consistently.
- [ ] Research gap supported by a documented literature search and comparison. First search record and comparison draft created; final review remains.
- [ ] No unsupported "first," "none exists," or universal novelty claim remains.

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
- [ ] Final implementation commit is frozen and recorded.
- [ ] Final dependency/version table is verified against the frozen commit.
- [ ] Complete automated test suite finishes cleanly and its output is retained. Pre-freeze status on 26 September 2026: a clean copy of the implementation (no `.env`, no `data/processed` directory, no provider key, outbound network blocked) passed 518/518 tests offline; no JUnit file was retained for that run. The retained interim JUnit file, `backend/evaluation/results/test-suite-interim-20260926.xml`, records an earlier 501/501 run and does not contain the 518-test suite. Final JUnit evidence must be generated from Commit 1 after it is created.

## Gate 3 - Evaluation evidence

- [x] Comparative simulator harness exists.
- [x] Thirty-two unique scenarios exist, including recovery cases.
- [x] Three repeatability runs are supported.
- [x] Scenario labels and justifications are included in an appendix. `thesis_restructured/appendix_a_evaluation_scenarios.md` records all 32 author-labelled cases, their fixed inputs, special controls, expected routes, and label reasons.
- [ ] Independent expert review of labels is recorded, or the author-labelled limitation is stated everywhere relevant.
- [ ] Final comparative run is generated from the frozen implementation commit.
- [ ] Counts per unique scenario are separated from repeated-run totals.
- [ ] Every percentage reports its numerator and denominator.
- [ ] Condition B is described as an approval-all/rubber-stamp simulation, not real human behaviour.
- [ ] Paired/comparable scenario analysis is used for success-rate comparisons.
- [ ] Fault-detection denominator is explicitly defined.
- [ ] Retrieval evaluation includes labelled queries, Hit@1, Hit@3, suitable ranking metrics, and error analysis. The interim live run produced Hit@1 30/30, Hit@3 30/30, and MRR 1.000; raw files and a limitations-aware analysis are retained. It remains unchecked until the frozen-commit rerun is complete.
- [x] End-to-end cases exercise retrieval, proposal, risk, approval, execution, verification, and recovery/escalation. Controlled cases E2E-01 and E2E-02 traverse the authenticated HTTP and service path; the external model and retriever are fixed to isolate controller behaviour. Evidence is retained in `backend/evaluation/results/end-to-end-safety-20260926.xml` and its companion Markdown summary.
- [x] Prompt/tool-injection behaviour is tested through the real path. PI-01 to PI-03 cover claimed approval in user text, malicious retrieved instructions, and unknown model-produced action identifiers. The demonstrated property is deterministic effect containment, not universal model immunity.
- [ ] Real Windows evidence is retained with device/OS, timestamp, configuration, trace, and result.
- [ ] Latency is measured end to end or clearly labelled as simulator/controller latency only.
- [ ] Raw evaluation files and calculation procedure are retained. Interim retrieval CSV, JSON, hashes, configuration, explicit denominators, timing, and analysis are retained; final frozen-commit outputs for all evaluation components still remain.
- [ ] Limitations and threats to validity are derived from the actual evaluation.

## Gate 4 - Six-chapter restructuring

- [ ] Chapter 1 contains background, problem, gap, questions, significance, scope, short solution overview, and summary. First structural draft created; citations and approval remain.
- [ ] Chapter 2 contains the general and specific objectives. First structural draft created; proposal/supervisor confirmation remains.
- [ ] Chapter 3 compares literature and finishes with the synthesized gap and design implications. First evidence-based draft created; final citation and supervisor review remain.
- [ ] Chapter 4 merges the research-relevant Methodology, SRS, and Implementation/Design material. First implementation-grounded draft created; figures and final methodological details remain.
- [x] Chapter 4 defines all risk inputs according to the actual code and records their limitations.
- [ ] Chapter 4 contains the complete evaluation plan without reporting outcomes. First plan drafted; final retrieval set, end-to-end cases, frozen configuration, and past-tense revision remain.
- [ ] Chapter 5 reports the final artefact and factual results without broad interpretation.
- [ ] Chapter 5 reports a result for every specific objective.
- [ ] Chapter 6 interprets findings against the questions, objectives, and literature.
- [ ] Chapter 6 contains contribution, implications, limitations, direct conclusions, and future work.
- [ ] Long SRS, raw results, test matrices, and evidence are moved to appendices as appropriate.

## Gate 5 - Implementation accuracy

- [ ] Retrieval is described as the implemented in-process Gemini-embedding comparison, not ChromaDB/LangChain.
- [ ] The model is identified as `gemini-embedding-001`, subject to final configuration verification.
- [ ] No document-chunking or environment-metadata-filter claim remains unless implemented.
- [ ] Diagnosis confidence is identified as an LLM-provided input to a deterministic risk calculation.
- [ ] Evidence quality is described as similarity-based unless richer assessment is implemented.
- [ ] Impact and affected-resource signals are described according to their catalogue/configuration derivation.
- [ ] Low-risk execution is not described as entirely automatic while the interface still requires a Run action.
- [ ] Audit logging is not called tamper-proof or tamper-evident unless strengthened and tested.
- [ ] Conceptual agents are distinguished from concrete services and endpoint orchestration.
- [ ] Approval-token scope and approver identity are described separately and accurately.
- [ ] Logical architecture is not misrepresented as physically isolated deployment zones.
- [ ] Action, verification-contract, knowledge-article, and test counts are regenerated from the frozen commit.

## Gate 6 - Front matter and presentation

- [ ] Faculty title page is correct.
- [ ] Declaration and approval pages are included if required.
- [ ] Abstract reports the problem, method, main results, contribution, and principal limitations.
- [ ] Table of contents is regenerated.
- [ ] List of figures is complete and regenerated.
- [ ] List of tables is complete and regenerated.
- [ ] Abbreviation list is included and abbreviations are defined at first use.
- [ ] Figure and table captions and numbering are unique and correct.
- [ ] Every figure and table is referenced and explained in the text.
- [ ] Tense, terminology, spelling, and academic tone are consistent.
- [ ] Main-text word count is between 10,000 and 13,000 words. The current Chapters 1-4 drafts contain approximately 9,324 words; references, search records, and planning files are excluded from this figure.
- [ ] Faculty rules are confirmed for whether tables, captions, quotations, front matter, references, and appendices count toward the word limit.
- [ ] Faculty formatting and submission rules are checked.

## Gate 7 - References and integrity

- [ ] One IEEE reference style is used consistently.
- [ ] All in-text citations have matching reference-list entries.
- [ ] All reference-list entries are cited in the text.
- [ ] Primary publication sources replace inappropriate product/GitHub references where available.
- [ ] URLs, DOI values, authors, venues, years, and access dates are verified.
- [ ] Adapted figures, datasets, tools, models, and external code are cited.
- [ ] Quotations and paraphrases are checked for attribution.
- [ ] The final document passes the institution's originality and research-integrity process.

## Final acceptance gate

- [ ] Every objective has a method, result, discussion, and conclusion.
- [ ] Every quantitative claim is reproducible from retained evidence.
- [ ] Every implementation claim agrees with the frozen code.
- [ ] Limitations are stated without hiding negative or inconclusive results.
- [ ] Supervisor feedback has been applied.
- [ ] Final PDF has been reviewed page by page after export.
- [ ] Thesis is ready for submission.

## Current overall assessment

**Core implementation:** substantially complete\
**Novelty:** defensible as an integration contribution\
**Evaluation:** incomplete for final research claims\
**Structure:** requires conversion from seven chapters to the faculty's six-chapter format\
**Submission status:** not yet ready
