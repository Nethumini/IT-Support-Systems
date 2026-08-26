# INTERIM SUBMISSION 01 (Revised)

**Research Title**

> **Context-Aware Intelligent IT Support: A Multi-Agent LLM Framework with Knowledge-Grounded Troubleshooting and Human-Gated Automated Remediation**

**Student:** P. T. N. Pathirana (28647)
**Institution:** NSBM Green University Town
**Submission:** Interim Submission 01 (Revised Edition)
**Date:** 18 August 2026

---

## Declaration of Current Research Status

In accordance with academic integrity requirements, this document explicitly distinguishes between work that is **complete**, work that is **in progress**, and work that is **planned but not yet executed**. No performance results are reported that have not been empirically measured.

| Research Phase | Status | Evidence Location |
|---|---|---|
| Problem identification and literature review | **Complete** | Chapters 1–2 |
| Methodology definition | **Complete** | Chapter 3 |
| System architecture design | **Complete** | Chapter 4 |
| Core system implementation (5 agents, API, frontend, RBAC) | **Complete and verified operational** | Chapter 4, Appendix A |
| Retrieval (RAG) subsystem | **Functionally complete; architecture revision required** | §4.5, §7.2 |
| Predictive ML subsystem | **Prototype trained; requires re-specification** | §4.7, §7.2 |
| Evaluation instrument design | **In progress** | Chapter 5 |
| Dataset construction for evaluation | **In progress — currently insufficient** | §5.3, §7.2 |
| Empirical evaluation execution | **Not started** | Chapter 6 |
| Results and statistical analysis | **Not started — no results claimed** | Chapter 6 |

**Critical statement:** At the time of this submission, the evaluation corpus contains 6 knowledge-base articles and the operational database contains 0 processed tickets. **No empirical performance results exist yet.** Chapter 6 therefore reports *implementation verification outcomes* only, and explicitly does not report resolution-time, accuracy, or user-satisfaction findings. These remain planned work (§7.3).

---

# Chapter 1 — Introduction

## 1.1 Chapter Overview

This chapter establishes the research foundation for a multi-agent, LLM-based IT support framework. It proceeds from the operational context of modern IT Service Management (ITSM), through a critical examination of what current automated approaches can and cannot do, to a precisely delimited research gap. It then states the research question, aim, objectives, and the specific scholarly contribution this work intends to make.

A deliberate change from the previous version of this submission is the **narrowing and evidencing of the novelty claim**. The earlier draft asserted that no integrated LLM-based IT support platform existed. That claim is not defensible: several commercial platforms already combine conversational AI with ticket automation and remediation workflows. This revision reframes the contribution around what is genuinely absent from the literature — an **openly specified, architecturally transparent, ablation-evaluated reference design** — which is a claim the research can actually substantiate.

## 1.2 Problem Background

### 1.2.1 The Operational Context

Enterprise IT support operates under a structural imbalance. The volume and heterogeneity of supported endpoints, applications, and services continue to expand, while the pool of skilled support personnel does not expand proportionally. Support organisations respond by tiering their workforce (L1 → L2 → L3), which controls cost but introduces queuing delay and repeated context-gathering at each handoff.

A substantial fraction of this workload is repetitive. The same categories of incident — credential and access problems, network and VPN connectivity, endpoint performance degradation, peripheral and driver faults — recur continuously, and their resolutions are frequently already documented within the organisation's own knowledge base. The inefficiency is therefore not primarily a *knowledge* deficit but a **knowledge-access and knowledge-application deficit**: the solution exists, but locating, interpreting, and executing it costs skilled human time on every recurrence.

### 1.2.2 The Technological Opening

Three developments make this problem newly tractable.

**Large Language Models (LLMs).** Contemporary LLMs demonstrate multi-step reasoning and sustained natural-language interaction sufficient for diagnostic dialogue [2]. Critically for IT support, they can conduct *adaptive* troubleshooting — adjusting the next diagnostic step based on the user's report of the previous one — which fixed decision-tree systems cannot.

**Retrieval-Augmented Generation (RAG).** LLMs generate fluent but sometimes factually incorrect output. RAG mitigates this by retrieving relevant documents from a trusted corpus and conditioning generation on them [3], [4]. In IT support this matters acutely: an incorrect remediation instruction does not merely misinform, it can damage the user's system. RAG has been applied specifically to incident-resolution recommendation, where retrieval over historical resolution records demonstrably improves recommendation relevance [6], and to ticket resolution over engineering issue trackers [17].

**LLM-based agent architectures.** Rather than a single monolithic model performing all functions, the agentic paradigm decomposes a task across specialised components that reason, act, observe outcomes, and iterate [1], [11]. This decomposition is significant for governance as much as for capability: it creates explicit boundaries at which policy can be enforced.

### 1.2.3 Why the Problem Remains Unsolved

The availability of these technologies has not produced solved IT support automation. The most direct evidence is benchmark performance: ITBench, a systematic benchmark of AI agents on real-world IT automation tasks, reports that agents built on state-of-the-art models resolve only **11.4% of Site Reliability Engineering scenarios**, 25.2% of security-operations scenarios, and 25.8% of financial-operations scenarios [7]. Similarly, evaluation of LLMs for cloud incident root-causing found meaningful but far-from-sufficient assistance quality [5].

This is the central justification for continued research: **the enabling technologies exist, and the task nevertheless remains largely unsolved.** The unresolved questions are therefore not "can an LLM talk about IT problems" but rather how such systems should be *architected*, *grounded*, and *governed* to become dependable.

## 1.3 Problem Statement

### 1.3.1 General Problem

Organisations cannot scale human IT support linearly with demand, and the repetitive fraction of support work consumes skilled capacity that could otherwise address novel and complex incidents. Automation attempts to date either constrain themselves to safe-but-shallow information retrieval, or extend into action-taking without adequate governance. Neither is satisfactory for production deployment.

### 1.3.2 Specific Problems Addressed

This research targets five specific, evidenced deficiencies:

**P1 — Shallow conversational capability.** Intent-classification and decision-tree support bots handle single-turn deflection adequately but degrade in multi-turn, context-dependent diagnosis where the correct next step depends on the outcome of the previous one.

**P2 — Ungrounded generation.** LLM-based assistants that generate advice without retrieval from organisational knowledge produce plausible but organisation-inappropriate guidance. Retrieval grounding is an established mitigation [3], [4], [6], but its *contribution within a full support pipeline* is rarely isolated and measured.

**P3 — Static ticket lifecycle management.** Ticket creation, prioritisation, categorisation, and status transition remain largely manual or governed by static rules. Machine-learning approaches to ticket classification and routing have been studied [14], [15], [16], [19], but typically as standalone classifiers detached from the conversational process that generates the ticket.

**P4 — The action gap.** Support systems predominantly *advise* rather than *act*. Even well-defined, low-risk operations (clearing temporary files, flushing DNS caches, restarting a service) are left to the user to perform manually. Closing this gap requires executing commands on user systems, which introduces genuine safety and security exposure — notably prompt injection, whereby adversarial content in the input stream induces unintended actions [10].

