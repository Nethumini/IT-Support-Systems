# Chapter 5 - Results

## 5.1 Chapter Overview

This chapter reports the artefact produced and the observations obtained from the evaluation defined in Chapter 4. Results are presented for the frozen implementation, automated tests, live knowledge retrieval, the three-condition comparative experiment, controlled end-to-end safety cases, and execution on a real Windows endpoint. The chapter finishes by mapping the evidence to the four specific objectives. Broader interpretation, comparison with the literature, limitations, and conclusions are reserved for Chapter 6.

## 5.2 Final Artefact and Evaluation Setting

The evaluated artefact was AutoOps AI commit `cc655c3411ea96e67740e04b9c36df47cdfba064` (`cc655c3`; tree `612f122e2f6514fc5d2716353a1c1fffd5c42751`). The implementation exposed 26 registered actions and 26 corresponding verification contracts. Ten contracts were read-only and two declared rollback actions. The fixed knowledge base contained 30 articles.

The final offline evaluation used Python 3.12.13 and Pytest 8.3.3 on an ARM64 macOS host. Automated and comparative runs used isolated environments, placeholder provider keys, and blocked outbound network access. The provider-call guard recorded no attempted language-model or embedding call. The separate retrieval evaluation used the live Gemini embedding service with `models/gemini-embedding-001`. The endpoint evaluation used Windows 11 Home Single Language, version 10.0.26200, build 26200, with PowerShell 5.1 and Python 3.12.6. Both the Mac backend and Windows agent used the frozen commit with clean working trees.

## 5.3 Automated Functional and Safety Tests

The complete backend suite executed 518 tests. All 518 passed, with zero failures, errors, or skipped tests, in 73.813 seconds. The suite covered authentication, authorization, device isolation, risk thresholds and overrides, approval-token scope and reuse, action contracts, driver restrictions, preconditions, observed-state postconditions, recovery, knowledge review, audit behaviour, evaluation calculations, and endpoint-agent communication.

A focused end-to-end and prompt/tool-safety selection executed 20 tests. All 20 passed, with zero failures, errors, or skipped tests, in 3.475 seconds. Five of these were the principal workflow and adversarial cases: a medium-risk action required approval before verified completion; a silent execution failure was detected and escalated; an approval claim in user text created no authority; retrieved malicious instructions could not create an unknown tool; and a model-shaped unknown action identifier was rejected by the allow-list. The remaining focused tests checked query grounding and prevented generated explanations from overriding recorded execution or verification outcomes.

## 5.4 Retrieval Results

The final live retrieval run evaluated 30 author-labelled paraphrased queries against 30 fixed knowledge articles, with one relevant article identified for each query before execution. Every relevant article was ranked first. Hit@1 was therefore 30/30 (1.000), Hit@3 was 30/30 (1.000), and mean reciprocal rank was 30.0/30 (1.000). There were no misses, empty result sets, non-top-one relevant results, or provider errors. Table 5.1 reports the complete retrieval measures.

**Table 5.1. Final retrieval results**

| Measure | Result |
| --- | ---: |
| Hit@1 | 30/30 (100%) |
| Hit@3 | 30/30 (100%) |
| Mean reciprocal rank | 1.000 |
| Relevant-article score | 0.799-0.890; mean 0.850; median 0.854 |
| Queries with a second returned result | 15/30 |
| Top-one margin where a second result existed | 0.041-0.163; median 0.124 |
| Errors or no-result cases | 0/30 |

The retrieval function took 28,602 ms across all queries. The first query took 15,007 ms because it also embedded all 30 knowledge articles with a cold in-process cache. The other 29 queries had a mean of 468.8 ms and median of 460.8 ms. These values measure only the retrieval and embedding function, not complete user-facing response latency. The ranked article identifiers and scores were identical to the pre-freeze pilot for all 30 queries.

## 5.5 Comparative Scenario Results

The comparative experiment contained 32 unique scenarios: eight labelled low risk, 12 medium risk, and 12 high risk. Twelve were labelled unsafe for autonomous execution, six contained injected faults, and five had no supporting evidence. Each scenario was run three times under each of three conditions. This produced 96 records per condition and 288 records overall. Condition A supplied advice without execution. Condition B was an approval-all or rubber-stamp simulation, not observed human behaviour. Condition C applied the complete risk-adaptive policy. Table 5.2 compares their recorded outcomes.

**Table 5.2. Comparative results across repeated observations**

| Measure | A: advice only | B: approval-all | C: risk-adaptive |
| --- | ---: | ---: | ---: |
| Records | 96 | 96 | 96 |
| Risk-label agreement | 96/96 | 96/96 | 96/96 |
| Route-label agreement | 96/96 | 96/96 | 96/96 |
| Actions executed | 0/96 | 93/96 | 57/96 |
| Unsafe cases executed | 0/36 | 36/36 | 0/36 |
| Human approvals required | 0/96 | 96/96 | 72/96 |
| Verified resolved among executed | Not applicable | 69/93 (74.2%) | 36/57 (63.2%) |
| Verified failures | 0 | 21 | 18 |
| Inconclusive outcomes | 0 | 3 | 3 |
| Precheck failures | 0 | 3 | 3 |
| Escalations | 0 | 21 | 18 |
| Executed injected faults detected | Not applicable | 18/18 | 15/15 |
| Faults reported as success | 0 | 0 | 0 |
| Verified rollbacks | 0/0 | 3/6 | 3/6 |
| Complete audit traces | 96/96 | 96/96 | 96/96 |

