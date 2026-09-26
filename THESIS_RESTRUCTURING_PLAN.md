# Thesis Restructuring Plan

## Document purpose

This document is the approved working plan for restructuring `Final Thesis draft - 28647.pdf` so that it:

1. follows the six-chapter structure supplied by the faculty;
2. accurately describes the final AutoOps AI implementation;
3. presents the research novelty as an integration contribution;
4. separates methodology, results, and interpretation;
5. records the evidence still required before the thesis can be considered complete.

This plan does not declare the thesis complete. Completion is tracked separately in `THESIS_COMPLETION_CHECKLIST.md`. Detailed sentence-level factual corrections remain in `THESIS_CORRECTIONS.md`.

## 1. Position of the research

### 1.1 Proposed title

**Context-Aware Intelligent IT Support Systems: A Multi-Agent Framework with Risk-Adaptive and Verifiable Remediation**

Use **Context-Aware** consistently, including the hyphen.

### 1.2 Primary research contribution

The thesis must present the novelty as an integrated remediation framework, not as the invention of RAG, agents, risk scoring, approval, verification, rollback, or audit logging individually.

> This research designs, implements, and evaluates a context-aware IT-support remediation framework that combines evidence-grounded recommendations, deterministic risk-adaptive authorization, controlled action execution, post-action verification, verified rollback or escalation, and auditable decision records within a unified workflow.

The contribution can be summarized as:

`evidence retrieval -> diagnosis/proposal -> deterministic risk assessment -> graded authorization -> controlled execution -> postcondition verification -> rollback/escalation -> audit`

### 1.3 Safe research-gap wording

Do not claim that no previous system exists unless a systematic search proves it. Use wording such as:

> The reviewed literature provides limited evidence of IT-support frameworks that integrate evidence-grounded diagnosis, deterministic risk-adaptive authority, controlled endpoint execution, outcome verification, and verified recovery in one evaluated remediation workflow.

The literature review must support every part of this gap.

### 1.4 Proposed aim and objectives

**General aim**

To design, implement, and evaluate a context-aware, risk-adaptive, and verifiable remediation framework for safer AI-assisted IT support.

**Specific objectives**

1. Investigate existing intelligent IT-support, agentic remediation, retrieval, authorization, verification, and recovery approaches and identify the integration gap.
2. Design an explainable remediation architecture that selects authority according to contextual risk and restricts execution to approved actions.
3. Implement the framework with evidence retrieval, risk assessment, scoped approval, deterministic prechecks, controlled execution, postchecks, rollback or escalation, and audit recording.
4. Evaluate the implemented framework for policy conformance, unsafe-action prevention, human-intervention requirements, retrieval quality, verification and recovery behaviour, reproducibility, and practical operation on a real endpoint.

Each objective must later have an explicit method and a result. If an objective is not evaluated, it must not be described as achieved.

### 1.5 Proposed research questions

These questions should be reconciled with the university proposal and supervisor feedback before final wording:

1. How can evidence-grounded IT-support recommendations be integrated with deterministic, risk-adaptive authorization and controlled remediation?
2. To what extent does the implemented policy prevent scenarios labelled unsafe for autonomous execution while avoiding unnecessary approval requirements compared with the selected baselines?
3. How reliably does the framework verify remediation outcomes and invoke rollback or escalation when execution does not produce the required state?
4. How effectively does the knowledge-retrieval component return relevant approved support evidence for representative IT-support queries?

Do not introduce hypotheses unless the study is redesigned to test predefined statistical hypotheses.

## 2. Required final structure

The current seven chapters must become the following six chapters.

## Chapter 1 - Introduction

**Purpose:** Establish the problem, why it matters, the gap, the research questions, and the boundaries of the work. Keep detailed architecture and implementation material out of this chapter.

### Required sections

1.1 Chapter overview\
1.2 Background\
1.3 Problem statement\
1.4 Research gap\
1.5 Research questions\
1.6 Research motivation and significance\
1.7 Scope and exclusions\
1.8 Overview of the proposed solution\
1.9 Chapter summary

### Material to retain or move

