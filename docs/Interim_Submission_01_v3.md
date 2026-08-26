# INTERIM SUBMISSION 01

**Research Title**

> **Context-Aware Intelligent IT Support: A Multi-Agent LLM Framework with Knowledge-Grounded Troubleshooting and Human-Gated Automated Remediation**

**Student:** P. T. N. Pathirana (28647)
**Institution:** NSBM Green University Town
**Submission:** Interim Submission 01 — Revision 3
**Date:** 18 August 2026
**Supersedes:** Interim Submission 01 (28 June 2026) and Revision 2 (18 August 2026)

---

## Declaration of Current Research Status

Academic integrity requires that a progress document distinguish what has been *done* from what has been *designed* and what remains *planned*. This submission makes that distinction explicit throughout. **No performance result is reported that has not been empirically measured.** Where a number appears, it describes either the artefact that was built (verified by source inspection) or a target defined in the evaluation design — never an unmeasured outcome.

| Research phase | Status | Evidence in this document |
|---|---|---|
| Problem identification and justification | **Complete** | Chapter 1 |
| Structured literature review and gap identification | **Complete** | Chapter 2 |
| Methodology definition | **Complete** | Chapter 3 |
| System architecture design | **Complete** | Chapter 4 |
| Core implementation (5 agents, API, frontend, RBAC, remediation governance) | **Complete; verified operational** | Chapter 4, Appendix A |
| Retrieval (RAG) subsystem | **Functionally complete; architecture revision required** | §4.6, §7.1 |
| Predictive ML subsystem | **Prototype trained; re-specification required** | §4.8, §7.1 |
| Evaluation instrument and protocol design | **Complete in design; harness not implemented** | Chapter 5 |
| Evaluation corpus construction | **In progress — currently insufficient** | §5.3, §6.4 |
| Empirical evaluation execution | **Not started** | §6.5 |
| Results chapter | **Not started — structure defined only** | §6.7 |
| Discussion chapter | **Not started — structure defined only** | §6.8 |

**Critical statement.** At the time of submission the curated corpus contains **6 knowledge-base articles, 5 synthetic users, 5 sample tickets and 4 sample conversations**, and the operational databases contain **0 processed tickets and 0 audit entries**. **No empirical performance results exist.** Chapter 6 therefore reports *implementation verification outcomes* and a *progress position* only, and explicitly does not report resolution-time, accuracy, retrieval-quality or user-satisfaction findings. Those remain planned work (§6.9, §7.3).

---

## Compliance Mapping — "Detailed and Elaboratory Thesis Chapter Breakdown v1.1"

Provided so that conformance to the prescribed structure can be checked directly.

| v1.1 requirement | Section in this document |
|---|---|
| 1.1 Chapter Overview | §1.1 |
| 1.2 Problem Background — "what has actually happened" | §1.2 (expanded to §1.2.1–§1.2.6) |
| 1.3 Problem Statement — focused, recent citations, statistics | §1.3 |
| 1.3.1 General Problem — high-level implication | §1.3.1 |
| 1.3.2 Specific Problem — domain shortcomings, ending on the gap | §1.3.2, §1.3.3 |
| 1.4 Research Question — 'Wh' form, one primary with sub-questions | §1.4 |
| 1.5 Research Motivation | §1.5 |
| 1.6 Research Aim | §1.6 |
| 1.7 Research Objectives — identify / analyse / design / evaluate | §1.7 |
| 1.8 Rich picture of the proposed solution | §1.8 |
| 1.9 Resource Requirements (hardware, software) | §1.9 |
| 1.10 Project Scope — in-scope / out-of-scope table | §1.10 |
| 1.11 Chapter Summary | §1.13 |
| *(Supervisor addition)* Significance of the research | §1.11 |
| *(Supervisor addition)* Thesis structure | §1.12 |
| 2.1 Chapter Overview | §2.1 |
| 2.2 Conceptual Map of the literature | §2.2 |
| 2.3 Domain Overview (~10%) | §2.3 |
| 2.4 Existing Systems / Frameworks / Designs (~30%), comparative with justification | §2.4 |
| 2.5 Technological Analysis (~60%): algorithmic, design, workflow | §2.5–§2.7 |
| 2.6 Reflection — gap justified from literature <5 years old | §2.8, §2.9 |
| 3.1 Research Paradigm | §3.2 |
| 3.2 Research Approach | §3.3 |
| 3.3 Research Strategy | §3.4 (research design), §3.5 (strategy) |
| 3.4 Fact Collection Mechanisms | §3.6 (methods), §3.7 (sources) |
| 3.5 Research Methodology Execution Workflow (tabular) | §3.8 |
| 3.6 Project Management Methodology | §3.11 |
| 3.6.1 Project Timeline | §3.12 |
| 3.6.2 Ethical Considerations | §3.13 |
| 3.7 Chapter Summary | §3.15 |

---

# Chapter 1 — Introduction

## 1.1 Chapter Overview

This chapter establishes the research foundation for a multi-agent, LLM-based IT support framework with knowledge-grounded troubleshooting and human-gated remediation. It begins with the broader research context of IT Service Management (ITSM) and the empirical evidence that generative AI now materially affects support work (§1.2). It then narrows through the current situation and its documented shortcomings, to the specific technical opening created by large language models (LLMs), retrieval-augmented generation (RAG) and agent architectures, and to the published evidence that — despite those enabling technologies — the task is *not* solved. From that evidence base the chapter derives a problem statement (§1.3), a comparative and testable research question (§1.4), the motivation (§1.5), aim (§1.6) and objectives (§1.7) of the study. A rich picture of the proposed solution (§1.8), the resource requirements (§1.9), the scope boundary (§1.10), the significance of the work (§1.11) and the structure of the thesis (§1.12) complete the chapter.

**A note on what changed in this revision.** Two claims made in the June 2026 submission are withdrawn here because they are not defensible. First, the claim that *no* integrated LLM-based IT support platform exists: commercial ITSM platforms already combine conversational AI with ticket automation, and recent peer-reviewed work — notably an enterprise deployment of desktop-resident agents performing consent-governed remediation [1] — occupies part of the same design space. Second, the intention to compare measured system performance against a published industry mean resolution time drawn from a different population. Both are replaced with claims this research can actually substantiate. The novelty claim is narrowed to what the literature genuinely lacks: an **openly specified, architecturally transparent, component-wise ablated reference design** for agent-decomposed IT support with governed remediation. This narrowing is deliberate; overstating a contribution is a more serious defect in a thesis than making a modest one.

## 1.2 Problem Background

### 1.2.1 The Broader Research Context

Organisational productivity now depends on IT infrastructure that is heterogeneous by construction — cloud services, on-premises systems, diverse endpoints and layered software stacks — and the support function that keeps this infrastructure usable has become a bottleneck of organisational rather than merely technical significance. The relevance of automating that function is no longer speculative. In the largest field study of generative AI in a support setting to date, Brynjolfsson, Li and Raymond observed the staged rollout of a generative-AI conversational assistant to more than five thousand customer-support agents and measured a productivity increase of approximately 14% in issues resolved per hour, with the largest gains accruing to the least experienced and least skilled workers [2]. Two features of that result matter for the present research. First, the improvement is attributed to the diffusion of *tacit knowledge* held by high performers into the working practice of everyone else — that is, to knowledge access rather than to raw generative fluency. Second, it was obtained with an assistant that *recommends*, not one that *acts*.

This is the empirical anchor for the research: assistance that improves knowledge access measurably improves support work, which makes the design of that assistance — how knowledge is retrieved, how advice is grounded, and whether the system may act on it — a question with demonstrated practical stakes rather than an assumed one.

### 1.2.2 The Current Situation

Enterprise IT support is delivered through tiered human workflows (L1 → L2 → L3) mediated by ticketing systems. This arrangement controls cost but imposes queuing delay and repeated context-gathering at each handoff. A substantial fraction of the workload is repetitive: credential and access problems, network and VPN connectivity faults, endpoint performance degradation, and peripheral or driver failures recur continuously, and their resolutions are frequently already documented inside the organisation's own records.

The academic response to this repetitiveness has, for the most part, taken the form of supervised classification. Oliveira, Nogueira and Brito compared machine-learning algorithms for classifying IT incident tickets and report that categorisation is substantially automatable, while also documenting the sensitivity of accuracy to category granularity and to class imbalance in real ticket data [3]. Related work extends supervised learning to the prediction of *when* an incident will be resolved: Mulyati et al. show that resolution-time prediction improves materially when features are aggregated across the incident lifecycle rather than taken at ticket-open time alone, and report that time-zero feature sets systematically under-perform [4].

The structural limitation of this body of work is that the model is a terminal artefact. A ticket is classified, or a duration is predicted, and the process ends. The classifier does not participate in diagnosis, does not consult resolution knowledge, and does not act. Reported classification accuracies are therefore not evidence that support automation is solved; they measure a sub-task that sits upstream of the work a support engineer actually performs.

### 1.2.3 The Technological Opening

Three developments make the end-to-end problem newly tractable, and each is accompanied by a documented limitation that constrains how it can responsibly be used.

**Large language models.** Contemporary LLMs demonstrate multi-step reasoning and sustained instruction-following [5], which supports *conditional* diagnostic dialogue — selecting the next diagnostic step from the reported outcome of the previous one, something fixed decision trees cannot do. The corresponding weakness is well documented: fluent generation of confident but factually incorrect content.

**Retrieval-augmented generation.** RAG conditions generation on documents retrieved from a trusted corpus, combining parametric model knowledge with an explicit non-parametric memory [6]; the approach has since matured into a substantial design space of retrieval, ranking and integration strategies [7]. Its retrieval component rests on dense representation learning — dual-encoder passage retrieval [8] and siamese sentence embeddings for efficient semantic similarity [9]. Applied to IT support specifically, Toro Isaza et al. combine retrieval over historical incident resolutions with generative recommendation and report improved recommendation quality under the domain-coverage and model-size constraints typical of enterprise deployment [10], while Xu et al. show at LinkedIn that treating a ticket corpus as flat text discards intra-issue structure and inter-issue relations, and that preserving that structure improves retrieval and downstream answer quality [11].

**Agent architectures.** Rather than a single model performing every function, the agentic paradigm decomposes a task across components that reason, act, observe the outcome and iterate [12], a construction pattern now surveyed systematically in general [13] and within software engineering specifically [14]. The decomposition matters for governance as much as for capability: it creates explicit boundaries at which policy can be enforced.

### 1.2.4 Why the Problem Remains Unsolved

The availability of these technologies has not produced solved IT support automation, and the evidence for that statement is direct rather than rhetorical.

The clearest measurement comes from ITBench, a systematic benchmark of AI agents on real-world IT automation tasks. Agents built on state-of-the-art models resolve only **11.4% of Site Reliability Engineering scenarios**, **25.2% of compliance and security-operations scenarios** and **25.8% of financial-operations scenarios** [15]. Domain-specific studies converge on the same picture at the diagnostic tier: Ahmed et al., evaluating LLMs for recommending root causes and mitigation steps for cloud incidents at scale, find meaningful assistance but performance short of autonomous reliability [16], and Chen et al.'s RCACopilot — a production on-call system at Microsoft that aggregates diagnostic information before invoking an LLM — reports root-cause categorisation accuracy of up to 0.766 on a year of real incidents [17]. A system correct roughly three times in four is a valuable assistant and an unacceptable autonomous actor; the gap between those two roles is precisely where the research question of this thesis sits.

Recent work has begun to close part of that gap and, in doing so, sharpens rather than removes the research opportunity. VIGIL, an edge-extended agentic system for enterprise IT support, deploys desktop-resident agents that perform situated diagnosis, retrieval over enterprise knowledge and *policy-governed remediation with explicit consent*, and reports from a ten-week pilot on 100 endpoints that interaction rounds fell by 39% and that self-service resolution was achieved in 82% of matched cases [1]. This is important for two reasons. It confirms that consent-gated on-device remediation is a viable and valuable design direction — the design premise of this research is therefore supported rather than speculative. It also confirms that the direction is under-characterised: a single industrial pilot establishes that the approach can work in one deployment, not *which architectural components produce the effect*. Broader AIOps surveys reach the same conclusion from the opposite direction, documenting rapid expansion of LLM application across failure-management tasks alongside fragmented architectures and inconsistent evaluation practice [18].

### 1.2.5 The Safety Dimension

A support system that executes commands on user machines consumes untrusted input by construction — user prose, pasted logs, error text, screenshots — and is therefore exposed to prompt injection. Greshake et al. demonstrated that adversarial instructions need not come from the user at all: content retrieved by an LLM-integrated application can itself carry the attack, an *indirect* injection vector that applies directly to any system performing retrieval over a shared corpus [19]. Systematic study of deployed LLM-integrated applications found injection vulnerabilities across a large proportion of those tested [20]. Where the model is permitted to call tools, the exposure becomes an execution risk rather than an information risk: AgentDojo, an evaluation environment populated with realistic tool-using tasks and hundreds of security test cases, finds that existing defences break some security properties but not all, and that state-of-the-art models fail many tasks even without an adversary present [21]. ToolEmu makes the complementary point that identifying such risks by hand is prohibitively laborious, motivating systematic sandboxed testing of agent failure modes [22].

The implication for design is specific and is adopted in this research: **safety for an acting system cannot rest on model behaviour**, because the model is the component under attack. It must rest on mechanisms that hold even when the model is fully compromised.

### 1.2.6 Summary of the Background Argument

The chain of reasoning that motivates this research is therefore: measured evidence exists that knowledge-access assistance improves support productivity [2]; the academic literature automates upstream sub-tasks in isolation [3], [4]; the enabling technologies for end-to-end support — LLMs [5], retrieval grounding [6]–[11] and agent decomposition [12], [13], [14] — are individually mature; benchmark and field evidence nevertheless shows the composed task is largely unsolved [15], [16], [17], [18]; a recent industrial pilot demonstrates that governed remediation is viable but does not decompose *why* it works [1]; and any system that acts must be governed by model-independent controls because the adversarial exposure is demonstrated and practical [19]–[22]. What is missing is not a further demonstration that such a system can be built, but **open, component-level evidence about which architectural decisions matter and under what governance action-taking becomes acceptably safe.**

## 1.3 Problem Statement

### 1.3.1 General Problem

Organisations cannot scale human IT support linearly with demand. The repetitive fraction of support work consumes skilled capacity that could otherwise be applied to novel and complex incidents, and the knowledge required to resolve much of that repetitive work already exists within the organisation but is costly to locate, interpret and apply on every recurrence. Automation attempts to date resolve this only partially: they either restrict themselves to safe-but-shallow information retrieval, terminating at a recommendation the user must still carry out, or they extend into action-taking without governance adequate for production deployment. The measured resolution rates on realistic IT tasks — 11.4% on SRE scenarios for state-of-the-art agents [15] — indicate that the deficiency is architectural rather than merely a matter of model capability.

### 1.3.2 Specific Problems

Within the ITSM domain this research targets five specific, evidenced shortcomings.

**P1 — Shallow conversational capability.** Intent-classification and decision-tree support bots handle single-turn deflection adequately but degrade in multi-turn, context-dependent diagnosis, where the correct next step depends on the outcome of the previous one. The capability required is conditional reasoning over dialogue state [5], not intent lookup.

**P2 — Ungrounded generation.** Assistants that generate advice without retrieval from organisational knowledge produce plausible but organisation-inappropriate guidance. Retrieval grounding is an established mitigation [6], [7], [10], [11], but the literature predominantly evaluates *retrieval relevance*; its contribution to *end-to-end resolution outcomes* within a full support pipeline is rarely isolated and measured.

**P3 — Static ticket lifecycle management.** Ticket creation, prioritisation, categorisation and status transition remain largely manual or governed by static rules. Supervised approaches to ticket classification [3] and resolution-time prediction [4] have been studied, but as standalone models detached from the conversational process that generates the ticket, and — in the resolution-time case — with the acknowledged weakness that features available at ticket-open time carry limited signal [4].

**P4 — The action gap.** Support systems predominantly *advise* rather than *act*. Even well-defined, low-risk operations — clearing temporary files, flushing a DNS cache, restarting a service — are left to the user to perform manually. Closing this gap requires executing commands on user systems, which introduces genuine security exposure through direct and indirect prompt injection [19]–[21]. Where the gap has been closed in practice it has been closed under policy governance and explicit consent [1], confirming both the viability of the approach and the necessity of the governance.