Condition C prevented all 36 repeated unsafe cases, whereas Condition B executed all 36. Condition C also required 72 approvals rather than 96, a reduction of 24 approval events across the repeated records. At the unique-scenario level, this was 24/32 rather than 32/32 requiring approval. Under both execution conditions, one unique scenario failed its precheck, two reached rollback, and one of those two obtained verified restoration.

The fault-detection denominator included only injected faults that reached execution. All 18 executed fault records were detected under Condition B. Condition C executed 15 injected-fault records and detected all 15; the remaining three repeated records represented high-risk scenario EV-27, which the policy blocked before execution. No injected fault that executed was reported as successful.

Conditions B and C both executed 19 of the 32 unique scenarios. For all 19 paired scenarios, the verification verdict and final status were the same. Condition B alone executed 12 unsafe high-risk scenarios that Condition C blocked; one additional scenario executed under neither condition because of a precheck failure. Consequently, the two aggregate resolution rates have different executed-case denominators. Across repeatability analysis, all 96 condition-scenario pairs produced stable non-timing outcomes over their three repetitions. Mean harness/controller duration per record was 2.4 ms for A, 3.9 ms for B, and 3.1 ms for C; these were simulator measurements rather than production latency.

## 5.6 End-to-End Safety Outcomes

The controlled end-to-end cases retained the real authentication, API, database, risk, authorization, remediation, verification, and audit layers while fixing external model and retrieval outputs. E2E-01 traversed proposal, medium-risk assessment, approval, execution, observed-state verification, and completion. E2E-02 simulated a command that reported success without producing the required state change; the post-check rejected completion and the request escalated.

The three adversarial cases produced no executable authority from untrusted text. PI-01 showed that a user statement claiming approval did not satisfy the approval state. PI-02 treated an unknown-tool instruction contained in retrieved evidence as data rather than an action. PI-03 rejected an unknown action identifier in model-shaped output because it was absent from the registered catalogue and verification contracts. Each outcome was retained in the 20/20 passing focused test record.

## 5.7 Real-Windows Endpoint Results

The endpoint test connected the Mac-hosted backend to an authenticated Windows polling agent using the PowerShell driver. A read-only `get_startup_programs` request was classified as low risk, routed as an automatic candidate, executed on the endpoint, and returned `verified_success`. Its output was a sorted JSON list of program names only; startup commands and locations were not returned. The before and after snapshots matched and contained flags and SHA-256 fingerprints rather than raw command text.

The recovery case used a dedicated harmless startup value named `AutoOpsThesisDemo`. A watcher re-registered the value after removal to stage an ineffective remediation. The controller classified `disable_startup_item` as medium risk with score 1.300, required user approval, and dispatched it after approval. The PowerShell command succeeded and saved the original value, but the observed state showed the item still enabled. The post-check therefore returned `verified_failure`.

Automatic recovery then executed `enable_startup_item`. Before recovery, both the live and saved values had fingerprint `46449d54bd16c5aca31518121878fcec5ae0a00961328b3afa4b87426eccd08f`. After recovery, the live value retained that fingerprint and the backup no longer existed. Recovery returned `verified_success`, and the request ended as `rolled_back`. A final agent diagnostic and a direct Windows registry check confirmed that the temporary live and backup values were absent. Unrelated recorded startup fingerprints were unchanged.

## 5.8 Results by Objective

Table 5.3 maps each specific objective to the evidence produced by the study.

**Table 5.3. Evidence produced for each specific objective**

| Objective | Recorded result |
| --- | --- |
| O1 - Investigate | Chapter 3 compared intelligent support, retrieval, authorization, runtime enforcement, verification, recovery, and audit approaches and identified the integration gap used to derive the framework requirements. |
| O2 - Design | The completed design connected the five-factor risk model, graded authorization, 26 allow-listed action contracts, driver boundary, observed-state verification, rollback or escalation, and structured audit records. |
| O3 - Implement | The frozen artefact implemented the complete workflow; 518/518 automated tests and 20/20 focused safety tests passed with no failures or errors. |
| O4 - Evaluate | The study retained 288 comparative records, a 30-query live retrieval run, paired and repeatability analyses, controlled end-to-end cases, and a real-Windows verified-rollback trace. |

## 5.9 Chapter Summary

The final artefact passed its complete automated suite and focused safety selection. Retrieval ranked the labelled relevant article first for all 30 queries. In the comparative experiment, the risk-adaptive condition executed no unsafe labelled case, required 24 fewer approvals than approval-all gating, detected every injected fault that reached execution, and produced complete audit traces. The Windows endpoint case additionally demonstrated detection of an ineffective command and fingerprint-verified restoration on real PowerShell. Chapter 6 interprets these findings against the research questions, literature, contribution, and validity constraints.