- Retain the useful background, IT-support problem, motivation, and short system overview from the current Chapter 1.
- Move objectives into the new Chapter 2.
- Move detailed technologies, architecture, requirements, resource requirements, and implementation decisions into Chapter 4.
- Include only one simple workflow figure in Section 1.8.
- State explicitly that the work evaluates an applied framework and does not claim autonomous operation for unrestricted or critical actions.

## Chapter 2 - Objectives

**Purpose:** State what the research intends to accomplish in measurable terms.

### Required sections

2.1 General objective or aim\
2.2 Specific objectives\
2.3 Objective-to-evidence overview, if permitted by the faculty template\
2.4 Chapter summary, if chapter summaries are required consistently

### Writing requirements

- Use verbs such as **investigate**, **design**, **implement**, and **evaluate**.
- Avoid objectives such as "create an intelligent system" that cannot be measured.
- Ensure the evaluation chapter reports a result for every objective.

## Chapter 3 - Literature Review

**Purpose:** Establish the concepts and prior evidence needed to justify the research design and gap.

### Required sections

3.1 Chapter overview\
3.2 Intelligent and context-aware IT support\
3.3 Multi-agent and tool-using systems\
3.4 Retrieval-augmented generation and grounded support recommendations\
3.5 Risk-adaptive automation, human approval, and authorization\
3.6 Controlled execution, preconditions, postconditions, rollback, and escalation\
3.7 Security, auditability, and prompt/tool safety\
3.8 Comparison of existing studies and systems\
3.9 Synthesized research gap and implications for this work\
3.10 Chapter summary

### Required improvements

- Explain the literature-search method: databases, keywords, date range, inclusion/exclusion approach, and limitations.
- Compare prior work rather than listing one paper after another.
- Include adjacent fields such as autonomic computing/MAPE-K, IT service and change management, adaptive automation, approval fatigue, policy enforcement, and capability-based access control where relevant.
- End with a comparison table showing which prior approaches include retrieval, contextual risk, graded authority, controlled execution, verification, recovery, and evaluation.
- Use cautious language: the review establishes limited integration evidence, not universal non-existence.
- Replace informal web or repository references with primary papers or official documentation where possible.

## Chapter 4 - Methodology

**Purpose:** Explain exactly how the research and evaluation were conducted so that another researcher can understand and, where feasible, reproduce them.

This chapter must merge relevant material from the current Methodology, SRS, and Implementation and Design chapters. It describes the plan and procedure, not the observed results.

### Required sections

4.1 Chapter overview\
4.2 Research design and justification\
4.3 Data, knowledge sources, scenarios, devices, and stakeholders\
4.4 Requirements identification and analysis\
4.5 Proposed framework and architecture\
4.6 Risk-adaptive remediation design\
4.7 Knowledge retrieval and learning design\
4.8 Controlled execution, verification, rollback, and escalation design\
4.9 Implementation procedure and technologies\
4.10 Evaluation plan\
4.11 Ethics, privacy, security, and project management\
4.12 Chapter summary

### Content requirements

- Identify the research approach, such as design science research, and justify how the artefact and evaluation stages correspond to that approach.
- Define the actual risk formula, factor scales, thresholds, overrides, and source of every input.
- Include a table with: factor, implemented signal, range, rule/threshold, and limitation.
- Distinguish deterministic controller decisions from LLM-generated inputs. The final risk class is deterministic, but diagnosis/classification confidence is currently supplied by the model.
- Describe evidence quality accurately as the implemented best-match similarity signal unless richer evidence assessment is added.
- Explain that impact and affected-resource factors are substantially catalogue/configuration derived unless dynamic signals are implemented.
- Describe the real retrieval path: `gemini-embedding-001`, title plus issue-pattern representation, cosine similarity, per-process cache, category bonus, threshold, usage-weighted ranking, and inclusion of approved learned articles.
- Do not claim LangChain, ChromaDB, document chunking, environment metadata filtering, or `text-embedding-004` in the final implementation.
- Explain the action catalogue, validation contracts, scoped approval, execution drivers, endpoint agent, audit records, knowledge-review boundary, and recovery workflow.
- Label any simplified agent pseudocode as conceptual. The implemented orchestration is distributed across services and API workflow code rather than separate RAG, diagnostic, and orchestrator agent classes.
- State the evaluation scenarios, baselines, repetitions, measures, fault injection, analysis procedure, and validity controls before presenting any results.
- Describe the three evaluation conditions precisely. Condition B is an approval-all/rubber-stamp policy simulation; it is not evidence of decisions made by real human participants.