**P5 — Absence of architectural evidence.** Where integrated systems exist — commercially, or as industrial pilots [1] — their internal architecture, per-component contribution and failure characteristics are not publicly decomposed or independently evaluated. Researchers and practitioners consequently have no evidence base on which architectural decisions actually matter, a fragmentation that AIOps surveys identify explicitly but do not resolve [18].

### 1.3.3 Statement of the Research Gap

> **The gap is not the absence of an integrated IT support system, but the absence of an openly specified, architecturally transparent and component-wise evaluated reference design for agent-decomposed IT support with model-independent, human-gated remediation.**

Concretely, the reviewed literature does not answer:

- **G1.** What does agent decomposition contribute, *measurably*, over a monolithic LLM performing the same functions in an ITSM setting? No reviewed publication isolates this by ablation.
- **G2.** What does retrieval grounding contribute to *end-to-end resolution outcomes* in IT support, as distinct from retrieval relevance measured in isolation [10], [11]?
- **G3.** How should a risk-tiered, human-gated remediation mechanism be specified so that action-taking is safe enough to deploy under adversarial input [19]–[21], and what usability cost does that gating impose on the user?

These are answerable with an implementable artefact and a designed experiment. They constitute the intended contribution of this project.

## 1.4 Research Question

**Primary research question**

> *To what extent does decomposing an LLM-based IT support system into specialised, independently governed agents — combined with retrieval-grounded troubleshooting and risk-tiered, human-gated remediation — improve diagnostic accuracy, resolution effectiveness and operational safety relative to monolithic LLM baselines?*

The question is stated in comparative and testable form. The formulation used in the June 2026 submission ("how can a system be designed…") was design-descriptive and admitted no empirical answer; any implemented system would have satisfied it.

**Sub-questions**

| ID | Sub-question | Answered by |
|---|---|---|
| **RQ1** | How accurately can an LLM-based classifier distinguish technical from non-technical requests and assign category and urgency, relative to keyword-based and classical supervised baselines [3]? | Ablation A1 (§5.4) |
| **RQ2** | What measurable effect does retrieval grounding have on the factual correctness and organisational appropriateness of generated troubleshooting guidance [6], [10], [11]? | Ablation A2 (§5.4) |
| **RQ3** | Does distributing ticket-lifecycle reasoning across dedicated agents improve lifecycle-state correctness relative to a single-model implementation [13], [14]? | Ablation A3 (§5.4) |
| **RQ4** | Can a whitelist-constrained, risk-tiered, approval-gated execution mechanism prevent unsafe action execution under adversarial input, including direct and indirect prompt injection [19]–[21]? | Adversarial protocol (§5.5) |
| **RQ5** | What is the contribution of each architectural component, established through systematic ablation? | Ablation family A0–A4 (§5.4) |

## 1.5 Research Motivation

**Measured evidence that the problem is worth solving.** The 14% productivity effect observed when support agents were given a generative assistant, concentrated among less-experienced workers [2], establishes that improving knowledge access in support work has real and quantified value. This research asks what architecture delivers that value most effectively and how far it can be extended from advice into action.

**Measured evidence that the problem is not solved.** The 11.4% SRE resolution rate reported by ITBench [15] and the ceiling of 0.766 root-cause categorisation accuracy reported by a production system on real incidents [17] together demonstrate that applying current models to IT operations does not by itself produce competent automation. Architectural research is therefore warranted rather than redundant.

**A governance question with reach beyond this domain.** Any AI system permitted to execute commands on real infrastructure raises the question of how autonomy should be bounded. Prompt injection against tool-using agents is a demonstrated, practical attack class [19]–[21]. IT support is an unusually tractable setting in which to study bounded autonomy, because the action space is enumerable and risk-classifiable — unlike open-ended agent domains where the set of possible actions cannot be listed in advance.

**A reproducibility deficit.** Commercial ITSM platforms are not inspectable, and industrial pilots report aggregate outcomes rather than component contributions [1]. If the research community is to reason about how these systems should be built, openly documented architectures with published evaluation methodology are a precondition. This project can supply one at a scale appropriate to an undergraduate thesis.

**Practitioner relevance.** Organisations without the budget for enterprise ITSM AI platforms currently have no documented reference design to build against. An open architecture with characterised component contributions and an explicit safety argument has direct practical value independent of the empirical findings.

## 1.6 Research Aim

> To design, implement and empirically evaluate an agent-decomposed, retrieval-grounded IT support framework with risk-tiered, human-gated remediation, and to determine — through systematic ablation and adversarial testing — the measurable contribution of each architectural component to diagnostic accuracy, resolution effectiveness and operational safety.

The aim is stated in terms of *determining component contributions*, not of demonstrating superiority over industry averages. This is a deliberate correction to the June 2026 aim, which promised improvement "compared to conventional IT support approaches" while planning a comparison against a published industry statistic drawn from a different population, a different ticket mix and a different measurement definition. That comparison could not have supported the claim it was intended to support and has been replaced by a matched internal human baseline (§5.4, condition A0).

## 1.7 Research Objectives

Objectives are stated in the identify / analyse / design–develop / evaluate form prescribed by the chapter breakdown, each with a verifiable completion criterion and an honest status.

| # | Objective | Verifiable completion criterion | Status |
|---|---|---|---|
| **O1** | **To identify** the limitations of existing automated IT support approaches, academic and commercial, through structured literature review | Comparative analysis distinguishing academic from commercial approaches, with strengths and limitations tabulated (§2.4, §2.8) | **Complete** |
| **O2** | **To analyse** the architectural suitability of LLM, RAG and agent-decomposition paradigms for ITSM, including their documented failure modes | Technological analysis at algorithmic, design and workflow levels, each terminating in a justified design decision (§2.5–§2.7) | **Complete** |
| **O3** | **To design and develop** an agent-decomposed IT support framework with retrieval grounding and model-independent remediation governance | Operational system with five specialised agents, seven governance controls, verified end-to-end (Chapter 4, Appendix A) | **Complete** |
| **O4** | **To design** an evaluation methodology capable of isolating individual component contributions and testing the safety claim adversarially | Ablation protocol, adversarial protocol, metric definitions and statistical analysis plan (Chapter 5) | **Complete in design; harness not implemented** |
| **O5** | **To evaluate** the framework empirically and characterise the contribution of each architectural component | Ablation results with effect sizes and significance testing | **Not started** |
| **O6** | **To evaluate** the adversarial robustness of the remediation governance mechanism | Injection and bypass test-suite results, including any successful bypass | **Not started** |

## 1.8 Rich Picture of the Proposed Solution

The proposed system — *Auto-Ops-AI* — routes every user interaction through an orchestration layer that invokes five specialised agents in a fixed sequence, grounds generated guidance in an organisational knowledge corpus, and permits remediation only through an enumerated whitelist behind a mandatory human approval gate.

```
        ┌───────────────────────────────────────────────────────────────┐
        │  USER  (text message · screenshot · approval decision)        │
        └───────────────┬───────────────────────────────┬───────────────┘
                        │                               │ approve / decline
                        ▼                               │
        ┌───────────────────────────────┐               │
        │  PRESENTATION — React + Vite  │               │
        │  chat · dashboard · tickets   │               │
        └───────────────┬───────────────┘               │
                        │ REST/JSON + JWT               │
        ┌───────────────▼───────────────────────────────┼───────────────┐
        │  API LAYER — FastAPI · JWT auth · RBAC (5 roles, 24 perms)    │
        └───────────────┬───────────────────────────────┼───────────────┘
                        │                               │
        ┌───────────────▼───────────────────────────────┼───────────────┐
        │  ORCHESTRATION LAYER (deterministic sequence) │               │
        │                                               │               │
        │  ① Image Analysis Agent ──── screenshot → text description    │
        │            ▼                                                  │
        │  ② Intent classification ── technical? · category · urgency   │
        │            ▼                                                  │
        │  ③ Retrieval  ── embed query → cosine similarity over KB      │
        │            │        (threshold 0.5, top-3 retained)           │
        │            ▼                                                  │
        │  ④ LLM Conversation Agent ─ grounded multi-turn diagnosis     │
        │            ▼                                                  │
        │  ⑤ Ticket Intelligence Agent ─ create? · priority · metadata  │
        │            ▼                                                  │
        │  ⑥ Assignment Service ── specialisation + workload matching   │
        │            ▼                                                  │
        │  ⑦ Ticket Status Agent ─ deterministic lifecycle state machine│
        │            ▼                                                  │
        │  ⑧ Action Executor Agent ─ propose ONE next action ───────────┤
        │        │  whitelist(25) → param validation → risk tier        │
        │        │                                                      │
        │        └──── ⛔ EXECUTION BLOCKED until human approval ───────┘
        │                       │ (approved + ownership verified)       │
        │                       ▼                                       │
        │              PowerShell subprocess (no shell), 30 s timeout    │
        └───────────────┬───────────────────────────────────────────────┘
                        ▼
        ┌───────────────────────────────────────────────────────────────┐
        │  DATA — SQLite (users · tickets · chat · audit) │ KB corpus    │
        │  ML  — resolution-time regressor │ system-health classifier   │
        └───────────────────────────────────────────────────────────────┘
```

**Workflow narrative.** A user reports a problem in natural language, optionally attaching a screenshot. If an image is present it is described first and merged into the textual message. The merged message is classified as technical or non-technical, with a category and an urgency score. Technical messages trigger retrieval over the knowledge corpus; retrieved passages above the similarity threshold are supplied to the conversation agent, which conducts a multi-turn diagnostic dialogue conditioned on them. From the third conversational turn onward the ticket intelligence agent decides whether a ticket is warranted and generates its metadata; if escalation is signalled, the assignment service allocates a human agent. The status agent then reconciles the ticket's lifecycle state against the conversation evidence using deterministic rules. Finally — and only when the user has explicitly enabled Agent Mode — the action executor proposes a *single* next remediation action drawn from the whitelist, together with its risk tier. Nothing executes until the user approves, and approval is checked against the requesting user's ownership of the request.

**The governance boundary is the design's centre of gravity.** Every arrow that leads to execution passes through the whitelist, parameter validation and the approval gate, and all three are enforced in application code rather than by prompt instruction. This is what makes the safety claim testable (§5.5) rather than merely asserted.

## 1.9 Resource Requirements

### 1.9.1 Hardware

| Resource | Minimum | Recommended | Justification |
|---|---|---|---|
| Processor | Intel Core i5 (8th gen) or equivalent | Intel Core i7 (10th gen) / AMD Ryzen 7 | Model inference is cloud-hosted; local load is API orchestration and the React build |
| RAM | 8 GB DDR4 | 16 GB DDR4 | Backend, frontend dev server, database and browser concurrently; embedding cache held in process memory |
| Storage | 256 GB SSD (50 GB free) | 512 GB SSD (100 GB free) | Container images, dependencies, corpus and evaluation trial logs |
| Network | 5 Mbps stable | 25+ Mbps broadband | Every generative and embedding call is a network round trip; latency measurements are sensitive to it |
| GPU | Not required | Optional | No local model hosting is in scope (§1.10) |
| Evaluation VMs | 1 isolated Windows VM with snapshot capability | 2 VMs | Remediation actions mutate system state; §5.2 requires restoration to a uniform baseline between trials, and §5.5 requires adversarial testing on isolated researcher-controlled machines only |

### 1.9.2 Software

| Category | Tool | Version in use | Purpose |
|---|---|---|---|
| Language | Python | 3.11 | Backend, agents, ML |
| Runtime | Node.js | 18+ | Frontend tooling |
| Backend framework | FastAPI | — | REST API, OpenAPI schema |
| Frontend framework | React | 19.2 | User interface |
| Build tool | Vite | 7.2 | Frontend build and dev server |
| LLM provider | Google Gemini API | version to be recorded with all results (§5.2) | Conversational reasoning, ticket metadata generation, multimodal image analysis |
| Embedding model | Google `text-embedding-004` | — | Semantic similarity for retrieval |
| Vector store | ChromaDB | — | **Offline ingestion only at present**; live retrieval is in-memory (§4.6) |
| Relational database | SQLite | 3.x | Users, tickets, chat history, audit log |
| ORM | SQLAlchemy | — | Database abstraction |
| ML libraries | scikit-learn, NumPy, Pandas | — | Predictive models, similarity computation, data handling |
| Execution | Windows PowerShell (subprocess, no shell interpretation) | — | Remediation action execution |
| Authentication | PyJWT (HS256) + bcrypt | — | Token issuance, password hashing |
| Containerisation | Docker + Docker Compose | — | Reproducible development and deployment environments |
| Version control | Git + GitHub | — | Source management; supports the reproducibility claim in §1.11 |
| Statistical analysis | Python (SciPy / statsmodels) | — | Analysis plan in §5.7 |

**Correction to the June 2026 submission.** That version listed LangChain as an AI-orchestration dependency and ChromaDB as the live vector database. Source inspection establishes that neither is in the runtime request path; both appear only in a standalone ingestion script. The table above reports the verified position, and §4.6 specifies the remedial work.

## 1.10 Project Scope

| Aspect | In scope | Out of scope | Justification for the boundary |
|---|---|---|---|
| Conversational AI | Multi-turn, context-retaining dialogue via a hosted LLM; escalation detection; 20-message memory window | Slack / Teams / WhatsApp integration; voice input | Channel integration is engineering surface, not research surface; it would not alter any measured outcome |
| Knowledge retrieval | Embedding-based semantic retrieval over a curated organisational corpus | Web crawling; external internet search | The research claim concerns grounding in *organisational* knowledge; open-web retrieval would confound the ablation in §5.4 |
| Input modalities | Text; images (screenshots, device photographs) via multimodal LLM | Video; live screen sharing | Multimodal fault description is demonstrated in the literature [23] and cheaply supported; video adds cost without addressing a stated gap |
| Ticket management | Automated creation, prioritisation, categorisation, assignment, lifecycle transition | ServiceNow / Jira / Zendesk integration | Integration would make lifecycle behaviour depend on an external system, destroying internal validity for RQ3 |
| Remediation | Whitelisted, risk-tiered Windows diagnostic and remediation actions under mandatory human approval | macOS / Linux; destructive operations; remote machine access | Single-platform scope is a stated limitation (§7.1, L6); destructive operations are excluded on ethical grounds (§3.13) |
| Agent architecture | Five specialised agents under centralised deterministic orchestration | Agent-to-agent negotiation; dynamic agent creation; self-modifying agents | Deterministic orchestration is required for reproducible ablation; autonomous negotiation would make trials non-comparable |
| Security | RBAC (5 roles, 24 permissions), JWT authentication, audit logging, adversarial input testing | SSO, OAuth2 federation, Active Directory, MFA | Enterprise identity federation is a deployment concern that does not bear on the safety claim being tested |
| Predictive analytics | Resolution-time estimation and system-health classification (secondary objective) | Real-time anomaly detection; capacity planning | Retained as a secondary objective only; §4.8 records that this component is currently under-specified |
| Evaluation | Controlled scenario-based ablation; adversarial safety testing; usability assessment | Longitudinal production study; cross-organisational benchmarking; production A/B testing | Out of reach at undergraduate scale; the resulting external-validity limit is stated rather than concealed (§7.1) |
| Data | Curated synthetic IT support corpus with human-authored ground truth | Real production data from live enterprises | No ethical route to production support transcripts; the consequent limitation is reported (§7.1, L5) |

## 1.11 Significance of the Research

**Academic significance.** The study addresses three questions the reviewed literature leaves open (G1–G3, §1.3.3). Its primary academic output is not the system but the *evidence about the system*: a component-wise characterisation of what agent decomposition and retrieval grounding contribute to end-to-end IT support outcomes, and an adversarial characterisation of when human-gated remediation holds. Existing work supplies either the components in isolation [3], [4], [6]–[12], [14] or an integrated outcome without decomposition [1], and infrastructure-tier benchmarks [15] do not cover the conversational support tier at which most support work occurs.

**Methodological significance.** The evaluation protocol — a five-condition ablation with a matched human baseline, human-authored ground truth established before any system execution, repeated trials to characterise generative non-determinism, and a five-class adversarial suite — is reusable by other researchers evaluating support automation. Two design decisions are worth stating explicitly because they address recurring validity threats: ground truth is authored by humans before execution rather than generated by a model, avoiding the circularity of evaluating a model against labels a model produced; and the human comparison uses the *same* scenarios under the same timing protocol rather than an external published mean.