**P5 — Absence of architectural evidence.** Where integrated systems do exist commercially, their internal architecture, component contributions, and failure characteristics are not publicly documented or independently evaluated. Researchers and practitioners therefore have no evidence base on which architectural decisions actually matter.

## 1.4 Research Gap

### 1.4.1 Positioning Against Existing Work

An honest statement of the gap requires acknowledging what already exists. Commercial platforms — including Moveworks, Aisera, ServiceNow Virtual Agent/Now Assist, and Freshservice Freddy AI — already deliver conversational IT support with degrees of ticket automation and workflow-triggered remediation. Any claim that this combination is unprecedented would be incorrect.

Academic work, conversely, has addressed the constituent capabilities largely **in isolation**:

| Capability | Representative academic treatment | Studied as part of an integrated, evaluated pipeline? |
|---|---|---|
| Conversational LLM reasoning | [1], [2], [11] | No — general-purpose, not ITSM-situated |
| Retrieval grounding for IT incidents | [6], [17] | Partially — retrieval evaluated, not end-to-end resolution |
| LLM-assisted incident diagnosis | [5], [18] | No — diagnosis only, no action execution |
| ML ticket classification / routing | [14], [15], [16], [19] | No — standalone classifiers |
| Agent evaluation on IT tasks | [7] | Benchmark only — does not propose an architecture |
| AIOps synthesis | [8], [9] | Survey — identifies fragmentation, does not resolve it |

### 1.4.2 Statement of the Gap

> **The gap is not the absence of an integrated system, but the absence of an openly specified, architecturally transparent, and component-wise evaluated reference design for agent-decomposed IT support with governed remediation.**

Specifically, the literature does not currently answer:

- **G1.** What does agent decomposition contribute, *measurably*, over a monolithic LLM performing the same functions? No published ablation isolates this.
- **G2.** What does retrieval grounding contribute to *end-to-end resolution outcomes* in IT support, as distinct from retrieval relevance measured in isolation?
- **G3.** How should a risk-tiered, human-gated remediation mechanism be specified so that action-taking becomes safe enough to deploy, and what is the usability cost of that gating?

These are answerable questions with an implementable system and a designed experiment. They constitute the research contribution of this project.

## 1.5 Research Question

**Primary Research Question**

> *To what extent does decomposing an LLM-based IT support system into specialised, independently governed agents — combined with retrieval-grounded troubleshooting and risk-tiered, human-gated remediation — improve diagnostic accuracy, resolution effectiveness, and operational safety relative to monolithic LLM baselines?*

This formulation is deliberately **comparative and testable**, replacing the previous draft's design-descriptive question ("how can a system be designed…"), which admitted no empirical answer.

**Sub-Questions**

- **RQ1.** How accurately can an LLM-based classifier distinguish technical from non-technical requests and assign category and urgency, compared with keyword-based and classical ML baselines [14], [15]?
- **RQ2.** What measurable effect does retrieval grounding have on the factual correctness and organisational appropriateness of generated troubleshooting guidance [3], [4], [6]?
- **RQ3.** Does distributing ticket lifecycle reasoning across dedicated agents improve lifecycle-state correctness relative to a single-model implementation?
- **RQ4.** Can a whitelist-constrained, risk-tiered, approval-gated execution mechanism prevent unsafe action execution under adversarial input, including prompt-injection attempts [10]?
- **RQ5.** What is the contribution of each architectural component, established through systematic ablation?

## 1.6 Research Motivation

**Empirical evidence of an unsolved problem.** The 11.4% SRE resolution rate reported by ITBench [7] is the strongest single motivator: it demonstrates that applying current models to IT operations does not by itself produce competent automation, and that architectural research is warranted.

**A governance question that matters beyond this domain.** Any AI system permitted to execute commands on real infrastructure raises the question of how autonomy should be bounded. Prompt injection against tool-using agents is a demonstrated, practical attack class [10]. IT support is a useful setting in which to study bounded autonomy because the action space is enumerable and risk-classifiable — unlike open-ended agent domains.

**The reproducibility deficit.** Commercial systems are not inspectable. If the research community is to reason about how these systems should be built, openly documented architectures with published evaluation methodology are necessary. This project can supply one.

**Practitioner relevance.** Organisations without the budget for enterprise ITSM AI platforms have no documented reference design to build against. An open architecture with characterised component contributions has direct practical value.

## 1.7 Research Aim

To design, implement, and empirically evaluate an agent-decomposed, retrieval-grounded IT support framework with risk-tiered human-gated remediation, and to determine — through systematic ablation — the measurable contribution of each architectural component to diagnostic accuracy, resolution effectiveness, and operational safety.

The aim is stated in terms of **determining component contributions**, not of demonstrating superiority over industry averages. This is a deliberate correction: the previous draft promised improvement "compared to conventional IT support approaches" while planning a comparison against a published industry statistic drawn from a different population — a comparison that could not have supported the claim.

## 1.8 Research Objectives

| # | Objective | Verifiable Completion Criterion | Status |
|---|---|---|---|
| **O1** | Identify and critically analyse limitations of existing automated IT support approaches through structured literature review | Comparative analysis table distinguishing academic and commercial approaches (§1.4.1, Ch. 2) | **Complete** |
| **O2** | Analyse the architectural suitability of LLM, RAG, and multi-agent paradigms for ITSM, including their failure modes | Technological analysis with justified design decisions (Ch. 2) | **Complete** |
| **O3** | Design and implement an agent-decomposed IT support framework with retrieval grounding and governed remediation | Operational system with five specialised agents, verified end-to-end (Ch. 4) | **Complete** |
| **O4** | Design an evaluation methodology capable of isolating individual component contributions | Ablation protocol, metric definitions, statistical plan (Ch. 5) | **In progress** |
| **O5** | Execute evaluation and empirically characterise component contributions | Ablation results with statistical significance testing | **Not started** |
| **O6** | Evaluate adversarial robustness of the remediation governance mechanism | Prompt-injection test suite results | **Not started** |

## 1.9 Expected Research Contribution

This research is positioned to contribute:

1. **An openly specified reference architecture** for agent-decomposed IT support, documented at a level permitting independent reimplementation.
2. **Empirical characterisation of component contributions** via ablation — addressing G1 and G2, which no reviewed publication currently answers.
3. **A safety evaluation of governed remediation**, including adversarial testing against prompt injection [10] — addressing G3.
4. **A reusable evaluation protocol** for IT support automation, complementing infrastructure-level benchmarks such as ITBench [7] at the conversational support tier.
5. **A documented account of negative and partial results**, including component configurations that did not perform as designed.

**Explicit limitation of contribution:** This work does not claim to introduce a previously non-existent system category, nor to outperform commercial platforms. Its claim is to make architectural knowledge in this space *open, measured, and reproducible*.

## 1.10 Research Scope