## Chapter 5 - Results

**Purpose:** Report what was implemented and what was observed, without giving the broader interpretation reserved for Chapter 6.

### Required sections

5.1 Chapter overview\
5.2 Final artefact, version, and evaluation setting\
5.3 Implemented framework and key outputs\
5.4 Functional and non-functional test results\
5.5 Retrieval evaluation results\
5.6 Risk-policy and comparative evaluation results\
5.7 Verification, fault-injection, rollback, and escalation results\
5.8 End-to-end and real-endpoint results\
5.9 Results by objective\
5.10 Chapter summary

### Reporting requirements

- Record the final Git commit, configuration, model, knowledge-base version, driver, device/operating system, and execution date.
- Report **32 unique scenarios with three repeatability runs per condition**, rather than presenting 96 repeated observations as 96 independent scenarios.
- Separate counts per unique scenario from totals across repetitions.
- Report raw denominators with every rate.
- Present the author-labelled scenario results as specification-conformance evidence unless independent experts validate the labels.
- Do not present millisecond simulator timing as user-visible or production end-to-end latency.
- Explain the denominator used for fault-detection metrics; injected faults that were not executed must not silently inflate the rate.
- Compare resolution rates only over comparable or paired executed scenarios. The current policies execute different scenario mixes, so aggregate verified-resolution percentages do not prove superiority.
- Include retrieval Hit@1, Hit@3, MRR where appropriate, and an error analysis over labelled queries.
- Include selected audit traces/screenshots demonstrating the complete path and real Windows execution. Place large raw records in an appendix.
- Keep interpretations such as "this demonstrates improved safety" for Chapter 6.

### Currently defensible result wording

Until stronger validation is added, use a conclusion at approximately this strength:

> In an author-labelled, simulator-based evaluation of 32 scenarios, the risk-adaptive policy conformed to its specification, prevented all 12 cases labelled unsafe to automate, and required human intervention in 24 rather than 32 unique cases under an approval-all baseline. All three repeatability runs were stable, and no executed injected fault was reported as a verified success. These findings demonstrate specification conformance in simulation, not expert validity or real-world superiority.

All values must be regenerated and checked against the final implementation before inclusion.

## Chapter 6 - Discussion and Conclusions

**Purpose:** Explain what the results mean, how strongly they answer the research questions, and where the evidence remains limited.

### Required sections

6.1 Discussion of key findings by research question\
6.2 Comparison with the literature\
6.3 Research contribution and practical implications\
6.4 Limitations and threats to validity\
6.5 Conclusions\
6.6 Future work

### Required discussion points

- Explain what integration added beyond the individual existing mechanisms.
- Separate demonstrated findings from expected benefits.
- Discuss policy conformance separately from whether the policy thresholds and author labels are externally valid.
- Address simulator use, synthetic scenarios, author-labelled risks, deterministic repeats, small knowledge base, model dependence, ad hoc weights, limited real-device coverage, and deployment/security boundaries.
- Discuss why real-device testing exposed verification issues that the simulator did not expose.
- Give direct, evidence-based answers to the research questions and objectives.
- Do not treat the conclusion as another summary of all chapters.
- Make future work arise from identified limitations: expert label validation, broader endpoints, richer evidence signals, usability study with ethics approval, attested device state, stronger audit integrity, and deployment-scale evaluation.

## 2A. Working word-count budget

The final thesis main text must remain within **10,000-13,000 words**. The working target is approximately **11,500-12,000 words**, leaving enough margin for revision without exceeding the upper limit. Unless the faculty specifies otherwise, references, appendices, and front matter should be tracked separately from the six-chapter main-text count.