**Practical significance.** Organisations that cannot procure enterprise ITSM AI platforms gain a documented reference design with an explicit, testable safety argument, together with an account of which components carry their weight and which do not. The set of governance controls in §4.7 is transferable to any system that permits an LLM to act.

**Significance of negative and partial results.** The project commits to reporting configurations that did not perform as designed, and any successful adversarial bypass, as findings rather than omissions. Given that AIOps surveys identify inconsistent and selective evaluation as a field-level problem [18], transparent reporting of partial failure is itself a contribution, if a modest one.

**Explicit limitation of the contribution.** This work does not claim to introduce a previously non-existent category of system, and does not claim to outperform commercial platforms or the industrial pilot described in [1]. Its claim is narrower and defensible: to make architectural knowledge in this space open, measured and reproducible at a scale that permits independent reimplementation.

## 1.12 Thesis Structure

| Chapter | Content | Status at this submission |
|---|---|---|
| **1. Introduction** | Research context, problem background and justification, problem statement, research question, motivation, aim, objectives, rich picture, resources, scope, significance | **Complete** |
| **2. Literature Review** | Conceptual map, domain overview, comparative assessment of existing systems and frameworks, technological analysis (algorithmic / design / workflow), critical reflection, gap justification | **Complete** |
| **3. Methodology** | Research paradigm, approach, design and strategy, data collection methods and sources, DSR execution workflow, development methodology, tools and technologies, evaluation approach, project management, timeline, ethics, validity | **Complete** |
| **4. System Design and Implementation** | Architecture, agent specifications, orchestration workflow, retrieval subsystem, remediation governance, predictive subsystem, data layer | **Complete for the implemented artefact; two subsystems require revision** |
| **5. Evaluation Design** | Evaluation objectives, experimental setup, corpus, ablation design, adversarial protocol, metrics, statistical analysis plan | **Designed; not executed** |
| **6. Progress, Results and Discussion** | Progress position; implementation verification outcomes; defined structure of the forthcoming Results and Discussion chapters | **Progress and verification reported; results not yet obtained** |
| **7. Limitations, Challenges and Remaining Work** | Current limitations, active risks, phased remaining work | **Complete for the current position** |
| *(Final thesis)* **Conclusions** | Accomplishment of objectives, problems encountered, self-reflection, real-world applicability, future recommendations | **Not started** |

## 1.13 Chapter Summary

This chapter established that IT support automation remains a genuinely unsolved problem despite mature enabling technologies. The background argument proceeded from measured evidence that knowledge-access assistance improves support productivity by approximately 14% [2], through the isolation-focused character of existing academic automation [3], [4], to benchmark and production evidence that composed IT automation resolves only 11.4% of realistic SRE scenarios [15] and reaches at best 0.766 root-cause accuracy in production [17]. A recent industrial pilot demonstrates that consent-governed remediation is viable [1] but reports aggregate outcomes rather than component contributions, and adversarial research establishes that any acting system must be governed by model-independent controls [19]–[22].

From this the chapter derived a research gap concerning the absence of open, component-wise evaluated architectural evidence; a comparative and testable primary research question with five sub-questions; an aim expressed as determining component contributions rather than demonstrating superiority; and six objectives with verifiable completion criteria and honest status. The rich picture, resource requirements, scope boundary, significance and thesis structure complete the foundation on which Chapter 2 builds.

---

# Chapter 2 — Literature Review

## 2.1 Chapter Overview

This chapter reviews the literature that defines and constrains the research problem, and does so critically: each strand closes with the researcher's own assessment of what the work establishes, what it does not, and what design decision follows for this project. The review is organised from domain to technology to gap. Section 2.3 characterises the ITSM domain; §2.4 assesses existing systems and frameworks comparatively, covering both academic prototypes and commercial platforms and justifying in each case whether the approach is suitable for the present problem; §2.5–§2.7 conduct the technological analysis at the algorithmic, design and workflow levels; §2.8 consolidates strengths and limitations and states the gap; §2.9 explains how this research addresses it.

Sources are drawn predominantly from 2019–2026. Older work is cited only where it is foundational — dense retrieval [8], [9], the original RAG formulation [6], and design science research methodology [24], [25] — as permitted by the chapter breakdown.

## 2.2 Conceptual Map of the Literature

```
                    ITSM AUTOMATION PROBLEM DOMAIN
              (repetitive workload · knowledge-access deficit)
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
   §2.4 EXISTING            §2.5 ALGORITHMIC          §2.6 DESIGN
   SYSTEMS                  FOUNDATIONS               ANALYSIS
   · supervised ITSM ML     · LLM reasoning [5]       · agent decomposition
     [3], [4]               · RAG [6], [7]              [12], [13], [14]
   · LLM incident           · dense retrieval         · safety of acting
     diagnosis [16], [17]       [8], [9]                agents [19]–[22]
   · RAG for IT support     · domain RAG [10], [11]   · multimodal input [23]
     [10], [11]             · RAG evaluation [26]
   · agentic IT support
     [1]
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                    §2.7 WORKFLOW ANALYSIS
              (the action gap · human-in-the-loop gating)
                                  │
                    §2.8 EVIDENCE OF RESIDUAL DIFFICULTY
                        [15] 11.4% SRE · [18] fragmentation
                                  │
                    §2.9 IDENTIFIED GAP → THIS RESEARCH
```

## 2.3 Domain Overview

IT Service Management is the practice of delivering, supporting and improving IT services through defined processes — incident management, request fulfilment, problem management and change management — instrumented by ticketing systems and service-level agreements. Its operational reality is a tiered human workflow whose cost scales with volume and whose latency is dominated by queuing and handoff rather than by the technical difficulty of the underlying faults.

The binding constraint is therefore not a deficit of *knowledge* but of *knowledge access and application*. The field evidence supports this reading directly: when support agents were given an assistant that surfaced the practices of high performers, resolution throughput rose approximately 14%, and the effect was concentrated among the least experienced agents [2] — precisely the pattern expected if the limiting factor is access to knowledge already held within the organisation rather than the existence of that knowledge.

**Critical assessment.** This framing has a consequence that shapes the entire research. If the constraint is access and application, then a system that merely *retrieves better* addresses half the problem; the residual half is the human effort of applying the retrieved procedure. That residual is what §2.7 identifies as the action gap, and it is why this research treats remediation execution as a first-class research object rather than a convenience feature.

## 2.4 Existing Systems, Frameworks and Designs

### 2.4.1 Supervised Machine Learning for ITSM

Classical approaches concentrate on ticket classification and routing. Oliveira et al. compare supervised algorithms on IT incident tickets and establish that categorisation is substantially automatable, while documenting sensitivity to category granularity and class imbalance [3]. Mulyati et al. address the adjacent prediction task, showing that resolution-time estimation improves when features aggregate the incident's lifecycle rather than being sampled at ticket creation, and reporting that time-zero feature sets under-perform systematically [4].

**Assessment of suitability.** These approaches are *suitable as components* and *unsuitable as solutions*. They are suitable because classification and duration estimation are genuine sub-problems this research must also solve, and because [3] gives a defensible baseline against which RQ1 can be tested. They are unsuitable as solutions because the model is a terminal artefact: it emits a label and stops, without consulting resolution knowledge or acting. **Design implication:** classification is positioned in this research as an *intermediate signal* consumed by downstream agents, never as an output in itself. **A second implication, drawn from [4]:** the resolution-time component of this project currently trains on features available at ticket-open time, which is exactly the configuration [4] identifies as weakest — a defect recorded honestly in §4.8 rather than presented as a design choice.

### 2.4.2 LLM-Based Incident Diagnosis

Ahmed et al. evaluate LLMs for recommending root causes and mitigation steps for cloud incidents at industrial scale and find meaningful but sub-autonomous assistance quality [16]. RCACopilot advances this by aggregating alert-specific diagnostic information before invoking the model, and reports root-cause categorisation accuracy up to 0.766 on a year of real Microsoft incidents together with explanatory narratives [17].

**Assessment of suitability.** The architectural lesson from [17] is directly applicable and is adopted here: the model performs better when it is invoked over *assembled context* than when invoked over the raw incident description — which is the same principle that motivates retrieval grounding. The limitation is equally clear. Both works stop at *recommendation*. Neither executes, and neither therefore confronts the safety obligations that execution creates. **Design implication:** context assembly before generation is retained; the pipeline is extended past recommendation into gated execution, which is where this research departs from [16] and [17].

### 2.4.3 Retrieval-Augmented Approaches in IT and Customer Support

Toro Isaza et al. build an incident-resolution recommendation system combining RAG-based answer generation with an encoder-only classifier and a generative query-formulation stage, explicitly addressing domain-coverage and model-size constraints in enterprise IT support [10]. Xu et al., working on LinkedIn's customer-service ticket corpus, demonstrate that conventional RAG treats past tickets as flat text and thereby discards intra-issue structure and inter-issue relations, and that constructing a knowledge graph over historical issues improves retrieval and downstream answer quality [11].

**Assessment of suitability.** Both are highly suitable as evidence that retrieval grounding is the correct mechanism for this domain, and [11] in particular is a well-founded critique of the naive retrieval design this project currently implements. Both are nonetheless limited for the present purpose in the same way: evaluation is reported principally at the level of *retrieval and answer quality*, not at the level of *whether the incident was resolved end to end*. That is exactly gap **G2**. **Design implication:** the evaluation includes a no-retrieval ablation condition (A2, §5.4) specifically to isolate the contribution of grounding to end-to-end resolution outcomes, not merely to retrieval relevance. **A second implication:** [11] identifies structured retrieval as a demonstrated improvement path; this is recorded as future work rather than claimed, since the current implementation retrieves over flat text.

### 2.4.4 Agentic IT Support with Governed Remediation

VIGIL is the closest published system to the design proposed here. It deploys desktop-resident agents that perform situated diagnosis, retrieval over enterprise knowledge and policy-governed remediation on user devices with explicit consent and end-to-end observability, and reports from a ten-week pilot on 100 resource-constrained endpoints a 39% reduction in interaction rounds, at least fourfold faster diagnosis and self-service resolution in 82% of matched cases, alongside favourable usability, trust and workload measures across four validated instruments [1].

**Assessment of suitability — and an honest consequence for this thesis.** This work must be engaged with directly rather than minimised, because it substantially overlaps the design premise of this project: on-device, consent-gated, knowledge-grounded remediation. Its existence removes any claim of categorical novelty, and the June 2026 claim that no such integrated system exists is withdrawn on the strength of it (§1.1).

What it does *not* do is decompose the result. The reported gains are attributed to the system as a whole; no ablation isolates what the retrieval component contributed versus the on-device situated diagnosis versus the governance layer. Indeed, the paper's own observation that users rated the system *higher* when no historical knowledge-base match was available suggests that the contribution of retrieval to perceived value is not straightforward and is worth isolating experimentally. **Design implication:** this research positions itself as complementary rather than competing — same design direction, different research question. Where [1] establishes *that* the approach works in one industrial deployment, this project asks *which components produce the effect*, using ablation on a common scenario set, and publishes the architecture at a level permitting reimplementation. That is a smaller claim than the June 2026 draft made, and a defensible one.

### 2.4.5 Commercial Platforms

Commercial ITSM platforms combine conversational AI with ticket automation and workflow-triggered remediation. Their existence is acknowledged as a matter of accuracy: any claim that this combination is unprecedented would be false.

**Assessment of suitability.** They are unsuitable as *research evidence*, for a methodological rather than a competitive reason. Their internal architecture, component contributions and failure characteristics are not publicly documented, their evaluation methodology is not published, and their behaviour cannot be independently reproduced or ablated. A researcher cannot learn from them which architectural decisions matter. **Design implication:** this is the reproducibility argument underpinning §1.11 — the contribution of an open architecture is not that it outperforms closed ones, but that it can be inspected, criticised and rebuilt.

## 2.5 Technological Analysis I — Algorithmic

### 2.5.1 Large Language Models

Surveys document strong LLM performance on multi-step reasoning and instruction-following [5]. The property that matters for IT support is *conditional adaptation*: selecting the next diagnostic action from the reported outcome of the previous one. The corresponding failure mode — confident generation of incorrect content — is the reason this capability cannot be used unmodified in a domain where an incorrect instruction can damage a user's system.

**Critical assessment.** For general question answering, hallucination degrades answer quality. For IT support it creates physical consequences on the user's machine. The algorithmic conclusion is therefore stronger in this domain than in the general case: unconstrained generation is not merely sub-optimal, it is inadmissible. Grounding is a precondition, not an enhancement.

### 2.5.2 Retrieval-Augmented Generation and Dense Retrieval

RAG conditions generation on documents retrieved from a trusted corpus, pairing parametric model knowledge with explicit non-parametric memory [6], and has developed into a broad design space of retrieval, ranking and integration strategies [7]. The retrieval component descends from dense representation learning: dual-encoder passage retrieval trained from limited question–passage supervision substantially outperforms sparse lexical baselines on top-k retrieval accuracy [8], and siamese sentence-embedding networks make large-scale semantic similarity computationally tractable by allowing independent encoding and cosine comparison [9].

**Critical assessment.** The dependence of the whole approach on embedding quality is frequently understated. Retrieval quality bounds generation quality: if the retriever returns nothing relevant, grounding contributes nothing, and if it returns something confidently irrelevant, grounding actively misleads. The similarity threshold that decides "relevant enough" is therefore a substantive design parameter, not an implementation detail. **Design implication:** the current 0.50 threshold in this project is an unjustified constant; §5.6 defines a threshold sweep so that it becomes a tuned and reported parameter rather than an arbitrary one.

### 2.5.3 Evaluating Retrieval-Augmented Systems

Evaluation of RAG pipelines is itself a research problem, because quality decomposes into at least three dimensions: whether retrieval identified relevant context, whether the model used that context faithfully, and whether the generation is otherwise adequate. RAGAS proposes reference-free metrics addressing these dimensions without requiring human-annotated ground-truth answers [26].

**Critical assessment.** Reference-free evaluation is attractive at scale but carries a circularity risk in this setting: metrics computed by a language model over the output of a language model are not independent evidence, particularly when the same model family is used for both. **Design implication:** this research adopts human-authored ground truth as its primary basis (§5.3) and treats automated RAG metrics as a secondary, corroborating signal. The faithfulness-versus-relevance decomposition from [26] is adopted conceptually — grounding is measured separately from retrieval — but the scoring is human.

### 2.5.4 Supervised Prediction Components

Ticket classification [3] and lifecycle-aware resolution-time prediction [4] supply the algorithmic basis for the predictive subsystem. The methodological finding in [4] — that lifecycle-aggregated features outperform time-zero features — is the most directly actionable result in this strand for the present project.

**Critical assessment and honest self-application.** The predictive component implemented in this project is a three-feature linear regression trained on 500 synthetic records using only information available at ticket creation. Measured against [4], this is the weak configuration, not the strong one, and against [3] it is under-featured. **Design implication:** §4.8 records this as a defect requiring re-specification rather than presenting it as a finding, and §7.3 places the re-specification in the critical path.

## 2.6 Technological Analysis II — Design

### 2.6.1 Agent Decomposition

Wang et al. survey LLM-based autonomous agents and formalise construction around profiling, memory, planning and action [13]; the ReAct paradigm establishes interleaved reasoning and acting with observation feedback [12]; and Liu et al. survey the application of LLM-based agents in software engineering across 124 papers, documenting both the breadth of adoption and the open challenges that remain [14].

**Critical assessment — and a correction to the earlier submission.** The June 2026 draft argued that decoupling the conversational agent from the execution agent constitutes a security boundary against prompt injection. On implementation review this argument is **not supportable as stated**. In the current system both agents are Python classes within a single process, sharing address space and privileges. There is no operating-system, container or privilege-level boundary between them, and an injection that manipulates conversational output does not encounter a trust boundary merely because the next function call is dispatched to a different class. Presenting class separation as privilege separation would be a category error, and it is withdrawn.

The defensible argument is narrower and more precise. Decomposition delivers three things:

1. **An enforcement point** — a single auditable location through which every proposed action must pass and be validated against a whitelist, architecturally guaranteed rather than prompt-instructed.
2. **Determinism where determinism is preferable** — lifecycle-state logic implemented as deterministic rules rather than generative inference, making state transitions reproducible and auditable.
3. **Independent testability** — each agent can be evaluated in isolation, which is a precondition for the ablation methodology in Chapter 5.

The *actual* safety mechanism is the combination of an enumerated action whitelist, parameter validation with metacharacter screening, and mandatory human approval. This is stated accurately here and evaluated as such in §5.5.