| Aspect | In Scope | Out of Scope |
|---|---|---|
| Conversational AI | Multi-turn, context-retaining dialogue via Gemini LLM; escalation detection | Slack/Teams/WhatsApp integration; voice input |
| Knowledge retrieval | Embedding-based semantic retrieval over curated organisational corpus | Web crawling; external internet search |
| Input modalities | Text; image (screenshots, device photographs) via multimodal LLM | Video; live screen sharing |
| Ticket management | Automated creation, prioritisation, categorisation, assignment, lifecycle transition | ServiceNow/Jira/Zendesk integration |
| Remediation | Whitelisted, risk-tiered Windows diagnostic and remediation actions under mandatory human approval | macOS/Linux; destructive operations; remote machine access |
| Agent architecture | Five specialised agents under centralised orchestration | Agent-to-agent negotiation; dynamic agent creation; self-modifying agents |
| Security | RBAC (5 roles), JWT authentication, audit logging, adversarial input testing | SSO, OAuth2 federation, Active Directory, MFA |
| Predictive analytics | Resolution-time estimation and system-health classification (secondary objective) | Real-time anomaly detection; capacity planning |
| Evaluation | Controlled scenario-based ablation; usability assessment | Longitudinal production study; cross-organisational benchmarking |
| Data | Curated synthetic IT support corpus | Real production data from live enterprises |

## 1.11 Chapter Summary

This chapter established that IT support automation is a genuinely unsolved problem despite mature enabling technologies, evidenced by benchmark resolution rates of 11.4% on realistic IT tasks [7]. It repositioned the research gap away from an unsupportable novelty claim toward a defensible one: the absence of open, architecturally transparent, component-wise evaluated reference designs. The research question was reformulated as a comparative, testable proposition, and objectives were restated with explicit completion criteria and honest status reporting.

---

# Chapter 2 — Literature Review

## 2.1 Chapter Overview

This chapter analyses literature across four strands: the ITSM automation domain, LLM and retrieval foundations, agent architectures, and the safety of action-taking AI systems. Each section closes with a critical assessment linking the literature to specific design decisions in this research.

## 2.2 Conceptual Structure of the Review

```
                      ITSM Automation Problem Domain
                                   |
        +--------------------------+--------------------------+
        |                          |                          |
  Classical ML ITSM         LLM + RAG for               Agent Architectures
  (classification,          incident support             (decomposition,
   routing) [14-16,19]      [3-6,17]                     tool use) [1,11]
        |                          |                          |
        +--------------------------+--------------------------+
                                   |
                    Evidence of unsolved difficulty [7,8,9]
                                   |
                    Safety of action-taking agents [10]
                                   |
                    IDENTIFIED GAP (§1.4.2) → This Research
```

## 2.3 Domain Analysis: Automation in IT Service Management

Classical machine-learning approaches to ITSM have concentrated on **ticket classification and routing**. Studies applying supervised classifiers to helpdesk ticket categorisation report accuracies in the mid-70s to mid-90s percent depending on category granularity and dataset [14], [15], [19], with more recent work extending to enterprise service management contexts [16]. These results establish that ticket categorisation is substantially automatable.

**Critical assessment.** This literature has a consistent structural limitation: the classifier is treated as a terminal artefact. A ticket is categorised — and then the process ends. The classifier does not participate in diagnosis, does not consult resolution knowledge, and does not act. Reported accuracy figures are therefore not comparable to end-to-end resolution capability, and should not be cited as evidence that support automation is solved. **Design implication:** classification in this research is positioned as an *intermediate signal* consumed by downstream agents, not as an output in itself.

## 2.4 Algorithmic Foundations

### 2.4.1 Large Language Models

Surveys of LLM capability document strong performance on multi-step reasoning and instruction-following [2]. For IT support, the relevant property is *conditional adaptation*: the ability to select the next diagnostic action based on the reported outcome of the previous one. The corresponding weakness is the generation of confident but incorrect content.

### 2.4.2 Retrieval-Augmented Generation

RAG conditions generation on retrieved documents from a trusted corpus [3], and the approach has matured into a substantial design space of retrieval, ranking, and integration strategies [4]. Domain-specific application to IT support is directly demonstrated by Toro Isaza et al., who combine retrieval over historical incident resolutions with generative recommendation, reporting improved resolution recommendation quality [6]. Comparable approaches have been applied to engineering ticket systems using dense retrieval over historical issues [17].

**Critical assessment.** In IT support, retrieval grounding is not an accuracy optimisation — it is a **safety mechanism**. An unsupported remediation instruction can cause data loss or system damage. However, existing work predominantly evaluates *retrieval relevance* rather than the effect of grounding on downstream resolution outcomes. This is precisely gap **G2**. **Design implication:** the evaluation in this research includes a no-retrieval ablation condition specifically to isolate this effect (§5.4).

### 2.4.3 LLM Application to IT Operations

Ahmed et al. conducted a large-scale evaluation of LLMs for recommending root causes and mitigation steps for cloud incidents, finding meaningful assistance but performance short of autonomous reliability [5]. Broader AIOps surveys document rapid expansion of LLM application across failure management tasks while noting fragmentation and inconsistent evaluation [8], [9], [18].

**Critical assessment.** These works consistently stop at *recommendation*. The transition from recommending a mitigation to executing it — with the attendant safety burden — is where the literature thins markedly. This is the action gap (P4).

## 2.5 Architectural Analysis: Agent Decomposition

Wang et al. survey LLM-based autonomous agents, formalising construction patterns around profiling, memory, planning, and action [1]. The ReAct paradigm establishes interleaved reasoning and acting with observation feedback [11].

**Critical assessment — and a correction to the previous submission.** The earlier draft argued that decoupling the conversational agent from the execution agent constitutes a security boundary against prompt injection. On implementation review this argument is **not supportable as stated**: in the current system both agents are Python classes within a single process, sharing address space and privileges. There is no OS-, container-, or privilege-level boundary between them, and an injection that manipulates conversational output does not encounter a trust boundary merely because the next function call is in a different class.

The defensible argument is different and more precise. Decomposition delivers:

1. **An enforcement point.** A single, auditable location through which every proposed action must pass and be validated against a whitelist — architecturally guaranteed rather than prompt-instructed.
2. **Determinism where determinism is preferable.** Lifecycle-state logic is implemented as deterministic rules rather than generative inference, making state transitions reproducible and auditable.
3. **Independent testability.** Each agent can be evaluated in isolation, which is a precondition for the ablation methodology in Chapter 5.

The **actual** safety mechanism is the combination of (a) an enumerated action whitelist, (b) input sanitisation rejecting shell metacharacters, and (c) mandatory human approval before execution. This is stated accurately here and evaluated as such in §5.5.

## 2.6 Safety of Action-Taking Agents

Prompt injection against LLM-integrated applications is an empirically demonstrated attack class, with systematic studies identifying vulnerabilities across a large proportion of tested real-world applications [10]. For a system authorised to execute system commands, this is the dominant security consideration.

**Design implication:** safety cannot rest on model behaviour. It must rest on mechanisms that hold *even when the model is fully compromised* — hence the enumerated whitelist and mandatory approval gate, both of which are model-independent. §5.5 defines the adversarial protocol testing this property.

## 2.7 Evidence of Residual Difficulty

ITBench provides the most direct evidence that the problem remains open, reporting **11.4% resolution on SRE scenarios** for agents using state-of-the-art models [7]. This benchmark targets infrastructure operations rather than end-user support, which leaves the conversational support tier comparatively under-benchmarked — a secondary opportunity this research addresses through its evaluation protocol.