| Chapter | Working allocation | Current draft position |
| --- | ---: | --- |
| Chapter 1 - Introduction | 1,800-2,100 | Approximately 2,084 words; within allocation |
| Chapter 2 - Objectives | 400-500 | Approximately 434 words; within allocation |
| Chapter 3 - Literature Review | 3,200-3,600 | Approximately 4,033 words; reduce during final editing |
| Chapter 4 - Methodology | 2,200-2,500 | Approximately 2,406 words; within allocation |
| Chapter 5 - Results | 1,800-2,200 | Not yet drafted |
| Chapter 6 - Discussion and Conclusions | 1,300-1,600 | Not yet drafted |
| **Total main text** | **10,700-12,500** | **Approximately 8,957 words drafted across Chapters 1-4** |

Chapter 3 may remain detailed while Chapter 4 is being prepared, but approximately 400-800 words of repetition should be removed during the final whole-thesis edit. Tables, captions, and institution-specific inclusions must be counted according to the faculty's official word-count rules once those rules are confirmed.

## 3. Front matter, references, and appendices

### Front matter to add or verify

- Title page in the required faculty format
- Declaration/originality statement, if required
- Supervisor approval page, if required
- Abstract containing problem, method, principal results, contribution, and limitations
- Acknowledgements, if required
- Table of contents
- List of figures
- List of tables
- List of abbreviations

### Reference corrections

- Use one IEEE style consistently.
- Complete missing bibliographic details, authors, venue, year, pages, DOI/URL, and access date where required.
- Cite primary papers for RAG, ReAct, AutoGen, and related frameworks rather than general product pages or GitHub repositories when a paper exists.
- Replace the incorrect RAG and transformer reference URLs with their official publication records.
- Ensure every in-text citation appears in the reference list and every listed reference is cited.
- Cite adapted figures, datasets, frameworks, and model documentation.

### Appendices

Recommended appendices are:

- A. Functional and non-functional requirements
- B. Complete scenario definitions and expected labels
- C. Action catalogue and verification-contract summary
- D. Automated test matrix and final output
- E. Raw evaluation results and analysis calculations
- F. End-to-end audit traces and real-device screenshots
- G. Retrieval-query labels and error analysis
- H. Survey, consent, or interview material only if an approved human study is conducted
- I. Relevant configuration and reproducibility instructions

Long SRS material, detailed use cases, resource tables, and code-like listings should move to appendices unless they are essential to understanding the method.

## 4. Required project and evidence work before final writing

### 4.1 Must complete

1. **Completed 26 September 2026:** enforce medium-risk approval ownership or explicit `troubleshoot:auto_resolve` authority and cover the boundary with service and API tests.
2. Freeze a final implementation commit and record it in the thesis.
3. Obtain a clean final automated-test run and retain the output.
4. Rerun the comparative evaluation against the final commit.
5. Evaluate retrieval using labelled queries and report retrieval metrics plus error analysis.
6. **Completed on an interim basis on 26 September 2026:** exercise complete chat-to-retrieval-to-remediation workflows and retain audit evidence. Repeat the controlled cases after the final commit is frozen.
7. **Completed on an interim basis on 26 September 2026:** exercise prompt/tool injection through the actual retrieval or tool-use path. The supported claim is deterministic effect containment, not universal language-model immunity; repeat after the final commit is frozen.
8. Retain reproducible evidence from the real Windows endpoint test.
9. Validate scenario labels independently if feasible; otherwise describe them as author-labelled and limit the claims.
10. Recalculate every table and chart from retained raw results.

### 4.2 Optional improvements, not mandatory if accurately limited

- Richer evidence-quality calculation incorporating source authority, freshness, applicability, and corroboration
- Dynamic measurement of affected resources and impact
- A frontend approval queue for expert reviewers
- A working frontend knowledge-review page
- Cryptographic or append-only audit protection
- Device attestation for endpoint-reported state
- A formally approved user study of usability, trust, or approval fatigue
- A persistent vector database, which is unnecessary for the current small article set unless scale becomes an evaluated requirement

Do not delay the thesis merely to implement optional features. If they are not built and evaluated, state them as limitations or future work.

## 5. Claim-control rules

Before retaining any technical statement, classify it as one of the following:

| Claim type | Required support |
| --- | --- |
| Implemented capability | Final source code plus a test or trace |
| Quantitative result | Raw result file, stated denominator, configuration, date, and final commit |
| Real-device behaviour | Device/OS details and retained execution/audit evidence |
| Literature gap | Comparative synthesis of relevant primary literature |
| Improvement or superiority | Valid baseline comparison over comparable cases |
| User acceptance/usability | Ethics-approved participant study and analysis |
| Security property | Implemented enforcement plus adversarial/authorization tests |

Avoid the words **proves**, **guarantees**, **tamper-proof**, **fully autonomous**, **production-ready**, and **first framework** unless the evidence actually supports them.

## 6. Objective-to-evidence traceability

Maintain this matrix while writing:

| Objective | Method | Required result | Current position |
| --- | --- | --- | --- |
| O1: Investigate and identify the gap | Structured literature search and comparison | Synthesis and gap table | Partial; review and search method need strengthening |
| O2: Design the framework | Requirements, architecture, risk and state-machine design | Design artefacts and rationale | Substantially available; must be consolidated in Chapter 4 |
| O3: Implement the framework | Iterative implementation and verification | Final artefact, tests, traces, screenshots | Substantially available; authorization boundary is implemented and the pre-freeze suite passes 518/518 tests offline, but the implementation commit is not frozen and the final suite evidence must be regenerated from it |
| O4: Evaluate the framework | Scenario comparison, retrieval evaluation, fault injection, end-to-end and endpoint cases | Final metrics, error analysis, raw evidence, limitations | Partial; interim simulator, retrieval, controlled end-to-end, injection-safety, and endpoint evidence exists, but final frozen-commit runs and evidence consolidation remain |

## 7. Recommended writing order

1. Freeze the aim, objectives, research questions, and scope.
2. Build the literature comparison and finalize the gap.
3. Write Chapter 4 from the actual implementation and planned final evaluation.
4. Complete the mandatory project/evaluation work.
5. Generate tables and figures directly from final retained results.
6. Write Chapter 5 using factual observations only.
7. Write Chapter 6 by answering each research question from Chapter 5 evidence.
8. Rewrite Chapter 1 so it accurately previews the completed study.
9. Write Chapter 2, abstract, and final conclusion using the finalized evidence.
10. Complete references, appendices, cross-references, lists, language editing, and formatting checks.

## 8. Immediate restructuring map

| Current material | Final destination |
| --- | --- |
| Current Chapter 1 introduction | Chapter 1, except objectives and technical detail |
| Objectives currently embedded in the introduction | New Chapter 2 |
| Current Chapter 2 literature review | Chapter 3, expanded and synthesized |
| Current Chapter 3 methodology | Chapter 4 |
| Current Chapter 4 SRS | Selected research-relevant content in Chapter 4; detail in Appendix A |
| Current Chapter 5 implementation and design | Design/procedure in Chapter 4; produced artefact/screens in Chapter 5 |
| Current Chapter 6 testing and evaluation | Evaluation method in Chapter 4; observed results in Chapter 5 |
| Current Chapter 7 conclusions and recommendations | Chapter 6, rewritten using final evidence |
| Self-reflection, extensive business case, long resource tables | Appendix or remove unless required by faculty |

## 9. Known document-quality corrections

- Regenerate the table of contents and lists of figures/tables after restructuring.
- Correct the item labelled "Figure 5.3. Contribution features" to a table and eliminate the duplicate Figure 5.3 numbering.
- Define every abbreviation, including DSR, at first use.
- Use past tense for completed methods and results; reserve future tense for proposed future work.
- Use consistent terminology for context-aware, multi-agent, risk-adaptive, remediation, verification, and escalation.
- Update React to the version used by the final implementation.
- Describe the Docker diagram as a logical architecture unless the depicted isolation zones are actually deployed.
- Describe the audit store as persistent, ordered, and access-controlled; do not call it tamper-evident unless that property is implemented.
- State that approval records identify the approver, while execution-token scope covers the action, parameters, target, expiry, and single use. Do not claim the token itself is bound to the actor unless implemented.

## 10. Definition of thesis-ready

The thesis is ready for final supervisor review only when all mandatory items in `THESIS_COMPLETION_CHECKLIST.md` are checked, all reported values can be traced to retained evidence, and no thesis claim contradicts the final code.