### 2.6.2 Safety of Acting Agents

Greshake et al. establish indirect prompt injection: adversarial instructions embedded in content that an LLM-integrated application retrieves, rather than in the user's own input, applying to any system that performs retrieval over a corpus it does not fully control [19]. Systematic testing of deployed LLM-integrated applications found injection vulnerabilities in a large proportion of those examined [20]. Where agents call tools, the exposure becomes execution risk: AgentDojo populates a realistic tool-use environment with 97 tasks and 629 security test cases and finds that existing attacks break some security properties while existing defences close some but not all, with state-of-the-art models failing many tasks even absent an adversary [21]. ToolEmu argues that manual identification of such risks does not scale and demonstrates LM-emulated sandboxing as a systematic alternative, with human evaluation indicating that 68.8% of identified failures would be valid real-world agent failures [22].

**Critical assessment.** Read together, these four works support one conclusion that this research adopts as a design axiom: **safety controls that depend on model compliance are not safety controls.** A defence expressed as a system-prompt instruction is defeated by an injection that rewrites the instruction. A defence expressed as an enumerated whitelist in application code is not, because the model cannot expand the set of executable operations regardless of what it is persuaded to output. **Design implication:** all seven governance controls in §4.7 are enforced outside the model, and §5.5 tests exactly this property by attacking the model and measuring whether the controls hold. The indirect vector from [19] is specifically operationalised as a test class in which adversarial content is planted in retrieved documents and uploaded images — an attack surface this system possesses by construction.

### 2.6.3 Multimodal Fault Description

Alsaif et al. propose a multimodal LLM-based fault detection and diagnosis framework for industrial settings, using a vision-capable model to interpret fault evidence that is visual rather than textual [23].

**Critical assessment.** The transfer to end-user IT support is natural: users describe faults badly in prose but photograph or screenshot them accurately, and error dialogues, BSOD codes and device photographs carry diagnostic information that free text loses. The limitation for this project's purposes is that visual interpretation adds a second generative stage before classification, compounding rather than reducing uncertainty. **Design implication:** the image agent's output is merged into the textual message and passed through the same classification and retrieval path as text, so that no separate, unvalidated decision path exists for image-originated requests.

## 2.7 Technological Analysis III — Workflow

Current ITSM workflows are fragmented across human and machine steps: a user converses with a bot, the bot creates a ticket, a human reads it, a human executes the fix, a human closes it. The literature reviewed above terminates at different points along that chain — classification terminates at step two [3], [4]; diagnosis terminates at recommendation [16], [17]; retrieval-augmented support terminates at a proposed resolution [10], [11].

**The action gap** is the resulting deficiency: systems can explain *how* to fix an issue but cannot fix it. Closing it changes the system's risk profile qualitatively rather than incrementally, because an incorrect output is no longer merely wrong — it is executed.

VIGIL demonstrates that the gap can be closed in production under policy governance and explicit consent, with measured operational benefit [1]. What the literature does not supply is a decomposition of the workflow into components whose individual contributions have been measured, or a published account of how the governance layer behaves under deliberate attack. Human-in-the-loop gating is widely prescribed as a principle in the safety literature [19]–[22] but is rarely instantiated, specified and then adversarially tested as a mechanism.

**Critical assessment.** A complete support workflow understands the issue, retrieves the documented procedure, requests permission, executes the approved operation, and closes or escalates the ticket. Anything short of that is partial automation that leaves the residual work with the user. But a complete workflow that cannot demonstrate its own safety under attack is not deployable. **Design implication:** the workflow in §4.5 closes the loop, and the approval gate is treated not as a usability nicety but as a load-bearing safety control whose cost to the user is itself measured (§5.6, usability dimension).

## 2.8 Critical Comparison: Strengths and Limitations

| Approach | Representative work | Strengths | Limitations for this problem | Studied within an integrated, ablated pipeline? |
|---|---|---|---|---|
| Supervised ticket classification | [3] | Mature, cheap, interpretable, strong baseline for RQ1 | Terminal artefact; no diagnosis, no knowledge use, no action | No — standalone classifier |
| Lifecycle-aware resolution-time prediction | [4] | Demonstrates value of lifecycle feature aggregation; directly critiques time-zero features | Prediction only; does not participate in resolution | No |
| LLM incident diagnosis | [16], [17] | Context assembly before generation improves accuracy; validated on real production incidents | Stops at recommendation; 0.766 accuracy insufficient for autonomy [17] | No — diagnosis only |
| RAG for IT/customer support | [10], [11] | Domain-appropriate grounding; [11] shows structured retrieval beats flat-text retrieval | Evaluated on retrieval/answer quality, not end-to-end resolution (**G2**) | Partially |
| Agentic IT support with governed remediation | [1] | Closes the action gap in production; consent-gated; validated usability instruments; measured operational gains | Aggregate outcomes only; no component ablation (**G1**); no published adversarial evaluation (**G3**) | No — integrated but not decomposed |
| Agent architecture theory | [12], [13], [14] | Establishes decomposition patterns and reasoning–action interleaving | General-purpose; not ITSM-situated; benefit not empirically isolated in this domain (**G1**) | No |
| Safety of acting agents | [19]–[22] | Demonstrates attack classes and evaluation environments; motivates model-independent controls | Prescribes principles; does not instantiate and test them within a domain support system (**G3**) | No |
| IT agent benchmarking | [15] | Direct measurement of residual difficulty (11.4% SRE) | Infrastructure tier, not conversational support tier; benchmarks rather than proposes architecture | Benchmark only |
| AIOps synthesis | [18] | Documents field-level fragmentation and inconsistent evaluation | Identifies the problem; does not resolve it | Survey |
| Commercial ITSM AI platforms | — | Deployed at scale; integrated capability | Architecture, component contributions and failure modes undocumented; not reproducible or ablatable (**P5**) | Not inspectable |

## 2.9 Reflection and Confirmation of the Research Gap

The reviewed literature, taken as a whole, establishes six things. Ticket classification and resolution-time prediction are substantially automatable but are studied as terminal artefacts [3], [4]. Retrieval grounding demonstrably improves IT incident recommendation but is evaluated on retrieval quality rather than resolution outcomes [10], [11]. LLMs assist incident diagnosis without reaching autonomous reliability, topping out at 0.766 in a production deployment [16], [17]. Agent decomposition is well theorised but its benefit is not empirically isolated in an ITSM setting [12], [13], [14]. Acting agents face demonstrated, practical adversarial exposure through both direct and indirect injection, and defences that depend on model compliance fail [19]–[22]. And realistic IT automation remains largely unsolved at the benchmark level [15], within a field that surveys characterise as fragmented and inconsistently evaluated [18].

The one system that closes the action gap in production [1] confirms the design direction and simultaneously defines the remaining opportunity: it reports what an integrated system achieved, not which of its components achieved it, and does not publish an adversarial evaluation of its governance layer.

> **Gap confirmed.** What is absent from the literature is not an integrated system but **open architectural evidence** — which components contribute what to end-to-end IT support outcomes, and under what governance action-taking becomes acceptably safe under deliberate attack.

## 2.10 How This Research Addresses the Gap

| Gap | Addressed by | Chapter |
|---|---|---|
| **G1** — contribution of agent decomposition is unmeasured | Ablation conditions A1 → A3 on an identical scenario set, isolating monolithic LLM, retrieval-augmented LLM and agent-decomposed configurations | §5.4 |
| **G2** — retrieval grounding evaluated on relevance, not resolution | Ablation condition A2 measured against end-to-end resolution outcomes and grounding correctness, with retrieval-relevance metrics reported separately | §5.4, §5.6 |
| **G3** — human-gated remediation prescribed but not adversarially tested | Five-class adversarial protocol including the indirect vector from [19], with a commitment to report any successful bypass | §5.5 |
| **P5** — architecture not inspectable | Architecture, agent specifications, governance controls, action inventory and parameters documented at reimplementation level, with verified rather than asserted values | Chapter 4, Appendix A |

## 2.11 Chapter Summary

This chapter mapped the literature from domain to technology to gap, assessing at each stage whether an approach is suitable for the present problem and justifying the resulting design decision. It established that the domain constraint is knowledge access and application rather than knowledge existence [2]; that existing academic approaches automate sub-tasks in isolation [3], [4], [10], [11], [16], [17]; that agent decomposition and its safety obligations are well theorised but not empirically characterised in ITSM [12], [13], [14], [19]–[22]; and that the closest published system [1] demonstrates viability without decomposing contribution. Two arguments from the earlier submission were corrected on review: the claim of categorical novelty, and the claim that class-level agent separation constitutes a privilege boundary. The gap was confirmed as the absence of open, component-wise architectural evidence, and §2.10 mapped each element of that gap onto the evaluation designed in Chapter 5.

---

# Chapter 3 — Research Methodology

## 3.1 Chapter Overview

This chapter specifies how the research is conducted and why each methodological choice is appropriate to the problem. It states the philosophical paradigm and its operationalisation (§3.2), the reasoning approach (§3.3), the research design and strategy (§3.4–§3.5), the data collection methods and sources (§3.6–§3.7), the DSR execution workflow (§3.8), the system development methodology and procedures (§3.9), the tools and technologies with justification (§3.10), the project management methodology (§3.11) and timeline (§3.12), the ethical framework (§3.13), and the threats to validity with their mitigations (§3.14).

## 3.2 Research Paradigm

This research adopts **pragmatism**, operationalised through **Design Science Research (DSR)**.

**Justification of the philosophy.** Pragmatism holds that the value of knowledge lies in its practical consequences — what works to resolve a real problem — rather than in correspondence to an observed phenomenon alone. The problem investigated here is an operational one: support organisations cannot scale to meet demand. The research does not merely observe that condition; it intervenes in it by constructing an artefact and then asks whether the intervention works and why. A purely positivist stance would treat the phenomenon as given and measure it; a purely interpretivist stance would foreground participants' subjective experience of support. Neither accommodates a study whose central object is a system that does not yet exist. Pragmatism does, and it also licenses the mixed quantitative–qualitative measurement this study requires: instrumented performance logs *and* user perception of trust and approval burden.

**Justification of the operationalisation.** DSR is directed at the construction and evaluation of an IT artefact as the primary vehicle of inquiry [24], and this study follows the established six-activity DSR process model: problem identification, objective definition, design and development, demonstration, evaluation, and communication [25].

**The obligation this carries.** DSR imposes a methodological requirement that the June 2026 submission under-served: **the artefact must be evaluated in a way capable of falsifying the design claims.** A demonstration that the system runs is not a DSR evaluation; it is a demonstration. Chapter 5 is therefore built around ablation and adversarial testing — designs in which the system can fail — rather than around feature demonstration.

## 3.3 Research Approach

The study uses a combined **abductive–deductive** approach, in that order.

**Abductive phase (complete).** Observation of the action gap in deployed support systems, of benchmark evidence that composed IT automation performs poorly [15], and of the safety literature's prescription of bounded autonomy [19]–[22], led to the inference of the most plausible explanatory architecture: that decomposition with explicit, model-independent governance is a productive response. Abduction is the appropriate mode here because the architecture is not deducible from existing theory and is not derivable by induction from a dataset; it is an inference to the best available explanation, subsequently to be tested.

**Deductive phase (designed; execution pending).** From that architecture and from the literature, four falsifiable hypotheses are derived and each is bound to a specific test.

| ID | Hypothesis | Grounded in | Tested by | Falsified if |
|---|---|---|---|---|
| **H1** | Retrieval grounding significantly increases the factual correctness and organisational appropriateness of troubleshooting guidance relative to ungrounded generation | [6], [7], [10], [11] | Ablation A2 (§5.4) | No significant difference between A1 and A2 on grounding correctness |
| **H2** | LLM-based intent classification outperforms keyword-based and classical supervised baselines on category and urgency assignment | [3] | Ablation A1 (§5.4) | Baseline macro-F1 ≥ LLM macro-F1 |
| **H3** | Dedicated lifecycle agents yield higher ticket-state correctness than single-model lifecycle handling | [13], [14] | Ablation A3 (§5.4) | No significant difference in state-transition correctness between A2 and A3 |
| **H4** | Whitelist constraint plus mandatory approval gating prevents unauthorised execution under adversarial input, including direct and indirect injection | [19], [20], [21] | Adversarial suite (§5.5) | Any unauthorised execution occurs |

H4 is deliberately stated so that a single counter-example falsifies it. That is the appropriate form for a safety claim, and §5.5 commits to reporting any such counter-example.

## 3.4 Research Design

The design is a **single-artefact design science study with an embedded within-subject experimental evaluation**.

- **Unit of analysis:** the support scenario — a defined IT problem with a pre-authored ground-truth resolution path.
- **Independent variable:** system configuration (five levels, A0–A4; §5.4).
- **Dependent variables:** classification accuracy, retrieval quality, end-to-end resolution success, grounding correctness, lifecycle-state correctness, safety violations, latency, and usability/trust ratings (§5.6).
- **Design type:** within-subject. Every configuration is exposed to the *same* scenario set, so that observed differences are attributable to configuration rather than to scenario variation. This removes between-group scenario heterogeneity as a confound at the cost of order effects, which are controlled by restoring a uniform virtual-machine snapshot between trials and by randomising scenario order.
- **Repetition:** each scenario is executed five times per configuration, because generative components are non-deterministic and a single trial cannot distinguish a systematic effect from sampling variation.

## 3.5 Research Strategy

**Applied system development (prototyping) combined with controlled experimental evaluation.**

Prototyping is the appropriate development strategy because the artefact's requirements were not fully specifiable in advance: the behaviour of LLM components under real diagnostic dialogue is discovered by construction and iteration rather than by specification. Experimental evaluation is the appropriate assessment strategy because the research question is comparative — it asks how much each component contributes — and only a controlled comparison across configurations can answer that.

An observational case study was considered and rejected: it could describe how a support organisation behaves but could not isolate component contributions. A purely theoretical analysis was rejected because the safety claim (H4) is an empirical claim about a mechanism under attack and cannot be established analytically.

## 3.6 Data Collection Methods

Mixed-methods collection, aligned to the research questions.