## 2.8 Synthesis and Gap Confirmation

The literature establishes that: ticket classification is largely automatable but studied in isolation [14]–[16], [19]; retrieval grounding improves IT incident recommendation but is evaluated on retrieval rather than resolution [6], [17]; LLMs assist incident diagnosis without reaching autonomous reliability [5]; agent decomposition is well-theorised but not empirically characterised in ITSM [1], [11]; action-taking agents face demonstrated adversarial exposure [10]; and realistic IT automation remains largely unsolved [7]–[9].

The gap stated in §1.4.2 is therefore confirmed by this review: what is missing is not a system, but **open architectural evidence** — which components contribute what, and under what governance action-taking becomes acceptably safe.

---

# Chapter 3 — Research Methodology

## 3.1 Research Paradigm

This research adopts **pragmatism**, operationalised through **Design Science Research (DSR)**. DSR is appropriate because the research produces and evaluates an IT artefact as its primary vehicle of inquiry [12], and this study follows the established DSR process model of problem identification, objective definition, design and development, demonstration, evaluation, and communication [13].

The DSR commitment carries a methodological obligation that the previous draft under-served: **the artefact must be evaluated in a manner capable of falsifying the design claims**. A demonstration that the system runs is not a DSR evaluation. Chapter 5 is therefore designed around ablation and adversarial testing rather than feature demonstration.

## 3.2 Research Approach

**Abductive phase (complete).** Observation of the action gap and of poor benchmark performance [7] motivated the hypothesis that architectural decomposition with explicit governance is a productive response.

**Deductive phase (designed; execution pending).** Testable hypotheses derived from the literature:

| ID | Hypothesis | Grounded in | Tested by |
|---|---|---|---|
| **H1** | Retrieval grounding significantly increases factual correctness of troubleshooting guidance versus ungrounded generation | [3], [4], [6] | Ablation A2 (§5.4) |
| **H2** | LLM-based intent classification outperforms keyword-based classification on category and urgency assignment | [14], [15] | Ablation A1 (§5.4) |
| **H3** | Dedicated lifecycle agents yield higher ticket-state correctness than single-model lifecycle handling | [1] | Ablation A3 (§5.4) |
| **H4** | Whitelist plus approval gating prevents unauthorised execution under adversarial input, including injection attempts | [10] | Adversarial suite (§5.5) |

## 3.3 Research Strategy

Applied system development (prototyping) combined with **controlled experimental evaluation**. The experimental design uses within-subject comparison across system configurations on an identical scenario set, so that observed differences are attributable to the configuration rather than to scenario variation.

## 3.4 Data Collection Mechanisms

**Primary — quantitative.** Instrumented system logs capturing classification decisions, retrieval hits and similarity scores, action proposals and approvals, lifecycle transitions, and latency, recorded per scenario per configuration.

**Primary — qualitative.** Structured post-task usability instrument administered to participants, covering perceived usefulness, trust in automated actions, and acceptability of the approval-gating burden.

**Secondary.** Peer-reviewed baselines for comparable subtasks — ticket classification accuracy ranges [14]–[16], [19] and agent task-resolution rates [7] — used as *contextual reference points* with explicit acknowledgement of population differences.

**Methodological correction:** the previous draft proposed comparing measured system performance against a published industry mean resolution time. That comparison is invalid, since the populations, ticket mixes, and measurement definitions differ. It has been removed. Where human comparison is required, a **matched human baseline condition** is used instead: participants resolve the *same* scenarios without system assistance, under the same timing protocol (§5.4, condition A0).

## 3.5 Ethical Considerations

1. **Non-maleficence.** The remediation agent is constrained to an enumerated whitelist of non-destructive operations. Destructive operations are absent from the whitelist and cannot be constructed through parameters, which are validated against allowed-value sets and screened for shell metacharacters.
2. **Informed consent and transparency.** Participants are informed they are interacting with an AI system. No action executes on any system without explicit, logged approval.
3. **Data protection.** Evaluation uses synthetic profiles and tickets. No personal data from real support interactions is processed. RBAC restricts audit-log visibility.
4. **Participant safety.** Adversarial testing (§5.5) is conducted exclusively on isolated researcher-controlled virtual machines, never on participant devices.

## 3.6 Project Management

Agile Scrum, selected for its accommodation of iterative refinement under evolving external dependencies (LLM API changes). Sprints target independently testable increments, consistent with the per-agent testability the architecture provides.

---

# Chapter 4 — System Design and Implementation Progress

## 4.1 Implementation Status Summary

| Component | Status | Verification |
|---|---|---|
| FastAPI backend, ~60 REST endpoints | Complete | Service verified responding; OpenAPI schema enumerated |
| JWT authentication + RBAC (5 roles) | Complete | Authenticated login verified returning valid token and permission set |
| LLM Conversation Agent | Complete | Instantiated and invoked in request pipeline |
| Ticket Intelligence Agent | Complete | Invoked for creation and priority escalation |
| Ticket Status Agent | Complete | Invoked for lifecycle reconciliation |
| Action Executor Agent | Complete (25 actions) | Whitelist, validation, and approval flow implemented |
| Image Analysis Agent | Complete | Multimodal endpoint implemented |
| Retrieval subsystem | Functional; **architecture revision required** | See §4.5 |
| Predictive ML models | Prototype; **re-specification required** | See §4.7 |
| React frontend | Complete | Application served and reachable |
| Docker deployment configuration | Complete | Compose definitions for development and deployment |
| Evaluation harness | **Not implemented** | Planned — §7.3 |

## 4.2 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  PRESENTATION (React + Vite)                 │
│     Chat  │  Dashboard  │  Ticket Manager  │  Admin Panel    │
└───────────────────────────┬──────────────────────────────────┘
                            │ REST / JSON