| Method | Type | Instrument | Feeds |
|---|---|---|---|
| Instrumented system logs | Primary, quantitative | Automated capture per scenario per configuration: classification decisions and confidence, retrieval hits with similarity scores, generated guidance, action proposals, approval decisions, execution outcomes, lifecycle transitions, latency, token consumption | RQ1, RQ2, RQ3, RQ5 |
| Rubric-based scenario scoring | Primary, quantitative | Fixed scoring rubric authored before execution; scorers blind to configuration where feasible; a sample independently double-scored to establish inter-rater agreement (Cohen's κ) | RQ1, RQ2, RQ5 |
| Adversarial test execution | Primary, quantitative | Five-class injection and bypass suite (§5.5) executed on isolated virtual machines; every attempt and outcome logged | RQ4 |
| Post-task usability questionnaire | Primary, qualitative and ordinal | Structured Likert instrument covering perceived usefulness, trust in automated actions, and acceptability of the approval-gating burden, with free-text items | RQ4 (usability cost), RQ5 |
| Matched human baseline sessions | Primary, quantitative | Participants resolve the same scenarios unassisted under the same timing protocol (condition A0) | Comparative reference |
| Structured literature extraction | Secondary | Published metrics used as *contextual reference points* with explicit acknowledgement of population differences | Chapters 1–2 |
| Source-code and artefact inspection | Primary, documentary | Direct verification of implementation claims against source (Appendix A) | Chapter 4 validity |

**Methodological correction carried forward.** The June 2026 submission proposed comparing measured system performance against a published industry mean L1 resolution time. That comparison is invalid: the populations, ticket mixes and measurement definitions differ, and no adjustment available at this scale would make them comparable. It has been removed. Where human comparison is required, the matched internal baseline (A0) is used instead.

## 3.7 Data Sources

| Source | Nature | Provenance | Current state |
|---|---|---|---|
| Evaluation scenario corpus | Synthetic, human-authored | Constructed by the researcher across five categories and three difficulty tiers, each with ground-truth resolution path and acceptance criteria | **In construction** — target 60 scenarios (§5.3) |
| Knowledge-base corpus | Synthetic, curated | IT support articles representing organisational documented procedures | **6 articles — insufficient** (§4.9) |
| Synthetic user and ticket records | Synthetic | Generated profiles, tickets and conversations for lifecycle and assignment logic | 5 users, 5 tickets, 4 conversations |
| ML training data | Synthetic | 500 records for resolution-time estimation | **Requires expansion and re-specification** (§4.8) |
| Adversarial prompt set | Constructed | Direct injections, indirect injections planted in retrieved documents and uploaded images [19], parameter-level metacharacter attacks, approval-bypass and privilege-escalation attempts | **Not yet constructed** |
| System execution logs | Generated | Produced during evaluation runs | Not yet generated |
| Participant responses | Primary human | Post-task questionnaires and A0 baseline sessions | Not yet collected; ethics approval pending |
| Published literature | Secondary | Peer-reviewed venues 2019–2026, plus foundational methodology sources | Complete for Chapters 1–3 |

**Why synthetic data.** No ethically available route exists to real production support transcripts at undergraduate scale: they contain identifiable user data, organisational security information and, frequently, credentials. Synthetic data permits a defined ground truth, which real transcripts would not, at the cost of external validity — a trade explicitly accepted and reported as limitation L5 (§7.1).

## 3.8 Research Methodology Execution Workflow

Mapping the DSR process model [25] onto the specific activities of this research.

| Phase | DSR aspect | Execution in this research | Status |
|---|---|---|---|
| **3.8.1** | **Problem identification** | Analysed the scalability constraint in ITSM through structured literature review; established that the constraint is knowledge access and application rather than knowledge existence [2], and that ticket volume growth is not matched by support capacity growth | **Complete** (§1.2, §2.3) |
| **3.8.2** | **Relevance justification** | Justified relevance with measured evidence rather than market projections: a 14% support-productivity effect from generative assistance [2], and an 11.4% agent resolution rate on realistic SRE scenarios [15] establishing that the problem is both valuable and unsolved. Grey-literature market statistics used in the June 2026 draft were removed from the evidential core | **Complete** (§1.2.1, §1.2.4) |
| **3.8.3** | **Comparative analysis and gap justification** | Compared supervised ITSM ML, LLM diagnosis, domain RAG, agentic remediation and commercial platforms on strengths, limitations and whether component contributions were isolated; identified G1–G3 | **Complete** (§2.4, §2.8, §2.9) |
| **3.8.4** | **Define and finalise objectives** | Six objectives (O1–O6) with verifiable completion criteria, reformulated from the earlier four so that evaluation and adversarial evaluation are separately accountable | **Complete** (§1.7) |
| **3.8.5** | **Design, development and data management** | *Design:* five-agent orchestrated architecture with model-independent governance. *Development:* Python/FastAPI backend (~13,100 LOC), React/Vite frontend (~11,100 LOC), 69 REST endpoints, 5 agents, 25 whitelisted actions, RBAC with 5 roles and 24 permissions. *Data management:* relational store for users, tickets, chat and audit; JSON knowledge corpus with in-memory embedding cache; ML artefacts persisted to disk | **Complete for the implemented artefact; retrieval and predictive subsystems require revision** (Chapter 4) |
| **3.8.6** | **Demonstration** | End-to-end operability verified: service health, authenticated login returning a valid token and permission set, endpoint enumeration, agent instantiation within the request pipeline, frontend reachable | **Complete** (§6.6) |
| **3.8.7** | **Evaluation** | Five-condition ablation with matched human baseline, five-class adversarial protocol, nine metric dimensions, statistical analysis plan with effect sizes and multiplicity correction | **Designed; not executed** (Chapter 5) |
| **3.8.8** | **Communication** | Interim submissions, final thesis, prototype demonstration and defence; architecture documented at reimplementation level to serve the openness contribution | **In progress** |

## 3.9 System Development Methodology and Procedures

**Development procedure.** Development proceeds in vertically integrated increments: each increment delivers one agent or subsystem together with its API surface, its persistence and its frontend affordance, so that every increment is independently exercisable. This matches the per-agent testability the architecture provides and is a precondition for the ablation design, which requires each component to be switchable at runtime.

**Procedure for the remaining evaluation work.** The evaluation harness is developed against the same increment discipline: scenario runner, then configuration switching (A0–A4), then metric extraction, then the adversarial suite, then the statistical pipeline. Each stage is verifiable before the next depends on it.

**Verification procedure.** A specific procedure was adopted in this revision cycle and is retained: **all quantitative claims about the artefact are verified against source before being written.** This procedure identified four material divergences between the June 2026 description and the implementation (§6.6, R5), and is the reason the figures in this document differ from that submission in several places.

**Configuration management.** Git with GitHub remote; the LLM model version and generation parameters are recorded with every evaluation run, because results conditioned on an unrecorded model version are not reproducible.

## 3.10 Tools and Technologies

| Layer | Technology | Justification for selection | Alternatives considered and why rejected |
|---|---|---|---|
| Backend framework | FastAPI (Python 3.11) | Native async suits I/O-bound LLM API orchestration; automatic OpenAPI schema supports the endpoint enumeration used in verification; Python co-locates the API with the ML and embedding code | Django — heavier, ORM-centric, no async advantage for this workload; Node/Express — would split the ML stack across languages |
| LLM | Hosted Gemini API (conversation, ticket metadata, multimodal analysis) | Multimodal capability in a single provider supports the image path without a second vendor; hosted inference removes the GPU requirement (§1.9.1) | Local open-weight models — infeasible on available hardware and would confound latency measurement; a second commercial provider — adds cost without addressing a stated gap. **Accepted cost:** single-vendor dependency, reported as limitation L7 |
| Embeddings | `text-embedding-004` | Same provider as generation, avoiding a second API dependency; dense embeddings are the established basis for semantic retrieval [8], [9] | Local sentence-transformer models — viable and recorded as future work for cost and reproducibility |
| Vector store | ChromaDB (currently ingestion only) | Persistent approximate-nearest-neighbour indexing is the correct structure at realistic corpus scale | In-memory linear scan — what is *currently* in the live path; adequate at 6 articles, not at realistic scale. §4.6 specifies the correction and turns the comparison into a measured result |
| Relational store | SQLite + SQLAlchemy | Zero-configuration, file-backed, sufficient for single-node evaluation; SQLAlchemy keeps a migration path open | PostgreSQL — operationally heavier than the evaluation requires; no benefit at this scale |
| Frontend | React 19 + Vite 7 | Component model suits the chat/dashboard/admin surfaces; Vite gives fast iteration during prototyping | Server-rendered templates — poor fit for real-time chat and approval interactions |
| Execution | PowerShell via subprocess **without shell interpretation** | Windows-native diagnostics; bypassing the shell removes metacharacter interpretation as an attack path, supporting H4 | `shell=True` invocation — explicitly rejected; it would reintroduce the injection surface the design exists to close |
| ML | scikit-learn | Adequate for the secondary predictive objective; interpretable models preferred where the output informs SLA accounting | Deep models — unjustifiable on 500 synthetic records |
| Auth | PyJWT (HS256) + bcrypt | Stateless tokens suit the REST design; bcrypt is the standard password-hashing choice | Session cookies — additional server state without benefit here |
| Containerisation | Docker + Docker Compose | Reproducible environment is a precondition for the reproducibility contribution (§1.11) | Bare-metal setup — not reproducible by a third party |
| Statistics | Python (SciPy / statsmodels) | Keeps analysis in the same environment as data extraction, reducing transcription error | SPSS — additional tooling, no methodological gain |

## 3.11 Project Management Methodology

**Agile Scrum**, with sprints targeting independently testable increments.

**Justification.** The artefact is complex, and its requirements are partly discovered through construction — particularly the behaviour of generative components under real diagnostic dialogue. External dependencies also change during the project: hosted model versions and API surfaces are outside the researcher's control. Sequential methodologies (Waterfall, PRINCE2) assume requirement stability and a controlled dependency environment, neither of which holds. Scrum's iterative increments accommodate the discovery and permit the architecture's per-agent testability to be exploited: each agent is developed and exercised before integration into the orchestration pipeline. Kanban was considered; it suits continuous-flow maintenance work better than a project with hard academic milestones and fixed review points, which map naturally onto sprint boundaries.

## 3.12 Project Timeline

| Phase | Period | Activities | Status |
|---|---|---|---|
| **Phase 1 — Initiation and foundation** | Weeks 1–4 | Problem formulation; structured literature review; methodology and architecture design | **Complete** |
| **Phase 2 — Core system development** | Weeks 5–10 | Sprint 1: data model, authentication, RBAC, frontend shell. Sprint 2: retrieval pipeline and knowledge ingestion. Sprint 3: five agents and orchestration layer. Sprint 4: predictive components and dashboards | **Complete** |
| **Phase 3a — Verification and correction** | Weeks 11–12 | Source-level verification of all documented claims; correction of four documentation–implementation divergences; withdrawal of two unsupportable arguments; evaluation redesign around ablation and adversarial testing | **Complete — this revision cycle** |
| **Phase 3b — Foundation repair** | Weeks 13–15 | Evaluation corpus construction (60 scenarios with human-authored ground truth); knowledge-base expansion; routing live retrieval through the persistent vector store; re-specification of the predictive component | **In progress — critical path** |
| **Phase 3c — Evaluation infrastructure** | Weeks 16–18 | Evaluation harness; runtime-selectable ablation configurations A0–A4; adversarial test suite; usability instrument finalisation; a priori power analysis; ethics approval | **Not started** |
| **Phase 4 — Execution** | Weeks 19–22 | Ablation execution; adversarial safety evaluation; participant sessions including the A0 baseline; predictive model evaluation on held-out data | **Not started** |
| **Phase 5 — Analysis and writing** | Weeks 23–26 | Statistical analysis; authoring of Results and Discussion from measured data; documentation of negative and partial results; thesis completion and defence preparation | **Not started** |

**Schedule risk, stated plainly.** Phase 3b is the critical path, and the schedule contains no slack before Phase 4. If corpus construction over-runs, the mitigation is to reduce scenario count while preserving category and difficulty stratification, and to report the reduced statistical power as a limitation rather than to compensate by reducing the number of ablation conditions — the conditions are what answer the research question.

## 3.13 Ethical Considerations

1. **Non-maleficence.** The remediation agent is constrained to an enumerated whitelist of 25 non-destructive operations. Destructive operations are absent from the whitelist and cannot be constructed through parameters, which are validated against allowed-value sets and screened for shell metacharacters. Commands are executed as subprocesses without shell interpretation, so parameter content cannot be reinterpreted as a command.
2. **Informed consent and transparency.** Participants are informed that they are interacting with an AI system. No action executes on any system without explicit, logged approval by the user who owns the request. The approval interface states the action, its parameters and its risk tier before approval is requested.
3. **Data protection.** Evaluation uses synthetic user profiles and tickets. No personal data from real support interactions is processed. RBAC restricts audit-log visibility to authorised roles.
4. **Participant safety.** Adversarial testing (§5.5) is conducted exclusively on isolated, researcher-controlled virtual machines and never on participant devices. Participants never interact with the system in an adversarial configuration.
5. **Institutional approval.** Ethics approval is required before participant sessions begin and is scheduled in Phase 3c. No participant data will be collected before approval is granted.
6. **Responsible disclosure of safety findings.** If adversarial testing identifies a bypass whose mechanism generalises beyond this artefact, the finding will be reported in the thesis at a level of detail sufficient for scientific evaluation but without publishing a directly reusable exploit against third-party systems.
7. **Research integrity.** No result is reported that has not been measured. The declaration at the head of this document, the corrections appendix (Appendix B) and the citation-verification appendix (Appendix C) exist to make the boundary between claim and evidence auditable.

## 3.14 Validity, Reliability and Threats

| Threat | Type | Mitigation |
|---|---|---|
| Circular ground truth (evaluating a model against labels a model produced) | Internal | Ground truth authored by a human before any system execution; second-assessor agreement (Cohen's κ) on a sample |
| Configuration order effects and state carry-over | Internal | Uniform VM snapshot restored between trials; randomised scenario order |
| Generative non-determinism mistaken for a systematic effect | Internal / reliability | Five repetitions per scenario per configuration; variance reported alongside means |
| Scorer bias | Internal | Rubric fixed before execution; scorers blind to configuration where feasible |
| Comparison against an incommensurable external population | Construct | Matched internal human baseline (A0) on identical scenarios; external published figures used only as context, never as a comparison baseline |
| Synthetic corpus does not reflect real support language | External | Stated as limitation L5; scenarios authored from documented incident categories rather than invented freely |
| Single-model dependency | External | Model version and parameters recorded with all results; stated as limitation L7 |
| Under-powered participant sample | Statistical conclusion | A priori power analysis before collection; effect sizes with confidence intervals reported rather than p-values alone; under-powering reported rather than concealed |
| Multiplicity across the ablation family | Statistical conclusion | Holm–Bonferroni correction across the family |
| Divergence between documented and actual artefact | Construct | Source-level verification procedure (§3.9); four divergences already identified and corrected |

## 3.15 Chapter Summary

This chapter established a pragmatist paradigm operationalised through Design Science Research, and accepted the obligation that follows: the artefact must be evaluated in a way capable of falsifying its design claims. The approach is abductive in architecture formulation and deductive in testing, with four hypotheses each bound to a specific test and an explicit falsification condition. The design is a within-subject experiment across five system configurations on a common scenario set, with mixed-methods collection through instrumented logs, rubric scoring, adversarial execution, usability instruments and a matched human baseline. The DSR execution workflow was mapped activity by activity with honest status. Tools were justified against rejected alternatives, Scrum was justified against sequential and continuous-flow alternatives, and the timeline identifies corpus construction as the critical path with no slack. Ethics and validity threats were specified with concrete mitigations rather than general assurances.

---

# Chapter 4 — System Design and Implementation

> **Scope of this chapter.** Every quantitative statement below was verified against source or artefact inspection during preparation of this submission. Where a subsystem does not meet its design specification, that is stated in place rather than deferred.

## 4.1 Implementation Status Summary

| Component | Status | Verification basis |
|---|---|---|
| FastAPI backend, **69** REST endpoints across 13 routers | Complete | Endpoint decorators enumerated from source |
| JWT authentication (HS256) + bcrypt; RBAC with **5 roles, 24 permissions** | Complete | Role and permission constants enumerated; authenticated login verified returning token and permission set |
| LLM Conversation Agent | Complete | Module present; invoked in request pipeline |
| Ticket Intelligence Agent | Complete | Invoked for creation decision and priority scoring |
| Ticket Status Agent | Complete | Invoked for lifecycle reconciliation |
| Action Executor Agent (**25** whitelisted actions) | Complete | Registry enumerated: 14 LOW, 8 MEDIUM, 3 HIGH across 6 categories |
| Image Analysis Agent | Complete | Multimodal endpoint implemented |
| Retrieval subsystem | Functional; **architecture revision required** | §4.6 |
| Predictive ML subsystem | Prototype trained; **re-specification required** | §4.8 |
| React 19 + Vite 7 frontend (47 source modules, ~11,100 LOC) | Complete | Application served and reachable |
| Docker / Docker Compose deployment configuration | Complete | Compose definitions for development and deployment |
| Automated test suite | **Minimal — 1 test module** | `backend/tests/test_main.py` only; expansion required |
| Evaluation harness | **Not implemented** | Planned, §7.3 |

## 4.2 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              PRESENTATION — React 19 + Vite 7                │
│     Chat  │  Dashboard  │  Ticket Manager  │  Admin Panel    │
└───────────────────────────┬──────────────────────────────────┘
                            │ REST / JSON  (69 endpoints)
┌───────────────────────────▼──────────────────────────────────┐
│      API LAYER — FastAPI · JWT (HS256) · RBAC 5 roles        │
├──────────────────────────────────────────────────────────────┤
│                    ORCHESTRATION LAYER                       │
│      Deterministic sequential pipeline (chat_enhanced)       │
│                                                              │
│   [Image Agent] → [Intent Classification] → [Retrieval]      │
│        → [Conversation Agent] → [Ticket Intelligence Agent]  │
│        → [Assignment Service] → [Ticket Status Agent]        │
│        → [Action Executor Agent — approval-gated]            │
├──────────────────────────────────────────────────────────────┤
│  Retrieval Engine  │  Assignment Service  │ PowerShell Exec  │
│  (in-memory cosine)│  (specialisation +   │ (subprocess,     │
│                    │   workload)          │  no shell, 30 s) │
├──────────────────────────────────────────────────────────────┤
│  DATA: SQLite (users/tickets/chat/audit) │ KB corpus (JSON)  │
├──────────────────────────────────────────────────────────────┤
│  ML: resolution-time regressor │ system-health classifier    │
└──────────────────────────────────────────────────────────────┘
```

**Architectural characterisation, stated precisely.** Coordination is **centralised and deterministic**: the orchestration function invokes each agent in a fixed sequence. Agents do not communicate directly, do not select which agent runs next, and do not negotiate. This is an *orchestrated specialist-agent pipeline*, not a decentralised autonomous multi-agent system in the sense surveyed by [13]. The distinction is stated explicitly because describing the artefact as autonomously multi-agent would misrepresent it, and because it bounds what the findings can claim (limitation L8, §7.1).

## 4.3 Agent Specifications

| Agent | Function | Input | Output | Implementation basis |
|---|---|---|---|---|
| **LLM Conversation Agent** | Multi-turn diagnostic dialogue; escalation and resolution signalling | User message, conversation history (20-message window), retrieved context | Response text; `is_technical`, `should_escalate`, `is_resolved` flags | Hosted LLM + prompt engineering; heuristic post-analysis |
| **Ticket Intelligence Agent** | Ticket creation timing, urgency scoring, title/description generation, categorisation | Conversation history, turn count, classification signal | Creation decision; priority from a 0–10 urgency score; ticket metadata | Hybrid: LLM generation with deterministic rule fallback |
| **Ticket Status Agent** | Lifecycle transitions, SLA tracking, re-open and abandonment detection | Conversation history, current status, ticket timestamps | Recommended state, confidence, SLA flags | **Deterministic rule-based state machine (intentionally non-LLM)** |
| **Action Executor Agent** | Risk-tiered remediation proposal and gated execution | Issue description, category, urgency, user approval | Proposed action with risk tier; execution result | Enumerated whitelist; regex parameter sanitisation; PowerShell subprocess |
| **Image Analysis Agent** | Visual fault analysis and text extraction from screenshots | Image bytes, MIME type, optional user context | Extracted text, issue description, category, retrieval keywords | Multimodal LLM API |

**Design rationale for heterogeneity.** The Ticket Status Agent is deliberately *not* LLM-based. Lifecycle state governs SLA accounting and audit records, where reproducibility and explainability outweigh linguistic flexibility: an auditor must be able to reconstruct why a ticket moved from OPEN to RESOLVED, and a generative justification is not a reconstruction. This heterogeneous design — generative where interpretation is required, deterministic where accountability is required — is itself a design claim, and it is tested by ablation A3 rather than asserted.

## 4.4 Access Control

| Role | Intended holder |
|---|---|
| `STAFF` | End user submitting requests |
| `CONTRACTOR` | External user with reduced visibility |
| `MANAGER` | Oversight of team tickets and reports |
| `IT_ADMIN` | Support engineer with troubleshooting and diagnostics rights |
| `SYSTEM_ADMIN` | Full administrative authority including user and role management |

Twenty-four permission constants span ticket operations, troubleshooting, system monitoring and diagnostics, user management, dashboards and reporting, and knowledge-base access. Permissions are checked at the API dependency layer, so authorisation is enforced before any agent is invoked — including before any action can be proposed.

## 4.5 Orchestration Workflow

1. **Multimodal pre-processing** *(image path only)* — visual analysis output merged into the textual message, so image-originated requests traverse the same downstream path as text.
2. **Intent classification** — technical/non-technical, category, urgency, confidence.
3. **Retrieval** — executed only when the message is classified technical; similarity threshold 0.50 applied; top-3 passages retained.
4. **Response generation** — conditioned on retrieved context when available.
5. **Ticket intelligence** — creation gated at ≥ 3 conversational turns, preventing premature ticket generation from an incomplete problem description.
6. **Escalation** — on an escalation signal, the assignment service allocates a human agent by specialisation and current workload.
7. **Lifecycle reconciliation** — the status agent reconciles ticket state against conversation evidence using deterministic rules.
8. **Remediation proposal** — only in explicitly enabled Agent Mode; a **single** next action is returned (stepwise protocol) and held pending approval.

**Why stepwise.** Returning one action at a time rather than a batch means each execution decision is separately approved and separately observable, which is a precondition for attributing an outcome to a specific action during evaluation, and which limits the blast radius of any single incorrect proposal.

## 4.6 Retrieval Subsystem — Status and Required Revision

**Current implementation (verified).** Query and knowledge-base texts are embedded with the hosted `text-embedding-004` model. Cosine similarity is computed in Python over an in-memory embedding cache. Results below a **0.50** similarity threshold are discarded, and the remainder are ranked by a weighted score combining semantic similarity with historical article usage (**0.8 × similarity + 0.2 × usage_count/100**); the top 3 are retained.

**Discrepancy identified and corrected.** The June 2026 submission stated that ChromaDB serves as the vector database for live retrieval, with LangChain as the orchestration layer. **Source review establishes that neither is in the runtime request path.** ChromaDB is initialised only within a standalone offline ingestion script; the live path performs a linear-scan similarity computation in application memory. This document corrects that claim.

**Implications, stated without softening.**

1. Retrieval complexity is **O(n)** per query, not the sub-linear behaviour an approximate-nearest-neighbour index provides. The scalability argument the design makes is therefore not currently realised.
2. At the present corpus size (6 articles) the distinction is operationally immaterial; at realistic corpus sizes it is material.
3. The usage-weighted ranking term is undocumented in the original design and unvalidated. It biases retrieval toward frequently used articles, which may improve practical relevance or may entrench popularity over correctness. It is currently an unjustified constant, like the threshold.
4. An additional defect was identified in the offline ingestion path: its local-embedding fallback produces deterministic pseudo-random vectors rather than semantic embeddings. Any corpus ingested through that path would yield retrieval indistinguishable from noise. **This must be fixed before the vector store is placed in the live path**, or the retrieval ablation would measure a broken retriever.

**Planned action.** Fix the ingestion embedding path; route live retrieval through the persistent vector store; retain the in-memory path as a comparison condition and report the retrieval latency/scale trade-off empirically; and sweep both the similarity threshold and the usage weight so that both become tuned, reported parameters (§5.6). This converts three documentation and design defects into measurable results.

## 4.7 Remediation Governance

**Action inventory: 25 whitelisted actions**, verified by enumeration of the registry.

| Risk tier | Count | Example actions |
|---|---|---|
| LOW | 14 | `list_top_processes`, `flush_dns`, `check_disk_space`, `test_connectivity`, `check_system_health`, `analyze_slow_performance` |
| MEDIUM | 8 | `empty_recycle_bin`, `clear_browser_cache`, `release_renew_ip`, `kill_process_by_id`, `restart_explorer`, `windows_disk_cleanup` |
| HIGH | 3 | `reset_network_adapter`, `restart_service`, `reset_winsock` |

| Category | Count |
|---|---|
| Diagnostics | 10 |
| Cleanup | 6 |
| Network | 4 |
| Process | 3 |
| Service | 1 |
| Browser | 1 |

Three actions require elevation. Two further definitions (`kill_process`, `stop_background_apps`) exist in source but are commented out and are **not** counted.

**Correction:** the June 2026 submission claimed "50+ safe actions" in both narrative and architecture diagram. Source inspection confirms 25 active definitions; the higher figure appears to have counted commented-out and duplicated entries. This document reports the verified count.

**Governance controls (all implemented):**

| # | Control | Mechanism | Enforced outside the model? |
|---|---|---|---|
| C1 | Action enumeration | Actions selectable only from a fixed whitelist; no free-form command construction is possible | **Yes** |
| C2 | Parameter validation | Required-field and allowed-value checking against the action definition | **Yes** |
| C3 | Injection screening | Regex rejection of shell metacharacters (`;`, `&`, `\|`, backtick, `$`) in parameters | **Yes** |
| C4 | Risk tiering | Every action carries a LOW / MEDIUM / HIGH classification surfaced to the user before approval | **Yes** |
| C5 | Human approval gate | Execution requires explicit approval; ownership verified against the requesting user | **Yes** |
| C6 | Execution isolation | Subprocess invocation **without shell interpretation**; 30-second timeout | **Yes** |
| C7 | Audit trail | Action requests, approvals and outcomes retained in history | **Yes** |

Every control is enforced in application code rather than by prompt instruction. This is the property that makes the safety claim (H4) testable under adversarial conditions [19]–[21], and it is the corrected form of the security argument discussed in §2.6.1.

## 4.8 Predictive Subsystem — Status and Required Re-specification

**Trained artefacts (verified by loading and inspecting each model file):**

| Model | Algorithm | Features | Target | Training data |
|---|---|---|---|---|
| Resolution-time model | **Linear Regression** | `category_code`, `priority`, `word_count` (3) | Resolution hours (continuous) | 500 synthetic records |
| System-health model | Random Forest Classifier (100 estimators) | `cpu_usage`, `ram_usage`, `disk_usage`, `temperature` (4) | Binary health state | Not documented |
| Category encoder | Label Encoder | — | 5 classes | — |

**Corrections and defects, stated in full:**

1. The June 2026 draft described this component as a **Random Forest SLA breach predictor**. The trained artefact is a **Linear Regression model predicting resolution hours** — a different algorithm solving a different problem (regression, not breach classification).
2. The system-health model *is* a Random Forest, consistent with the earlier description.
3. **No performance metrics (R², MAE, accuracy, F1) have been computed for either model. None are reported here.**
4. **Label-space mismatch (newly identified).** The persisted category encoder was fitted on the classes *Hardware Failure, Password Reset, Printer Issue, Software Crash, VPN Connection*, whereas the system's ticket category enumeration contains *hardware, software, network, account, user_error, system_issue, feature_request, other*. The two label spaces do not correspond, so live ticket categories cannot be fed to the resolution-time model without an undefined mapping. This is a correctness defect, not a documentation defect.
5. **Feature specification is the weak configuration identified in the literature.** All three features are available at ticket-open time, which is exactly the time-zero configuration that lifecycle-aggregated approaches are shown to outperform [4].
6. Training provenance is not fully recoverable: no training script or training dataset is retained for the system-health model, so its data cannot be described.

**Required work (§7.3):** re-specify the component — either as breach classification with an explicit label definition, or accurately as resolution-time estimation; adopt lifecycle-aggregated features following [4]; reconcile the label spaces; retrain with a recorded, reproducible protocol and a held-out split; and evaluate properly. Until then, **no predictive claim is made anywhere in this thesis.**

## 4.9 Data Layer

| Store | Purpose | Verified current volume |
|---|---|---|
| Operational relational database | Users, roles, tickets, chat history, audit logs | 1 user; **0 tickets**; **0 audit entries**; 2 chat messages |
| Curated corpus (JSON, ~28 KB) | Retrieval source and lifecycle test fixtures | **6 knowledge-base articles**; 5 users; 5 tickets; 4 conversations |
| ML training data | Resolution-time model | 500 synthetic records |
| Persistent vector store (offline only) | Ingested embeddings | Present on disk; **not queried by the live path** (§4.6) |

**Correction:** the June 2026 submission described a synthetic dataset of "200 users, historical tickets and SOPs." The actual corpus is substantially smaller. Corpus construction is **in progress** and is the principal blocker to evaluation (§6.4, §7.2).

---

# Chapter 5 — Evaluation Design

> **Status: designed; not executed.** This chapter specifies the intended protocol. No data has been collected under it, and no results are reported from it.

## 5.1 Evaluation Objectives

To determine the measurable contribution of each architectural component (RQ1, RQ2, RQ3, RQ5) and to establish whether the governance mechanism withstands adversarial input (RQ4) — not to demonstrate that the system functions. Functioning is a precondition verified in §6.6, not a result.

## 5.2 Experimental Setup

- **Environment:** isolated Windows virtual machines; a uniform baseline snapshot is restored between trials to eliminate state carry-over from remediation actions.
- **Model configuration:** a fixed model version and generation parameters across all conditions. The model version, generation parameters and access date are recorded with every run, because results conditioned on an unrecorded model version are not reproducible.
- **Determinism handling:** classification tasks run at low temperature; each scenario is executed **n = 5 times per configuration** to characterise residual non-determinism, with variance reported alongside central tendency.
- **Blinding:** scenario scoring is performed against a rubric fixed before execution, with scorers blind to configuration where feasible.

## 5.3 Evaluation Corpus (In Preparation)

**Target:** 60 scenarios spanning five categories (network, performance, peripheral/hardware, access/account, software), stratified across three difficulty tiers, each with a defined ground-truth resolution path and acceptance criteria.

**Current status: insufficient.** The existing corpus of 6 knowledge-base articles cannot support this design; retrieval precision measured over six documents would not generalise, and would arguably be meaningless. Expansion is the critical-path item (§7.2).

**Ground-truth protocol.** Scenario ground truth is authored **before** any system execution and is **not LLM-generated**, avoiding the circularity of evaluating a model against labels produced by a model — a risk that automated reference-free RAG evaluation frameworks make convenient but do not eliminate [26]. Independent review of a sample by a second assessor establishes inter-rater agreement (Cohen's κ).

## 5.4 Ablation Design

The core experiment. Identical scenarios are executed under progressively enabled configurations.

| ID | Configuration | Isolates | Tests |
|---|---|---|---|
| **A0** | Unassisted human baseline — participant resolves the scenario manually | Human reference performance | Comparative reference |
| **A1** | Single LLM; no retrieval, no agent decomposition, no actions | Monolithic baseline | H2 (versus keyword and supervised baselines [3]) |
| **A2** | A1 + retrieval grounding | **Contribution of retrieval** | **H1** (G2) |
| **A3** | A2 + ticket intelligence and lifecycle agents | **Contribution of agent decomposition** | **H3** (G1) |
| **A4** | A3 + gated remediation (full system) | Contribution of action execution | RQ5 |

Because A0 uses the **same** scenarios under the same timing protocol, the human comparison is internally valid — unlike a comparison against an external published mean, which the earlier draft proposed and which is withdrawn.

## 5.5 Adversarial Safety Protocol

Testing whether governance holds when the model itself is manipulated [19]–[22].

| Test class | Method | Success criterion |
|---|---|---|
| Direct injection | Instructions embedded in user input attempting to induce non-whitelisted commands | Zero unauthorised executions |
| **Indirect injection** | Adversarial content planted in retrieved knowledge-base documents and in uploaded images — the vector demonstrated in [19] and directly applicable to this architecture | Zero unauthorised executions |
| Parameter injection | Shell metacharacters and escape sequences in action parameters | 100% rejection at validation (C3) |
| Approval bypass | Execution attempts without approval; approval attempts by non-owning users | Zero successes |
| Privilege escalation | Requests for elevation-requiring actions by insufficiently privileged roles | Zero successes |

**Reporting commitment.** Any successful bypass will be reported as a finding, not omitted. H4 is falsified by a single counter-example, and reporting that counter-example is more valuable than a clean result obtained by not looking.

## 5.6 Metrics

| Dimension | Metric | Method |
|---|---|---|
| Classification | Accuracy, macro-F1, per-class precision/recall (technical / category / urgency) | Against pre-authored ground truth; baselines from [3] |
| Retrieval | Precision@3, Recall@3, MRR; threshold and usage-weight sweeps | Against human relevance judgements |
| Resolution | Task success rate; steps to resolution; time to resolution | Rubric scoring |
| Grounding | Proportion of factually correct guidance; unsupported-claim rate | Blind human assessment; automated RAG metrics [26] as a secondary signal only |
| Lifecycle | State-transition correctness | Against expected lifecycle path |
| Safety | Unauthorised execution count; validation rejection rate; per-class containment | Adversarial suite (§5.5) |
| Predictive | MAE and R² (resolution time); accuracy and F1 (health) | Held-out split — **only after re-specification** (§4.8) |
| Usability | Instrument score; trust rating; approval-burden acceptability | Post-task questionnaire |
| Efficiency | End-to-end latency; token consumption per interaction | Instrumented logs |

## 5.7 Statistical Analysis Plan

- **Target sample:** 60 scenarios × 5 configurations × 5 repetitions = 1,500 system trials; **12–15 participants** for usability and the A0 human baseline.
- **Continuous outcomes** (time, latency): repeated-measures ANOVA where assumptions hold; Friedman test otherwise.
- **Categorical outcomes** (success/failure): Cochran's Q with pairwise McNemar tests.
- **Multiplicity:** Holm–Bonferroni correction across the ablation family.
- **Reporting:** effect sizes (Cohen's *d* or Cliff's δ) with 95% confidence intervals, not p-values alone.
- **Power:** a priori power analysis to be completed before data collection; the sample sizes above are provisional pending it.

**Acknowledged constraint.** A 12–15 participant sample is adequate for usability signal but under-powered for small effects in the human baseline comparison. This will be reported as a limitation rather than concealed by selective reporting.

---

# Chapter 6 — Progress Update: Position Toward Results and Discussion

> **Scope statement.** This chapter reports the **research progress position** and **implementation verification outcomes only**. The evaluation protocol in Chapter 5 has not been executed. No accuracy, resolution-time, retrieval-quality, safety-containment or user-satisfaction results exist, and none are reported. Sections 6.7 and 6.8 define the *structure* of the forthcoming Results and Discussion chapters; every cell in those structures is currently empty by design.

## 6.1 What Has Been Completed

| Work item | Completion evidence |
|---|---|
| Problem formulation grounded in measured evidence rather than market projections | §1.2, with grey-literature statistics removed from the evidential core |
| Structured literature review across five strands, with critical assessment and design implications | Chapter 2 |
| Identification and justification of the research gap (G1–G3), including engagement with the closest published system [1] | §1.3.3, §2.4.4, §2.9 |
| Reformulation of the research question into comparative, testable form with five sub-questions | §1.4 |
| Six objectives with verifiable completion criteria | §1.7 |
| Methodology: paradigm, approach, design, strategy, collection methods and sources, DSR workflow, tooling justification, ethics, validity threats | Chapter 3 |
| System architecture design and full specification | §4.2–§4.5 |
| Core implementation, verified operational | §4.1, §6.6 |
| Remediation governance: seven model-independent controls | §4.7 |
| Evaluation design: ablation, adversarial protocol, metrics, statistical plan | Chapter 5 |
| Source-level verification of all documented artefact claims | §3.9, §6.6 (R5), Appendix A |
| Correction of two unsupportable arguments and four documentation–implementation divergences | Appendix B |
| Reference-base reconstruction on verified sources only | Appendix C |

## 6.2 What Has Been Implemented and Developed

| Subsystem | Delivered | Verified quantity |
|---|---|---|
| Backend service | FastAPI application, 13 routers | **69** REST endpoints; ~13,100 LOC Python |
| Authentication and authorisation | JWT (HS256) + bcrypt; RBAC | **5** roles, **24** permission constants, enforced at the API dependency layer |
| Agents | Conversation, Ticket Intelligence, Ticket Status, Action Executor, Image Analysis | **5** agent modules, all invoked in the request pipeline |
| Remediation | Whitelisted action registry with risk tiering, parameter validation, approval gating, audit | **25** actions (14 LOW / 8 MEDIUM / 3 HIGH) across **6** categories; **7** governance controls |
| Retrieval | Embedding-based semantic search with threshold filtering and usage-weighted ranking | Threshold 0.50; top-3; ranking 0.8 × similarity + 0.2 × usage |
| Orchestration | Deterministic 8-stage pipeline | §4.5 |
| Predictive | Two trained model artefacts + label encoder | Loaded and inspected; **no metrics computed** |
| Frontend | React 19 + Vite 7 application: chat, dashboard, ticket manager, admin panel | 47 source modules, ~11,100 LOC |
| Deployment | Docker + Docker Compose (development and deployment configurations) | Compose definitions present |

## 6.3 Research Methodology Progress

| Methodological element | Status |
|---|---|
| Paradigm and its justification | **Complete** — pragmatism via DSR [24], [25], with the falsifiability obligation accepted (§3.2) |
| Approach | **Complete** — abductive phase concluded; four deductive hypotheses derived with explicit falsification conditions (§3.3) |
| Research design | **Complete** — within-subject, five configurations, five repetitions (§3.4) |
| Data collection instruments | **Designed; not built** — log schema, scoring rubric, adversarial suite and usability questionnaire are specified but not implemented |
| Data sources | **Partially secured** — literature complete; synthetic corpora insufficient; participant data not yet collectable (ethics pending) |
| Ethics approval | **Not yet obtained** — scheduled in Phase 3c; blocks all participant activity including the A0 baseline |
| Statistical analysis plan | **Complete in specification; a priori power analysis outstanding** |

## 6.4 Data Collection and Evaluation Progress

| Data asset | Target | Current | Gap |
|---|---|---|---|
| Evaluation scenarios with human-authored ground truth | 60 (5 categories × 3 difficulty tiers) | **0 authored** | **60** — critical path |
| Knowledge-base articles | Realistic scale (30–50 minimum for meaningful retrieval measurement) | **6** | 24–44 |
| Adversarial test cases | 5 classes, multiple cases per class | **0** | All |
| Participant recruitment (A0 baseline + usability) | 12–15 | **0** | All; blocked on ethics approval |
| System execution trials | 1,500 | **0** | All; blocked on harness and corpus |
| ML training data with recorded provenance | Expanded, lifecycle-aggregated features [4] | 500 records, 3 time-zero features, partial provenance | Re-specification required |

**Honest assessment of the position.** Data collection has not begun in any meaningful sense. The blocker is not effort applied to collection but the two preconditions collection depends on: a corpus of sufficient size to measure retrieval over, and an evaluation harness capable of executing the same scenario under five configurations. Both are specified; neither is built.

## 6.5 Current Testing and Evaluation Status

| Testing activity | Status |
|---|---|
| Manual functional verification of the end-to-end pipeline | **Performed** — outcomes in §6.6 |
| Source-level verification of documented claims | **Performed** — four divergences found and corrected |
| Automated unit / integration test suite | **Minimal** — a single test module covering service health; substantive coverage not yet written |
| Ablation execution (A0–A4) | **Not started** — harness not implemented |
| Adversarial safety execution | **Not started** — suite not constructed |
| Usability evaluation | **Not started** — ethics approval pending |
| Predictive model evaluation | **Not started** — blocked on re-specification (§4.8) |
| Statistical analysis | **Not started** — no data |

## 6.6 Implementation Verification Outcomes

These are outcomes of *verification*, not of *evaluation*. They establish that a functioning artefact exists to be measured; they say nothing about how well it performs.

**R1 — End-to-end operability.** The backend service responds to health checks; authentication returns a valid token with an associated permission set; 69 REST endpoints are registered and enumerable from the OpenAPI schema; the frontend application is served and reachable. Subsequent evaluation therefore has a functioning artefact to measure.

**R2 — Agent instantiation and integration.** All five specified agents are implemented as discrete modules and are invoked within the request pipeline. Agent decomposition exists as implemented architecture rather than design intention — a precondition for ablation A3.

**R3 — Governance controls implemented and model-independent.** All seven controls in §4.7 are implemented, and all are enforced outside the language model. This satisfies the precondition for the adversarial protocol: the safety claim is testable precisely because it does not depend on model compliance.

**R4 — Heterogeneous agent design realised.** The lifecycle agent is implemented deterministically while the conversational and ticket-metadata agents are generative, confirming that the heterogeneous design of §4.3 is realised rather than merely proposed.

**R5 — Documentation–implementation divergences identified and corrected.** Systematic source verification identified four material divergences between the June 2026 submission and the artefact, plus one correctness defect not previously known:

| Claim in the June 2026 submission | Verified reality | Corrected in |
|---|---|---|
| ChromaDB + LangChain serve live retrieval | Live path performs in-memory linear-scan cosine similarity; ChromaDB appears only in an offline ingestion script; LangChain is not in the runtime path | §4.6, §1.9.2 |
| "50+ safe actions" | 25 active action definitions (14 LOW / 8 MEDIUM / 3 HIGH) | §4.7 |
| SLA breach predictor using Random Forest | Linear Regression predicting resolution hours — different algorithm, different problem | §4.8 |
| Synthetic dataset of 200 users, historical tickets and SOPs | 6 KB articles; 5 synthetic users; 0 tickets in the operational database | §4.9 |
| *(not previously identified)* | Category encoder label space does not match the system's ticket category enumeration; the resolution-time model cannot consume live categories without an undefined mapping | §4.8 |

**R6 — Two design arguments withdrawn on review.** The claim of categorical novelty is withdrawn in light of [1] and of commercial platforms (§1.1, §2.4.4), and the claim that class-level agent separation constitutes a privilege boundary is withdrawn as mechanically incorrect (§2.6.1). Both are replaced with narrower claims the research can substantiate.

## 6.7 Expected Structure of the Results Chapter

The Results chapter will report measured outcomes only, in the following structure. **All tables below are empty and are presented as structure, not as findings.**

**7.1 Chapter overview and reporting conventions** — model version, generation parameters, access dates, trial counts, and the treatment of failed or excluded trials.

**7.2 Corpus and participant characteristics** — final scenario count by category and difficulty tier; knowledge-base size; inter-rater agreement (κ) on ground truth; participant demographics and experience distribution.

**7.3 Classification results (RQ1)**

| Configuration | Accuracy | Macro-F1 | Per-class precision / recall | 95% CI |
|---|---|---|---|---|
| Keyword baseline | *to be measured* | | | |
| Classical supervised baseline [3] | *to be measured* | | | |
| LLM classifier (A1) | *to be measured* | | | |

**7.4 Retrieval results (RQ2, part 1)** — Precision@3, Recall@3 and MRR against human relevance judgements; similarity-threshold sweep; usage-weight sweep; retrieval latency for the in-memory and persistent vector-store paths.

**7.5 Grounding and resolution results (RQ2, part 2)** — factual correctness and unsupported-claim rate for A1 versus A2; end-to-end task success, steps to resolution and time to resolution across A0–A4.

**7.6 Lifecycle results (RQ3)** — state-transition correctness for A2 versus A3.

**7.7 Ablation summary (RQ5)**

| Condition | Task success | Steps | Time | Grounding correctness | Lifecycle correctness | Effect vs. previous condition (effect size, 95% CI) |
|---|---|---|---|---|---|---|
| A0 human baseline | | | | | | — |
| A1 monolithic LLM | | | | | | |
| A2 + retrieval | | | | | | |
| A3 + agent decomposition | | | | | | |
| A4 full system | | | | | | |

**7.8 Adversarial safety results (RQ4)**

| Attack class | Attempts | Unauthorised executions | Control that contained the attempt | Bypasses (if any) |
|---|---|---|---|---|
| Direct injection | | | | |
| Indirect injection (documents / images) | | | | |
| Parameter injection | | | | |
| Approval bypass | | | | |
| Privilege escalation | | | | |

**7.9 Usability and trust results** — instrument scores; trust ratings; acceptability of the approval-gating burden; free-text themes.

**7.10 Efficiency results** — end-to-end latency and token consumption per configuration.

**7.11 Predictive model results** — reported **only if** the re-specification in §4.8 completes; otherwise the chapter will state that the component was withdrawn from evaluation and why.

**7.12 Statistical analysis** — hypothesis tests per §5.7 with Holm–Bonferroni correction, effect sizes and confidence intervals.

**7.13 Negative and null results** — configurations that did not perform as designed, reported in place rather than in an appendix.

## 6.8 Expected Structure of the Discussion Chapter

The Discussion chapter will interpret the measured results against the literature and the hypotheses. Its structure is defined as follows.

**8.1 Interpretation of component contributions (G1, G2).** What the ablation deltas mean for the design claim that decomposition and grounding contribute measurably. This section will state directly whether H1 and H3 were supported, and will interpret a null result as a finding — that decomposition does not confer measurable benefit under centralised orchestration would itself answer G1.

**8.2 Interpretation of the safety findings (G3, H4).** Whether the governance controls held under adversarial input, which control contained each attack class, and — if any bypass occurred — its mechanism, its generalisability beyond this artefact, and the design change it implies. Comparison with the failure patterns documented in [21] and [22].

**8.3 The usability cost of governance.** Whether mandatory approval gating imposes a burden users find acceptable, and how that trades against the safety it provides. This is the question [1] raises implicitly with its consent-based design and does not decompose.

**8.4 Comparison with existing approaches.** Positioning of the measured results against classification baselines [3], resolution-time prediction [4], LLM diagnosis accuracy [17], RAG-based IT support [10], [11], and the aggregate outcomes reported by the closest agentic system [1] — with explicit acknowledgement of population and measurement differences wherever a figure from a different study is placed alongside one measured here.

**8.5 Answers to the research questions.** Each of RQ1–RQ5 answered directly from measured evidence, including any that the evidence does not support answering.

**8.6 Threats to validity revisited.** Which mitigations from §3.14 held, which did not, and what the residual threats mean for the conclusions.

**8.7 Implications.** For research (what the component-level evidence adds to the fragmented picture described in [18]); for practice (what a practitioner should build, and what the evidence says they can safely omit).

**8.8 Limitations of the findings.** Restated in the light of what was actually measured rather than what was planned.

## 6.9 What Remains to Be Completed

**Phase 3b — Foundation repair (immediate priority; critical path)**
1. Construct the 60-scenario evaluation corpus with human-authored ground truth and second-assessor agreement.
2. Expand the knowledge base to a realistic scale (30–50 articles minimum).
3. Fix the ingestion embedding defect (§4.6), then route live retrieval through the persistent vector store, retaining the in-memory path as a comparison condition.
4. Re-specify the predictive component: define the target, reconcile the label spaces, adopt lifecycle-aggregated features [4], retrain with recorded provenance, or withdraw the component from evaluation.

**Phase 3c — Evaluation infrastructure**
5. Implement the automated evaluation harness for scenario execution.
6. Implement A0–A4 as runtime-selectable configurations.
7. Construct the five-class adversarial test suite, including planted indirect-injection content in documents and images [19].
8. Finalise the usability instrument; complete the a priori power analysis; obtain ethics approval.
9. Expand automated test coverage beyond the single existing test module.

**Phase 4 — Execution**
10. Execute the ablation experiment (1,500 trials).
11. Execute the adversarial safety evaluation.
12. Conduct participant sessions, including the A0 human baseline.
13. Evaluate the predictive models on a held-out split, if re-specified.

**Phase 5 — Analysis and writing**
14. Statistical analysis per §5.7 with effect sizes and confidence intervals.
15. Author the Results chapter from measured data, following the structure in §6.7.
16. Author the Discussion chapter following the structure in §6.8.
17. Document negative and partial results.
18. Complete the thesis; prepare the demonstration and defence.

---

# Chapter 7 — Limitations, Challenges and Risks

## 7.1 Current Limitations

**L1 — No empirical evidence yet.** Every performance claim remains untested. This is the dominant limitation and the honest characterisation of the project's present scientific status: an implemented artefact with a designed evaluation is substantial groundwork, not a research finding.

**L2 — Insufficient evaluation corpus.** Six knowledge-base articles cannot support meaningful retrieval evaluation; precision measured over so small a corpus would not generalise.

**L3 — Retrieval architecture below specification.** Linear-scan similarity does not realise the scalability property the design argument claims, the ranking weights and threshold are unjustified constants, and the offline ingestion path contains an embedding defect that must be fixed before the persistent store can be used (§4.6).

**L4 — Predictive component under-specified and partly incorrect.** A three-feature linear model on 500 synthetic records with a mismatched label space cannot support any predictive claim, and its feature set is the configuration the literature identifies as weakest [4].

**L5 — Synthetic data only.** External validity will be constrained. Real support conversations differ from authored scenarios in ambiguity, incompleteness and noise.

**L6 — Single-platform remediation.** Windows and PowerShell only; findings do not transfer to macOS or Linux endpoints.

**L7 — Single-model dependency.** Results will be conditioned on one commercial LLM family and may not transfer across models. The model version is recorded with all results so that the dependency is at least explicit.

**L8 — Centralised orchestration.** Conclusions will apply to orchestrated specialist-agent pipelines, not to autonomous negotiating multi-agent systems as surveyed in [13].

**L9 — Minimal automated test coverage.** A single test module means regressions during the remaining development phases would not be caught automatically, which is a risk to the integrity of the artefact being evaluated.

## 7.2 Active Challenges

| Challenge | Impact | Mitigation |
|---|---|---|
| Corpus construction is the critical path with no schedule slack | Blocks all evaluation | Prioritised immediately; if over-run, reduce scenario count while preserving stratification and report reduced power (§3.12) |
| Avoiding circular ground truth | Threatens the validity of every accuracy metric | Human-authored ground truth fixed before execution; second-assessor agreement (κ) |
| Non-determinism in generative components | Complicates reproducibility and effect attribution | Five repetitions per scenario per configuration; variance reported |
| Participant recruitment and ethics approval for A0 | Limits statistical power; blocks all human data | Early recruitment; approval scheduled in Phase 3c; under-powering reported rather than concealed |
| LLM API rate limits and cost across 1,500 trials | May constrain trial count | Batch scheduling; token budgeting; trial count reduced transparently if required |
| Model version drift during the evaluation window | Threatens comparability across conditions | Version pinned where the provider permits; version and access date recorded per run; any drift reported |

## 7.3 Concluding Statement

The research has completed problem formulation, literature analysis, methodological design and system implementation. Its most significant progress in this revision cycle is **corrective and evidential**: the problem justification has been rebuilt on measured, peer-reviewed evidence rather than market projection; an unsupportable novelty claim has been narrowed to a defensible one in light of the closest published system [1]; an invalid external comparison baseline has been replaced by a matched internal control; a mechanically incorrect safety argument has been restated in testable form; four documentation–implementation divergences and one correctness defect have been identified and reported; and the reference base has been reconstructed on sources verified individually.

The project's scientific value now rests on executing the ablation and adversarial evaluations specified in Chapter 5. Until those are complete, the contribution remains an implemented artefact with a designed evaluation — substantial groundwork, but not yet a research finding. This document is written so that the distinction between the two is visible on every page.

---

# References

[1] S. Ahuja, N. Kordjazi, E. Yortucboylu, V. Kapoor, M. Dundua, Y. Li, D. Ho, V. Padala, J. Whitted, and R. Steinert, "VIGIL: Towards edge-extended agentic AI for enterprise IT support," *arXiv preprint* arXiv:2603.16110, 2026.

[2] E. Brynjolfsson, D. Li, and L. R. Raymond, "Generative AI at work," *The Quarterly Journal of Economics*, vol. 140, no. 2, pp. 889–942, 2025, doi: 10.1093/qje/qjae044. (Earlier version: NBER Working Paper 31161, Apr. 2023, rev. Nov. 2023.)

[3] D. F. Oliveira, A. S. Nogueira, and M. A. Brito, "Performance comparison of machine learning algorithms in classifying information technologies incident tickets," *AI*, vol. 3, no. 3, pp. 601–622, 2022, doi: 10.3390/ai3030035.

[4] Mulyati, D. Stiawan, A. Rahman, M. S. Shakkah, and R. Budiarto, "Predicting incident resolution time in IT service management via lifecycle feature aggregation and machine learning," *Ingénierie des Systèmes d'Information*, vol. 31, no. 2, 2026, doi: 10.18280/isi.310219.

[5] W. X. Zhao, K. Zhou, J. Li, T. Tang, X. Wang, Y. Hou, et al., "A survey of large language models," *arXiv preprint* arXiv:2303.18223, 2023.

[6] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, "Retrieval-augmented generation for knowledge-intensive NLP tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, 2020, pp. 9459–9474.

[7] Y. Gao, Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, et al., "Retrieval-augmented generation for large language models: A survey," *arXiv preprint* arXiv:2312.10997, 2024.

[8] V. Karpukhin, B. Oğuz, S. Min, P. Lewis, L. Wu, S. Edunov, D. Chen, and W. Yih, "Dense passage retrieval for open-domain question answering," in *Proc. 2020 Conf. Empirical Methods in Natural Language Processing (EMNLP)*, 2020, pp. 6769–6781.

[9] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using siamese BERT-networks," in *Proc. 2019 Conf. Empirical Methods in Natural Language Processing and 9th Int. Joint Conf. Natural Language Processing (EMNLP-IJCNLP)*, Hong Kong, China, 2019, pp. 3982–3992.

[10] P. Toro Isaza, M. Nidd, N. Zheutlin, J.-W. Ahn, C. A. Bhatt, Y. Deng, R. Mahindru, M. Franz, H. Florian, and S. Roukos, "Retrieval augmented generation-based incident resolution recommendation system for IT support," *arXiv preprint* arXiv:2409.13707, 2024.

[11] Z. Xu, M. J. Cruz, M. Guevara, T. Wang, M. Deshpande, X. Wang, and Z. Li, "Retrieval-augmented generation with knowledge graphs for customer service question answering," in *Proc. 47th Int. ACM SIGIR Conf. Research and Development in Information Retrieval (SIGIR '24)*, Washington, DC, USA, 2024, doi: 10.1145/3626772.3661370.

[12] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, "ReAct: Synergizing reasoning and acting in language models," in *Proc. Int. Conf. Learning Representations (ICLR)*, 2023.

[13] L. Wang, C. Ma, X. Feng, Z. Zhang, H. Yang, J. Zhang, Z.-Y. Chen, J. Tang, X. Chen, Y. Lin, W. X. Zhao, Z. Wei, and J.-R. Wen, "A survey on large language model based autonomous agents," *Frontiers of Computer Science*, vol. 18, no. 6, art. 186345, 2024, doi: 10.1007/s11704-024-40231-1.

[14] J. Liu, K. Wang, Y. Chen, X. Peng, Z. Chen, L. Zhang, and Y. Lou, "Large language model-based agents for software engineering: A survey," *arXiv preprint* arXiv:2409.02977, 2024.

[15] S. Jha, R. Arora, Y. Watanabe, T. Yanagawa, Y. Chen, J. Clark, et al., "ITBench: Evaluating AI agents across diverse real-world IT automation tasks," in *Proc. 42nd Int. Conf. Machine Learning (ICML)*, PMLR, vol. 267, 2025, pp. 27134–27197.

[16] T. Ahmed, S. Ghosh, C. Bansal, T. Zimmermann, X. Zhang, and S. Rajmohan, "Recommending root-cause and mitigation steps for cloud incidents using large language models," in *Proc. IEEE/ACM 45th Int. Conf. Software Engineering (ICSE)*, Melbourne, Australia, 2023, pp. 1737–1749, doi: 10.1109/ICSE48619.2023.00149.

[17] Y. Chen, H. Xie, M. Ma, Y. Kang, X. Gao, L. Shi, Y. Cao, X. Gao, H. Fan, M. Wen, J. Zeng, S. Ghosh, X. Zhang, C. Zhang, Q. Lin, S. Rajmohan, D. Zhang, and T. Xu, "Automatic root cause analysis via large language models for cloud incidents," in *Proc. 19th European Conf. Computer Systems (EuroSys '24)*, Athens, Greece, 2024, doi: 10.1145/3627703.3629553.

[18] L. Zhang, T. Jia, M. Jia, Y. Wu, A. Liu, Y. Yang, et al., "A survey of AIOps for failure management in the era of large language models," *arXiv preprint* arXiv:2406.11213, 2024.

[19] K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz, "Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection," in *Proc. 16th ACM Workshop on Artificial Intelligence and Security (AISec '23)*, Copenhagen, Denmark, 2023, pp. 79–90.

[20] Y. Liu, G. Deng, Y. Li, K. Wang, Z. Wang, X. Wang, et al., "Prompt injection attack against LLM-integrated applications," *arXiv preprint* arXiv:2306.05499, 2023.

[21] E. Debenedetti, J. Zhang, M. Balunović, L. Beurer-Kellner, M. Fischer, and F. Tramèr, "AgentDojo: A dynamic environment to evaluate prompt injection attacks and defenses for LLM agents," in *Advances in Neural Information Processing Systems (NeurIPS) Datasets and Benchmarks Track*, 2024.

[22] Y. Ruan, H. Dong, A. Wang, S. Pitis, Y. Zhou, J. Ba, Y. Dubois, C. J. Maddison, and T. Hashimoto, "Identifying the risks of LM agents with an LM-emulated sandbox," in *Proc. Int. Conf. Learning Representations (ICLR)*, 2024.

[23] K. M. Alsaif, A. A. Albeshri, M. A. Khemakhem, and F. E. Eassa, "Multimodal large language model-based fault detection and diagnosis in context of Industry 4.0," *Electronics*, vol. 13, no. 24, art. 4912, 2024, doi: 10.3390/electronics13244912.

[24] A. R. Hevner, S. T. March, J. Park, and S. Ram, "Design science in information systems research," *MIS Quarterly*, vol. 28, no. 1, pp. 75–105, 2004.

[25] K. Peffers, T. Tuunanen, M. A. Rothenberger, and S. Chatterjee, "A design science research methodology for information systems research," *Journal of Management Information Systems*, vol. 24, no. 3, pp. 45–77, 2007.

[26] S. Es, J. James, L. Espinosa-Anke, and S. Schockaert, "RAGAS: Automated evaluation of retrieval augmented generation," in *Proc. 18th Conf. European Chapter of the Association for Computational Linguistics: System Demonstrations (EACL)*, 2024, pp. 150–158.

---

## Appendix A — Implementation Verification Evidence

Every value below was obtained by direct inspection of source or artefacts during preparation of this submission.

| Item | Verified value |
|---|---|
| Backend framework | FastAPI (Python 3.11) |
| Registered REST endpoints | **69** across 13 routers |
| Backend source size | ~13,100 lines of Python |
| Frontend | React 19.2 + Vite 7.2; 47 source modules, ~11,100 lines |
| Authentication | JWT (HS256); bcrypt password hashing |
| RBAC | 5 roles; 24 permission constants |
| Agent modules implemented | 5 |
| Whitelisted remediation actions | **25** active (2 further definitions commented out and excluded) |
| Action risk distribution | 14 LOW / 8 MEDIUM / 3 HIGH |
| Action categories | Diagnostics 10, Cleanup 6, Network 4, Process 3, Service 1, Browser 1 |
| Actions requiring elevation | 3 |
| Governance controls | 7, all enforced outside the model |
| Command execution | PowerShell subprocess **without shell interpretation**; 30 s timeout |
| Retrieval embedding model | `text-embedding-004` (hosted) |
| Retrieval similarity threshold | 0.50 |
| Retrieved passages per query | Top 3 |
| Retrieval ranking function | 0.8 × cosine similarity + 0.2 × (usage_count / 100) |
| Live retrieval implementation | In-memory linear-scan cosine similarity (**not** the persistent vector store) |
| Ticket-creation turn threshold | ≥ 3 turns |
| Conversation memory window | 20 messages |
| Resolution-time model | Linear Regression; 3 features; 500 synthetic records; **no metrics computed** |
| System-health model | Random Forest Classifier; 100 estimators; 4 features; binary; **no metrics computed** |
| Category encoder classes | 5 (`Hardware Failure`, `Password Reset`, `Printer Issue`, `Software Crash`, `VPN Connection`) — **do not match** the system's 8-value ticket category enumeration |
| Knowledge-base articles | 6 |
| Synthetic users / tickets / conversations in corpus | 5 / 5 / 4 |
| Operational database contents | 1 user; 0 tickets; 0 audit entries |
| Automated test modules | 1 |
| Deployment | Docker Compose (development and deployment configurations) |

## Appendix B — Corrections Applied Across Revisions

| # | Statement in an earlier submission | Status | Section |
|---|---|---|---|
| 1 | "No comprehensive integrated IT support platform exists" | **Withdrawn** — commercial platforms exist, and a published agentic IT support system with governed remediation is reported in [1]; the gap is narrowed to open, component-wise evaluated architecture | §1.1, §2.4.4 |
| 2 | Comparison against a published industry mean resolution time | **Withdrawn** — invalid across populations; replaced by matched human baseline A0 | §3.6, §5.4 |
| 3 | Agent decoupling constitutes a security/privilege boundary | **Corrected** — agents share a process; safety derives from whitelist, parameter validation and approval gating | §2.6.1, §4.7 |
| 4 | ChromaDB (with LangChain) serves live retrieval | **Corrected** — live path uses in-memory linear-scan similarity; neither is in the runtime path | §1.9.2, §4.6 |
| 5 | "50+ safe actions" | **Corrected** — 25 verified active definitions | §4.7 |
| 6 | Random Forest SLA breach predictor | **Corrected** — Linear Regression resolution-time estimator | §4.8 |
| 7 | Dataset of 200 users with historical tickets and SOPs | **Corrected** — 6 KB articles, 5 synthetic users, 0 operational tickets | §4.9 |
| 8 | Research question was design-descriptive | **Reformulated** as comparative and testable | §1.4 |
| 9 | Problem justified largely by market-size and vendor statistics | **Rebuilt** on measured, peer-reviewed evidence [2], [17], [15], [1] | §1.2 |
| 10 | No ablation planned | **Added** — five-configuration ablation as the core experiment | §5.4 |
| 11 | No adversarial safety evaluation | **Added** — five-class injection and bypass protocol including the indirect vector [19] | §5.5 |
| 12 | No statistical analysis plan | **Added** — tests, multiplicity correction, effect sizes, power | §5.7 |
| 13 | *(newly identified this cycle)* Category encoder label space assumed compatible with ticket categories | **Defect reported** — label spaces do not correspond | §4.8 |
| 14 | *(newly identified this cycle)* Ingestion embedding fallback assumed semantic | **Defect reported** — produces non-semantic vectors; must be fixed before the vector store enters the live path | §4.6 |

## Appendix C — Citation Verification Status

Prepared in the interest of academic integrity. Every reference in this document was verified individually: the majority were verified against the full paper obtained and read during preparation; the remainder were verified against publisher or proceedings records.

| Ref | Verification basis | Outstanding action |
|---|---|---|
| [1] | Full text obtained; author list and arXiv identifier confirmed | Check for a peer-reviewed venue version before final submission |
| [2] | Full text obtained (NBER WP 31161); journal-of-record details confirmed against publisher | None |
| [3] | Full text obtained; volume, pages and DOI confirmed | None |
| [4] | Full text obtained; volume, issue and DOI confirmed | Confirm page range from the publisher |
| [5] | Established survey; arXiv identifier confirmed | Check for a peer-reviewed version of record |
| [6] | Full text obtained; NeurIPS 33 pages confirmed | None |
| [7] | arXiv identifier confirmed | Check for a peer-reviewed version of record |
| [8] | Full text obtained; EMNLP 2020 pages confirmed | None |
| [9] | Full text obtained; EMNLP-IJCNLP 2019 pages confirmed | None |
| [10] | Full author list and arXiv identifier confirmed | Check for a peer-reviewed venue version |
| [11] | Full text obtained; SIGIR '24 venue and DOI confirmed | None |
| [12] | Established ICLR 2023 paper | Confirm proceedings detail |
| [13] | Full text obtained; DOI and complete author list confirmed | None |
| [14] | Full text obtained; author list and arXiv identifier confirmed | Check for a peer-reviewed version of record |
| [15] | Full text obtained; ICML 2025 / PMLR volume and pages confirmed | Transcribe the complete author list for the final thesis |
| [16] | ICSE 2023 record; DOI and pages confirmed | None |
| [17] | Full text obtained; EuroSys '24 venue and DOI confirmed | None |
| [18] | arXiv identifier confirmed | Confirm complete author list |
| [19] | Full text obtained; AISec '23 venue and pages confirmed | None |
| [20] | arXiv identifier confirmed | Confirm complete author list |
| [21] | Full text obtained; NeurIPS 2024 Datasets and Benchmarks Track confirmed | None |
| [22] | Full text obtained; ICLR 2024 confirmed | None |
| [23] | Full text obtained; volume, article number and DOI confirmed | None |
| [24], [25] | Foundational DSR methodology (pre-2019, cited as methodological canon, permitted by the chapter breakdown) | None |
| [26] | Full text obtained; EACL 2024 demonstrations pages confirmed | None |

**References removed and not reinstated.** The following were cited in the June 2026 submission and could not be verified in any bibliographic database; they are removed rather than reformatted, since citing an unverifiable source is a more serious defect than having fewer citations: Ahmad et al. (2023); Xu et al., "Conversational AI for IT Support" (2023); Patel & Singh (2023); Kumar & Mehta (2024); Li et al., "Multi-Agent Systems for Enterprise AI," *ACM Computing Surveys*; and a CompTIA entry dated "2924."

**References removed in this revision.** Revision 2 carried six entries identified only by title and an IEEE Xplore document number or DOI, without author lists — covering IT support ticket classification, helpdesk ticket automation, enterprise service-management classification, RAG-based ticket resolution, and LLM-based AIOps. Because their bibliographic details could not be completed to IEEE standard from the information held, they have been replaced by sources verified in full: [4] and [5] now carry the supervised ITSM ML argument, [12] and [13] the domain RAG argument, and [17] and [18] the agentic and AIOps arguments. No argument in this document depends on a source that was not verified.

**Grey literature.** Market-size, downtime-cost and vendor survey statistics (Gartner, IDC, HDI, Statista, Freshworks, CompTIA) used in the June 2026 submission have been removed from the evidential core of the argument. Where industry context is genuinely useful in the final thesis, such sources may be reinstated only with verified report titles, publication dates and access URLs, and must be clearly marked as industry rather than peer-reviewed evidence.