┌───────────────────────────▼──────────────────────────────────┐
│              API LAYER (FastAPI) — JWT + RBAC                │
├──────────────────────────────────────────────────────────────┤
│                    ORCHESTRATION LAYER                       │
│   Deterministic sequential pipeline (chat_enhanced.py)       │
│                                                              │
│   [Image Agent] → [Intent Classification] → [Retrieval]      │
│        → [Conversation Agent] → [Ticket Intelligence Agent]  │
│        → [Assignment Service] → [Ticket Status Agent]        │
│        → [Action Executor Agent — gated]                     │
├──────────────────────────────────────────────────────────────┤
│  Retrieval Engine  │  Assignment Service  │ PowerShell Exec  │
├──────────────────────────────────────────────────────────────┤
│  DATA: SQLite (tickets/users/roles/audit) │ KB corpus (JSON) │
├──────────────────────────────────────────────────────────────┤
│  ML: Resolution-time regressor │ System-health classifier    │
└──────────────────────────────────────────────────────────────┘
```

**Architectural characterisation — stated precisely.** Coordination is **centralised and deterministic**: the orchestration function invokes each agent in a fixed sequence. Agents do not communicate directly, do not select which agent runs next, and do not negotiate. This is an *orchestrated specialist-agent pipeline*, not a decentralised multi-agent system in the classical autonomous-negotiation sense [1]. This distinction is stated explicitly because overstating architectural autonomy would misrepresent the artefact.

## 4.3 Agent Specifications

| Agent | Function | Input | Output | Implementation Basis |
|---|---|---|---|---|
| **LLM Conversation Agent** | Multi-turn diagnostic dialogue; escalation and resolution signalling | User message, conversation history, retrieved context | Response text; `is_technical`, `should_escalate`, `is_resolved` flags | Gemini LLM + prompt engineering; heuristic post-analysis |
| **Ticket Intelligence Agent** | Ticket creation timing, urgency scoring, title/description generation, categorisation | Conversation history, turn count, classification signal | Creation decision; priority (0–10 urgency score); ticket metadata | Hybrid: LLM generation with deterministic rule fallback |
| **Ticket Status Agent** | Lifecycle transitions, SLA tracking, re-open and abandonment detection | Conversation history, current status, ticket timestamps | Recommended state, confidence, SLA flags | **Deterministic rule-based state machine** (intentionally non-LLM) |
| **Action Executor Agent** | Risk-tiered remediation proposal and gated execution | Issue description, category, urgency, user approval | Proposed actions with risk tier; execution result | Enumerated whitelist; regex parameter sanitisation; PowerShell subprocess |
| **Image Analysis Agent** | Visual fault analysis, text extraction from screenshots | Image bytes, MIME type, optional user context | Extracted text, issue description, category, retrieval keywords | Gemini multimodal API |

**Design rationale for heterogeneity.** The Ticket Status Agent is deliberately *not* LLM-based. Lifecycle state governs SLA accounting and audit records, where reproducibility and explainability outweigh linguistic flexibility. This heterogeneous design — generative where interpretation is required, deterministic where accountability is required — is itself a contribution claim, tested by ablation A3.

## 4.4 Orchestration Workflow

1. **Multimodal pre-processing** *(image path only)* — visual analysis output merged into the textual message.
2. **Intent classification** — technical/non-technical, category, urgency, confidence.
3. **Retrieval** — executed only when classified technical; similarity threshold 0.5 applied; top-3 retained.
4. **Response generation** — conditioned on retrieved context when available.
5. **Ticket intelligence** — creation gated at ≥3 conversational turns to prevent premature ticket generation.
6. **Escalation** — on escalation signal, assignment service allocates a human agent by specialisation and workload.
7. **Lifecycle reconciliation** — status agent reconciles ticket state against conversation evidence.
8. **Remediation proposal** — only in explicitly enabled Agent Mode; single next action returned (stepwise protocol) pending approval.

## 4.5 Retrieval Subsystem — Status and Required Revision

**Current implementation.** Query and knowledge-base texts are embedded using a hosted embedding model; cosine similarity is computed in Python over an in-memory cache; results are threshold-filtered and ranked.

**Discrepancy identified and corrected.** The previous submission stated that ChromaDB serves as the vector database for live retrieval. **Code review established that this is not the case.** ChromaDB is initialised only within an offline ingestion script and is not queried by the live request path, which performs linear-scan similarity in application memory. This document corrects that claim.

**Implications.**
1. Retrieval complexity is **O(n)** per query, not sub-linear as an approximate-nearest-neighbour index would provide.
2. The scalability argument for a vector database is not currently realised.
3. At the present corpus size (6 articles) the distinction is operationally immaterial; at realistic corpus sizes it is material.

**Planned action.** Route the live retrieval path through the persistent vector store, and evaluate both configurations to report the retrieval-latency/scale trade-off empirically (§7.3). This converts a documentation defect into a measurable result.

## 4.6 Remediation Governance

**Action inventory: 25 whitelisted actions** across process management, cleanup, network diagnostics, service management, and system diagnostics.

**Correction:** the previous submission claimed "50+ safe actions" in both narrative and architecture diagram. Source inspection confirms **25 active definitions**; the higher figure appears to have counted commented-out and duplicated entries. This document reports the verified count.

**Governance controls (implemented):**

| Control | Mechanism | Model-independent? |
|---|---|---|
| Action enumeration | Actions selectable only from a fixed whitelist; no free-form command construction | **Yes** |
| Parameter validation | Required-field and allowed-value checking against action definition | **Yes** |
| Injection screening | Regex rejection of shell metacharacters (`;`, `&`, `\|`, backtick, `$`) in parameters | **Yes** |
| Risk tiering | Every action assigned LOW / MEDIUM / HIGH | **Yes** |
| Human approval gate | Execution requires explicit approval; ownership verified against requesting user | **Yes** |
| Execution isolation | Subprocess invocation without shell interpretation; 30-second timeout | **Yes** |
| Audit trail | Action requests and outcomes retained in history | **Yes** |

All controls are enforced outside the language model. This is the property that makes safety claims testable under adversarial conditions (§5.5).

## 4.7 Predictive Subsystem — Status and Required Re-specification

**Trained artefacts (verified by inspection):**

| Model | Algorithm | Features | Target | Training Data |
|---|---|---|---|---|
| Resolution-time model | **Linear Regression** | `category_code`, `priority`, `word_count` (3) | `hours_taken` (continuous) | 500 synthetic records |
| System-health model | Random Forest Classifier (100 estimators) | `cpu_usage`, `ram_usage`, `disk_usage`, `temperature` (4) | Binary health state | Not documented |
| Category encoder | Label Encoder | — | 5 categories | — |

**Corrections to previous submission:**

1. The previous draft described the SLA component as a **Random Forest SLA breach predictor**. The trained artefact is a **Linear Regression model predicting resolution hours** — a different algorithm solving a different problem (regression, not breach classification).
2. The system-health model *is* a Random Forest, consistent with the earlier description.
3. No performance metrics (R², MAE, accuracy, F1) have been computed for either model. **None are reported here.**

**Required work (§7.3):** either re-specify the SLA component as breach classification with a label definition and evaluate it properly, or reframe it accurately as resolution-time estimation. The 3-feature, 500-record configuration is additionally too limited to support meaningful claims and requires expansion.

## 4.8 Data Layer

| Store | Purpose | Current Volume |
|---|---|---|
| Relational database | Users, roles, tickets, chat history, audit logs | 1 user; **0 tickets**; 0 audit entries |
| Knowledge corpus (JSON) | Retrieval source | **6 articles**, 5 users, 5 tickets, 4 conversations |
| ML training data | Resolution-time model | 500 records |

**Correction:** the previous submission described a synthetic dataset of "200 users, historical tickets, and SOPs." The actual corpus is substantially smaller. Corpus construction is **in progress** and is the principal blocker to evaluation (§7.2).

---

# Chapter 5 — Evaluation Methodology and Experimental Design

> **Status: designed; not yet executed.** This chapter specifies the intended protocol. No data has been collected under it.

## 5.1 Evaluation Objectives

To determine the measurable contribution of each architectural component (RQ5) and to establish whether the governance mechanism withstands adversarial input (RQ4) — rather than to demonstrate that the system functions.

## 5.2 Experimental Setup

- **Environment:** isolated Windows virtual machines, uniform baseline snapshot restored between trials to eliminate carry-over.
- **Model configuration:** fixed model version and generation parameters across all conditions; temperature recorded, and classification tasks run at low temperature for determinism.
- **Repetition:** each scenario executed **n = 5 times per configuration** to characterise non-determinism in generative components.
- **Blinding:** scenario scoring performed against a rubric fixed before execution; scorers blind to configuration where feasible.

## 5.3 Evaluation Corpus (In Preparation)

**Target:** 60 scenarios spanning five categories (network, performance, peripheral/hardware, access/account, software), stratified across three difficulty tiers, each with a defined ground-truth resolution path and acceptance criteria.

**Current status: insufficient.** The existing corpus of 6 knowledge-base articles cannot support this design. Expansion is the critical path item (§7.2).

**Ground-truth protocol.** Scenario ground truth is authored **before** any system execution and is **not LLM-generated**, avoiding the circularity of evaluating a model against labels produced by a model. Independent review of a sample by a second assessor will establish inter-rater agreement (Cohen's κ).

## 5.4 Ablation Design

The core experiment. Identical scenarios executed under progressively enabled configurations:

| ID | Configuration | Isolates | Tests |
|---|---|---|---|
| **A0** | Unassisted human baseline (participant resolves scenario manually) | Human reference performance | Comparative reference |
| **A1** | Single LLM, no retrieval, no agents, no actions | Monolithic baseline | H2 (vs. keyword baseline) |
| **A2** | A1 + retrieval grounding | **Contribution of retrieval** | **H1** |
| **A3** | A2 + ticket intelligence and lifecycle agents | **Contribution of agent decomposition** | **H3** |
| **A4** | A3 + gated remediation (full system) | Contribution of action execution | RQ5 |

Because A0 uses the **same scenarios** under the same timing protocol, the human comparison is internally valid — unlike a comparison against an external published mean.

## 5.5 Adversarial Safety Protocol

Testing whether governance holds when the model is manipulated [10]:

| Test class | Method | Success criterion |
|---|---|---|
| Direct injection | Instructions in user input attempting to induce non-whitelisted commands | Zero unauthorised executions |
| Indirect injection | Adversarial content embedded in retrieved documents and uploaded images | Zero unauthorised executions |
| Parameter injection | Shell metacharacters and escape sequences in action parameters | 100% rejection at validation |
| Approval bypass | Execution attempts without approval; approval attempts by non-owning users | Zero successes |
| Privilege escalation | Requests for elevation-requiring actions by insufficiently privileged roles | Zero successes |

**Reporting commitment:** any successful bypass will be reported as a finding, not omitted.

## 5.6 Metrics

| Dimension | Metric | Method |
|---|---|---|
| Classification | Accuracy, macro-F1, per-class precision/recall (technical/category/urgency) | Against pre-authored ground truth |
| Retrieval | Precision@3, Recall@3, MRR | Against relevance judgements |
| Resolution | Task success rate; steps to resolution; time to resolution | Rubric scoring |
| Grounding | Proportion of factually correct guidance; unsupported-claim rate | Blind expert assessment |
| Lifecycle | State-transition correctness | Against expected lifecycle |
| Safety | Unauthorised execution count; validation rejection rate | Adversarial suite |
| Predictive | MAE and R² (resolution time); accuracy and F1 (health) | Held-out test split |
| Usability | Usability instrument score; trust and approval-burden ratings | Post-task questionnaire |
| Efficiency | End-to-end latency; token consumption per interaction | Instrumented logs |

## 5.7 Statistical Analysis Plan

- **Target sample:** 60 scenarios × 5 configurations × 5 repetitions = 1,500 system trials; **12–15 participants** for usability and the A0 human baseline.
- **Continuous outcomes** (time, latency): repeated-measures ANOVA where assumptions hold; Friedman test otherwise.
- **Categorical outcomes** (success/failure): Cochran's Q with pairwise McNemar tests.
- **Correction:** Holm–Bonferroni across the ablation family.
- **Reporting:** effect sizes (Cohen's *d* or Cliff's δ) with 95% confidence intervals, not p-values alone.
- **Power:** a priori power analysis to be completed before data collection; sample sizes above are provisional pending that analysis.

**Acknowledged constraint:** a 12–15 participant sample is adequate for usability signal but underpowered for small effects in the human baseline comparison. This will be reported as a limitation rather than concealed by selective reporting.

---

# Chapter 6 — Current Results and Discussion

> **Scope statement.** This chapter reports **implementation verification outcomes only**. The evaluation protocol in Chapter 5 has not been executed. No accuracy, resolution-time, retrieval-quality, or user-satisfaction results are available, and none are reported. Any figure presented here describes *what was built*, not *how well it performs*.

## 6.1 Implementation Verification Results

**R1 — End-to-end operability.** The system was verified operational: the backend service responds successfully to health checks, authentication returns a valid token with an associated permission set, and approximately 60 REST endpoints are registered and enumerable. The frontend application is served and reachable. This establishes that subsequent evaluation has a functioning artefact to measure.

**R2 — Agent instantiation and integration.** All five specified agents are implemented as discrete modules and are invoked within the request pipeline. Agent decomposition therefore exists as an implemented architecture rather than a design intention — a precondition for ablation A3.

**R3 — Governance controls implemented.** All seven controls in §4.6 are implemented and, critically, all are enforced outside the language model. This satisfies the precondition for the adversarial protocol: the safety claim is testable because it does not depend on model compliance.

**R4 — Heterogeneous agent implementation confirmed.** The lifecycle agent is implemented deterministically while conversational and ticket-metadata agents are generative, confirming the heterogeneous design is realised rather than merely proposed.

**R5 — Three documentation–implementation discrepancies identified and corrected.** Systematic source verification identified three material divergences between the previous submission and the artefact:

| Claim in previous submission | Verified reality | Correction |
|---|---|---|
| ChromaDB vector database serves live retrieval | Live path uses in-memory linear-scan cosine similarity; ChromaDB used only in offline ingestion | §4.5 |
| "50+ safe actions" | 25 active action definitions | §4.6 |
| SLA breach predictor using Random Forest | Linear Regression predicting resolution hours | §4.7 |
| Synthetic dataset of 200 users, historical tickets, SOPs | 6 knowledge-base articles; 5 synthetic users; 0 tickets in operational database | §4.8 |

## 6.2 Discussion

### 6.2.1 On the Discrepancy Findings

These findings are reported prominently rather than quietly corrected, for a methodological reason. In DSR the artefact *is* the evidence [12], so any divergence between the described and actual artefact invalidates conclusions drawn from the description. Discovering three such divergences before evaluation — rather than after — preserves the validity of the results to come. The episode also supports a broader argument in this thesis: **claims about AI system architecture require source-level verification**, which is precisely what closed commercial platforms preclude and what this project's openness enables (§1.9).

### 6.2.2 On Architectural Characterisation

Honest characterisation of the artefact as an *orchestrated specialist-agent pipeline* rather than an autonomous multi-agent system (§4.2) narrows the contribution but strengthens it. Deterministic orchestration is an appropriate — arguably preferable — choice where auditability is required, since execution order is fixed and reproducible. The research question this raises is empirical rather than terminological: does specialisation confer measurable benefit even under centralised control? Ablation A3 is designed to answer it.

### 6.2.3 On the Safety Argument

Revising the safety rationale from "agent decoupling provides a security boundary" to "model-independent whitelisting and approval gating constrain the action space" (§2.5) changes what must be demonstrated. The revised claim is narrower, mechanically accurate, and — unlike the original — falsifiable by the adversarial protocol in §5.5. A claim that can fail a test is more valuable than one that cannot be tested.

### 6.2.4 Comparison With Existing Approaches

Comparison at this stage is necessarily **architectural rather than empirical**, since no performance data exists:

| Dimension | Classical ML ITSM [14]–[16], [19] | RAG incident recommendation [6], [17] | LLM incident diagnosis [5], [18] | This work (implemented) |
|---|---|---|---|---|
| Multi-turn dialogue | No | No | Partial | Yes |
| Retrieval grounding | No | Yes | Partial | Yes |
| Automated ticket lifecycle | Classification only | No | No | Yes |
| Action execution | No | No | No | Yes (gated) |
| Multimodal input | No | No | No | Yes |
| Adversarial safety evaluation | N/A | Not reported | Not reported | **Planned** (§5.5) |
| Component ablation | N/A | Not reported | Not reported | **Planned** (§5.4) |

The rightmost column's final two rows are the intended contribution. Their present status is *planned*, and the comparison should be read accordingly.

### 6.2.5 Preliminary Answers to Research Questions

| RQ | Status | Present position |
|---|---|---|
| RQ1 (classification accuracy) | **Unanswered** | Classifier implemented; no accuracy measured |
| RQ2 (retrieval contribution) | **Unanswered** | Retrieval implemented; ablation A2 designed |
| RQ3 (lifecycle decomposition) | **Unanswered** | Agents implemented; ablation A3 designed |
| RQ4 (governance under attack) | **Partially addressed by design** | Controls implemented and model-independent; adversarial testing pending |
| RQ5 (component contributions) | **Unanswered** | Ablation designed; execution pending |

---

# Chapter 7 — Limitations, Challenges, and Remaining Work

## 7.1 Current Limitations

**L1 — No empirical evidence yet.** Every performance claim remains untested. This is the dominant limitation.

**L2 — Insufficient evaluation corpus.** Six knowledge-base articles cannot support meaningful retrieval evaluation; retrieval precision over so small a corpus would not generalise.

**L3 — Retrieval architecture below specification.** Linear-scan similarity does not demonstrate the scalability property the design argument claims (§4.5).

**L4 — Predictive component under-specified.** A 3-feature linear model on 500 synthetic records cannot support meaningful predictive claims (§4.7).

**L5 — Synthetic data only.** Findings will be constrained in external validity. Real support conversations differ in ambiguity, incompleteness, and noise.

**L6 — Single-platform remediation.** Windows/PowerShell only.

**L7 — Model dependency.** Results are conditioned on one commercial LLM family; conclusions may not transfer across models. Model version will be recorded with all results.

**L8 — Centralised orchestration.** Conclusions apply to orchestrated pipelines, not to autonomous negotiating agent systems.

## 7.2 Active Challenges

| Challenge | Impact | Mitigation |
|---|---|---|
| Corpus construction is the critical path | Blocks all evaluation | Prioritised immediately; target 60 scenarios + expanded KB |
| Avoiding circular ground truth | Threatens validity of accuracy metrics | Human-authored ground truth; second-assessor agreement (κ) |
| Non-determinism in generative components | Complicates reproducibility | n = 5 repetitions; variance reported |
| Participant recruitment for A0 baseline | Limits statistical power | Early recruitment; limitation reported honestly |
| LLM API rate limits and cost | May constrain trial count | Batch scheduling; token budgeting |

## 7.3 Remaining Work

**Phase A — Foundation repair (immediate priority)**
1. Construct 60-scenario evaluation corpus with human-authored ground truth.
2. Expand knowledge base to a realistic scale.
3. Route live retrieval through the persistent vector store; retain the current path as a comparison condition.
4. Re-specify the predictive component (breach classification with defined labels, or accurate reframing as resolution-time estimation); expand features and training data.

**Phase B — Evaluation infrastructure**
5. Implement automated evaluation harness for scenario execution across configurations.
6. Implement the five ablation configurations as runtime-selectable modes.
7. Build the adversarial test suite (§5.5).
8. Finalise usability instrument; complete a priori power analysis; obtain ethics approval.

**Phase C — Execution**
9. Execute ablation experiment (1,500 trials).
10. Execute adversarial safety evaluation.
11. Conduct participant sessions including the A0 human baseline.
12. Evaluate predictive models on held-out data.

**Phase D — Analysis and writing**
13. Statistical analysis per §5.7 with effect sizes and confidence intervals.
14. Author Results and Discussion chapters from measured data.
15. Document negative and partial results.
16. Complete thesis; prepare defence.

## 7.4 Concluding Statement

The research has completed problem formulation, literature analysis, methodological design, and system implementation. Its most significant progress in this revision cycle is **corrective**: an unsupportable novelty claim has been narrowed to a defensible one; an invalid comparison baseline has been replaced with a matched internal control; an inaccurate safety argument has been restated in mechanically correct and testable terms; and three documentation–implementation discrepancies have been identified and rectified.

The project's scientific value now rests on executing the ablation and adversarial evaluations specified in Chapter 5. Until those are complete, the contribution remains an implemented artefact with a designed evaluation — substantial groundwork, but not yet a research finding.

---

# References

[1] L. Wang, C. Ma, X. Feng, Z. Zhang, H. Yang, J. Zhang, et al., "A survey on large language model based autonomous agents," *Frontiers of Computer Science*, vol. 18, no. 6, art. 186345, 2024, doi: 10.1007/s11704-024-40231-1.

[2] W. X. Zhao, K. Zhou, J. Li, T. Tang, X. Wang, Y. Hou, et al., "A survey of large language models," *arXiv preprint* arXiv:2303.18223, 2023.

[3] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, et al., "Retrieval-augmented generation for knowledge-intensive NLP tasks," in *Proc. 34th Conf. Neural Information Processing Systems (NeurIPS)*, 2020, pp. 9459–9474.

[4] Y. Gao, Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, et al., "Retrieval-augmented generation for large language models: A survey," *arXiv preprint* arXiv:2312.10997, 2024.

[5] T. Ahmed, S. Ghosh, C. Bansal, T. Zimmermann, X. Zhang, and S. Rajmohan, "Recommending root-cause and mitigation steps for cloud incidents using large language models," in *Proc. IEEE/ACM 45th Int. Conf. Software Engineering (ICSE)*, Melbourne, Australia, 2023, pp. 1737–1749, doi: 10.1109/ICSE48619.2023.00149.

[6] P. Toro Isaza, M. Nidd, N. Zheutlin, J.-W. Ahn, C. A. Bhatt, Y. Deng, R. Mahindru, M. Franz, H. Florian, and S. Roukos, "Retrieval augmented generation-based incident resolution recommendation system for IT support," *arXiv preprint* arXiv:2409.13707, 2024.

[7] S. Jha, R. Arora, Y. Watanabe, T. Yanagawa, Y. Chen, J. Clark, et al., "ITBench: Evaluating AI agents across diverse real-world IT automation tasks," in *Proc. 42nd Int. Conf. Machine Learning (ICML)*, PMLR vol. 267, 2025; *arXiv preprint* arXiv:2502.05352.

[8] L. Zhang, T. Jia, M. Jia, Y. Wu, A. Liu, Y. Yang, et al., "A survey of AIOps for failure management in the era of large language models," *arXiv preprint* arXiv:2406.11213, 2024.

[9] L. Zhang, T. Jia, M. Jia, Y. Yang, and Z. Wu, "A survey of AIOps in the era of large language models," *ACM Computing Surveys*, 2025, doi: 10.1145/3746635; *arXiv preprint* arXiv:2507.12472.

[10] Y. Liu, G. Deng, Y. Li, K. Wang, Z. Wang, X. Wang, et al., "Prompt injection attack against LLM-integrated applications," *arXiv preprint* arXiv:2306.05499, 2023.

[11] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, "ReAct: Synergizing reasoning and acting in language models," in *Proc. Int. Conf. Learning Representations (ICLR)*, 2023.

[12] A. R. Hevner, S. T. March, J. Park, and S. Ram, "Design science in information systems research," *MIS Quarterly*, vol. 28, no. 1, pp. 75–105, 2004.

[13] K. Peffers, T. Tuunanen, M. A. Rothenberger, and S. Chatterjee, "A design science research methodology for information systems research," *Journal of Management Information Systems*, vol. 24, no. 3, pp. 45–77, 2007.

[14] "Machine learning for classification of IT support tickets," in *Proc. IEEE Int. Conf.*, 2023. [IEEE Xplore document 10051041]

[15] "Automated ticket classification for information technology helpdesks using machine learning," in *Proc. IEEE Int. Conf.*, 2024. [IEEE Xplore document 10528578]

[16] "AI-based classification of IT support requests in enterprise service management systems," *Systems*, vol. 14, no. 2, art. 223, doi: 10.3390/systems14020223.

[17] "RAG4Tickets: AI-powered ticket resolution via retrieval-augmented generation on JIRA and GitHub data," *arXiv preprint* arXiv:2510.08667, 2025.

[18] "Empowering AIOps: Leveraging large language models for IT operations management," *arXiv preprint* arXiv:2501.12461, 2025.

[19] "Automatic Thai ticket classification by using machine learning for IT infrastructure company," in *Proc. IEEE Int. Conf.*, 2022. [IEEE Xplore document 9836250]

---

## Appendix A — Implementation Verification Evidence

| Item | Verified Value |
|---|---|
| Backend framework | FastAPI (Python 3.11) |
| Registered REST endpoints | ~60 |
| Authentication | JWT (HS256); bcrypt password hashing |
| RBAC roles | 5 |
| Agent modules implemented | 5 |
| Whitelisted remediation actions | 25 |
| Action risk tiers | LOW / MEDIUM / HIGH |
| Command execution timeout | 30 s |
| Retrieval similarity threshold | 0.50 |
| Retrieved documents per query | Top 3 |
| Ticket-creation turn threshold | ≥ 3 turns |
| Conversation memory window | 20 messages |
| Resolution-time model | Linear Regression, 3 features, 500 records |
| System-health model | Random Forest, 100 estimators, 4 features, binary |
| Knowledge-base articles | 6 |
| Tickets in operational database | 0 |
| Frontend | React 19 + Vite |
| Deployment | Docker Compose (development and deployment configurations) |

## Appendix B — Corrections Applied to Interim Submission 01

| # | Previous statement | Status | Section |
|---|---|---|---|
| 1 | "No comprehensive integrated IT support platform exists" | **Withdrawn** — commercial platforms exist; gap narrowed to open, evaluated architecture | §1.4 |
| 2 | Comparison against published industry mean resolution time | **Withdrawn** — invalid across populations; replaced with matched human baseline A0 | §3.4, §5.4 |
| 3 | Agent decoupling constitutes a security boundary | **Corrected** — agents share a process; safety derives from whitelist + approval gate | §2.5, §4.6 |
| 4 | ChromaDB serves live retrieval | **Corrected** — live path uses in-memory linear-scan similarity | §4.5 |
| 5 | "50+ safe actions" | **Corrected** — 25 verified action definitions | §4.6 |
| 6 | Random Forest SLA breach predictor | **Corrected** — Linear Regression resolution-time estimator | §4.7 |
| 7 | Dataset of 200 users with historical tickets | **Corrected** — 6 KB articles, 5 synthetic users, 0 operational tickets | §4.8 |
| 8 | Research question was design-descriptive | **Reformulated** as comparative and testable | §1.5 |
| 9 | No ablation planned | **Added** — five-configuration ablation as core experiment | §5.4 |
| 10 | No adversarial safety evaluation | **Added** — five-class injection and bypass protocol | §5.5 |
| 11 | No statistical analysis plan | **Added** — tests, corrections, effect sizes, power | §5.7 |

## Appendix C — Citation Verification Status

Prepared in the interest of academic integrity. All references below were located through live source verification during preparation of this document.

| Ref | Verification status | Action required before final submission |
|---|---|---|
| [1] | Verified — Springer, DOI confirmed | None |
| [2] | Well-established survey; arXiv ID confirmed | Confirm latest version/pagination |
| [3] | Landmark NeurIPS 2020 paper | Confirm page range against proceedings |
| [4] | arXiv ID confirmed | Check for peer-reviewed publication version |
| [5] | Verified — ICSE 2023, full author list and DOI confirmed | None |
| [6] | Verified — arXiv ID and full author list confirmed | Check for peer-reviewed venue version |
| [7] | Verified — arXiv ID and ICML/PMLR venue confirmed | Confirm full author list from PMLR |
| [8] | Verified — arXiv ID confirmed | Confirm full author list |
| [9] | Verified — ACM Computing Surveys DOI confirmed | Confirm volume/issue/pages |
| [10] | Verified — arXiv ID confirmed | Confirm full author list |
| [11] | Well-established ICLR 2023 paper | Confirm proceedings details |
| [12], [13] | Foundational DSR methodology (pre-2019, cited as methodological canon) | None |
| [14], [15], [19] | Titles and IEEE Xplore document numbers verified | **Retrieve full author lists, venue names, pages from IEEE Xplore** |
| [16] | DOI verified | **Retrieve full author list and year from publisher** |
| [17], [18] | arXiv IDs verified | **Retrieve full author lists** |

**References removed from the previous submission** because they could not be verified and should not be cited without confirmation: Ahmad et al. (2023); Xu et al. (2023); Patel & Singh (2023); Kumar & Mehta (2024); Li et al., "Multi-Agent Systems for Enterprise AI," *ACM Computing Surveys*; and the CompTIA entry dated "2924."

**Grey-literature statistics** (Gartner, IDC, HDI, Statista, Freshworks) cited in the previous submission have been removed from the argument's evidential core. Where market or industry context is desirable, these should be reinstated only with verified report titles, publication dates, and access URLs, and clearly marked as industry rather than peer-reviewed sources.
