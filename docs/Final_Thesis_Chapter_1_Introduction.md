# CHAPTER 1 — INTRODUCTION

**Thesis title:** Context-Aware Intelligent IT Support: A Multi-Agent LLM Framework with Knowledge-Grounded Troubleshooting and Human-Gated Automated Remediation

**Author:** P. T. N. Pathirana (28647) · NSBM Green University Town

> **Citation numbering.** References are numbered [1]–[27] in IEEE order of first appearance across Chapters 1–3. A crosswalk to the numbering used in Interim Submission 01 (Revision 3) is provided in the accompanying reference document.

---

## 1.1 Chapter Overview

This chapter establishes the foundation of the research. It develops, in sequence, the context in which the problem arises, the evidence that the problem is both economically consequential and technically unsolved, the specific deficiencies that remain in the literature, and the aim, objectives and questions through which this study responds to them.

The argument proceeds deliberately from the general to the particular. Section 1.2 sets out the research context — the delivery of enterprise IT support, the measured effect of generative assistance on support productivity, the state of academic automation in this domain, the technological developments that make end-to-end automation newly plausible, the benchmark evidence that it nevertheless remains largely unachieved, and the adversarial exposure that any system permitted to act must survive. Section 1.3 converts that context into a general problem, five specific problems and a precisely bounded research gap. Section 1.4 states the primary research question and its five sub-questions in comparative and testable form; §1.5 states the motivation; §1.6 the aim; and §1.7 six objectives, each with a verifiable completion criterion. Section 1.8 presents a rich picture of the proposed solution, *Auto-Ops-AI*. Sections 1.9 to 1.13 state the resource requirements, the scope boundary, the significance of the work, its delimitations and limitations, and the structure of the remainder of the thesis. Section 1.14 summarises the chapter.

Two positions adopted throughout the thesis are stated here at the outset, because they shape how every later claim is framed. First, **the contribution claimed is architectural evidence, not categorical novelty.** Integrated systems that combine conversational AI, retrieval over enterprise knowledge and governed remediation already exist, both commercially and — as of 2026 — in the peer-reviewable literature as an industrial pilot, examined in §1.2.4 and §2.5.4. What does not exist is an openly specified, component-wise evaluated reference design for such a system. Second, **the safety of an acting system is claimed only for mechanisms enforced outside the language model.** The reasoning behind this is developed in §1.2.5 and §2.7.2, but its consequence is immediate: no safety property asserted in this thesis rests on a model following an instruction.

---

## 1.2 Background and Research Context

### 1.2.1 The Broader Research Context

Organisational productivity now depends on IT infrastructure that is heterogeneous by construction — cloud services, on-premises systems, diverse endpoints and layered software stacks — and the support function that keeps this infrastructure usable has become a bottleneck of organisational rather than merely technical significance. Support capacity is bounded by the number of trained engineers an organisation can employ, while the demand placed upon it grows with the number of devices, services and integrations under management. The two quantities do not scale together, and the gap between them is absorbed as queuing delay, deferred resolution and displaced staff productivity.

The relevance of automating this function is not speculative. In the largest field study of generative artificial intelligence in a support setting conducted to date, Brynjolfsson, Li and Raymond observed the staggered rollout of a generative-AI conversational assistant to **5,172 customer-support agents** and measured an increase in productivity, defined as issues resolved per hour, of **approximately 15% on average** [1]. Three features of that result are decisive for the present research.

First, the effect was strongly heterogeneous: less experienced and lower-skilled workers improved in both speed and quality, while the most skilled agents gained little in speed and showed slight quality declines [1]. The authors attribute this pattern to the diffusion of *tacit knowledge* — the working practice of high performers becoming accessible to everyone else. The improvement is therefore an improvement in **knowledge access**, not in raw generative fluency, and this distinction determines what an effective support architecture must optimise.

Second, the gains were largest for problems of moderate rarity — those where the individual agent lacked personal experience but the system had adequate precedent to draw on [1]. This is precisely the profile of the recurrent-but-not-trivial incident that dominates enterprise support queues.

Third, and most importantly for this thesis, the assistant that produced these gains **recommended; it did not act**. The measured 15% therefore represents the value of better advice delivered to a human who must still perform the work. Whether that residual work can itself be automated — and under what governance it would be safe to do so — is an open question that the study does not address and that this research takes as its subject.

This is the empirical anchor of the research. Assistance that improves knowledge access measurably improves support work; the design of that assistance — how knowledge is retrieved, how advice is grounded, and whether the system may act on it — is therefore a question with demonstrated practical stakes rather than an assumed one.

### 1.2.2 The Current Situation and Its Documented Shortcomings

IT Service Management (ITSM) is the body of practice through which organisations deliver, support and improve IT services, structured around defined processes — incident management, request fulfilment, problem management and change management — and instrumented by ticketing systems and service-level agreements. A systematic review of 47 studies characterises ITSM adoption as delivering real benefits in service quality and process standardisation while simultaneously documenting persistent implementation challenges, notably process rigidity, the cost of maintaining process discipline, and difficulty in sustaining the knowledge assets on which the processes depend [2]. That last challenge is directly germane here: the frameworks presuppose documented, current, findable resolution knowledge, and the reviewed literature records that maintaining it is among the hardest parts of ITSM in practice [2].

Operationally, support is delivered through tiered human workflows (L1 → L2 → L3) mediated by ticketing systems. This arrangement controls cost, because inexpensive generalists filter work before it reaches expensive specialists, but it imposes two structural penalties: queuing delay at each tier, and repeated context-gathering at each handoff, since the information a user supplied at L1 is rarely sufficient for L2 and must be re-elicited. A substantial fraction of the resulting workload is repetitive — credential and access problems, network and VPN connectivity faults, endpoint performance degradation, and peripheral or driver failures recur continuously — and the resolutions to much of it are already documented inside the organisation's own records. The problem is therefore not primarily one of missing knowledge but of the cost of locating, interpreting and applying existing knowledge on every recurrence, which is the same diagnosis the productivity evidence in §1.2.1 supports from the opposite direction [1].

The academic response to this repetitiveness has, for the most part, taken the form of supervised classification. Oliveira, Nogueira and Brito compare six supervised algorithms for classifying IT incident tickets and report that a linear support vector classifier reaches **93.12% accuracy** on their Portuguese-language corpus, ahead of stochastic gradient descent (90.01%), logistic regression (88.65%) and multinomial naïve Bayes (85.03%), with random forest and k-nearest neighbours performing worst [3]. Two of their secondary findings matter more than the headline figure: oversampling materially improved results, and the smaller Spanish and English datasets, to which oversampling was not applied, performed appreciably worse [3]. Automated ticket categorisation is therefore substantially achievable, but its accuracy is contingent on corpus size and on explicit treatment of class imbalance rather than being an intrinsic property of the method.

Related work extends supervised learning from categorisation to timing. Mulyati et al. show that predicting incident resolution time improves substantially when features are aggregated across the incident lifecycle rather than taken at ticket-open time alone: their lifecycle-aggregated model attains **R² = 0.8318** with a mean absolute error of 60.67 hours, against **R² = 0.5412** for the non-aggregated configuration [4]. Process-derived features such as the number of system modifications, the assignment group and reassignment frequency proved considerably more predictive than the attributes available when the ticket was first raised [4].

The structural limitation shared by this body of work is that **the model is a terminal artefact**. A ticket is classified, or a duration is predicted, and the process ends. The classifier does not participate in diagnosis, does not consult resolution knowledge, and does not act. Reported accuracies, however high, are consequently not evidence that support automation is solved; they measure a sub-task that sits upstream of the work a support engineer actually performs.

### 1.2.3 The Technological Opening

Three developments make the end-to-end problem newly tractable. Each is accompanied by a documented limitation that constrains how it can responsibly be used, and it is the pairing of capability with limitation — not the capability alone — that shapes the design proposed in this thesis.

**Large language models.** Contemporary LLMs demonstrate multi-step reasoning and sustained instruction-following, capabilities that emerge with scale and are further shaped by adaptation tuning [5]. The property that matters for IT support is *conditional adaptation*: selecting the next diagnostic step from the reported outcome of the previous one. A fixed decision tree cannot do this beyond the branches its author anticipated; a model that reasons over dialogue state can. The corresponding weakness is equally well documented — fluent generation of confident but factually incorrect content [5] — and in this domain that weakness has consequences beyond a poor answer, because an incorrect instruction may be carried out on a user's machine.

**Retrieval-augmented generation.** RAG conditions generation on documents retrieved from a trusted corpus, pairing the model's parametric knowledge with an explicit non-parametric memory that can be inspected and updated without retraining [6]. The approach has since matured into a substantial design space of retrieval, ranking and integration strategies, surveyed by Gao et al. across naïve, advanced and modular paradigms and motivated explicitly by hallucination, knowledge staleness and untraceable reasoning [7]. Its retrieval component rests on dense representation learning: dual-encoder passage retrieval trained from limited question–passage supervision substantially outperforms sparse lexical baselines on top-k retrieval accuracy [8], and siamese sentence-embedding networks make large-scale semantic similarity computationally tractable by permitting passages to be encoded independently and compared by cosine distance [9]. Applied to IT support specifically, Toro Isaza et al. combine retrieval over historical incident resolutions with generative recommendation, addressing explicitly the domain-coverage and model-size constraints that arise when enterprises decline larger proprietary models on cost and privacy grounds [10]; and Xu et al., working on LinkedIn's customer-service corpus, show that treating past tickets as flat text discards intra-issue structure and inter-issue relations, and that constructing a knowledge graph over historical issues improves both retrieval and downstream answer quality [11].

**Agent architectures.** Rather than a single model performing every function, the agentic paradigm decomposes a task across components that reason, act, observe the outcome and iterate. The ReAct formulation established that interleaving reasoning traces with actions allows a model to induce and revise plans while interfacing with external sources, and demonstrated substantial gains on interactive decision-making benchmarks [12]. Wang et al. survey LLM-based autonomous agents and formalise their construction around profiling, memory, planning and action [13], while Liu et al. survey 124 studies applying LLM-based agents across software engineering activities and document both the breadth of adoption and the open challenges that remain [14]. For the present research the decomposition matters for governance at least as much as for capability: it creates explicit, nameable boundaries at which policy can be enforced.

### 1.2.4 Why the Problem Remains Unsolved

The availability of these technologies has not produced solved IT support automation. The evidence for that statement is direct and measured rather than rhetorical.

The clearest measurement comes from ITBench, a benchmark of 102 real-world IT automation scenarios spanning site reliability engineering, compliance and security operations, and financial operations. Agents built on state-of-the-art models resolve **11.4% of SRE scenarios**, **25.2% of compliance and security-operations scenarios** and **25.8% of financial-operations scenarios**, with anomaly-detection tasks reaching an F1 of only 0.35 [15]. These are not marginal shortfalls to be closed by a larger model; they indicate that composing capable components into a system that reliably completes realistic IT work is itself an unsolved problem.

Domain-specific studies converge on the same picture one tier closer to the support desk. Ahmed et al. evaluate large language models for recommending root causes and mitigation steps for cloud incidents at industrial scale and find meaningful assistance but performance short of autonomous reliability [16]. Chen et al.'s RCACopilot — a production on-call system at Microsoft that matches an incident to a handler and aggregates critical runtime diagnostic information *before* invoking the model — reports root-cause categorisation accuracy of **up to 0.766** over a year of real Microsoft incidents [17]. A system that is correct roughly three times in four is a valuable assistant and an unacceptable autonomous actor. The distance between those two roles is precisely where the research question of this thesis is located.

Recent work has begun to close part of that distance and, in doing so, sharpens rather than removes the research opportunity. VIGIL, an edge-extended agentic system for enterprise IT support, deploys desktop-resident agents that perform situated diagnosis, retrieval over enterprise knowledge and **policy-governed remediation on user devices with explicit consent** and end-to-end observability. A ten-week pilot on 100 resource-constrained endpoints reports a **39% reduction in interaction rounds**, at least **fourfold faster diagnosis**, and **self-service resolution in 82% of matched cases**, alongside favourable usability, trust and cognitive-workload results across four validated instruments [18].

This result is important to the present research in two opposing ways, and both are accepted here rather than minimised. It confirms that consent-gated on-device remediation is a viable and valuable design direction, so the design premise of this thesis is supported by evidence rather than assumed. It equally confirms that the direction is **under-characterised**: a single industrial pilot establishes that an integrated system can work in one deployment; it does not establish *which architectural components produce the effect*. The paper's own observation that users rated the system higher when no historical knowledge-base match was available [18] is a direct illustration of why decomposition matters — it suggests the contribution of retrieval to perceived value is not monotonic and cannot be inferred from an aggregate outcome.

Field-level syntheses reach the same conclusion from the opposite direction. Zhang et al.'s survey of AIOps in the era of large language models analyses 183 articles published between January 2020 and December 2024 and documents rapid expansion of LLM application across failure-management tasks alongside fragmented architectures, uneven data practices and inconsistent evaluation methodology [19]. The field is producing systems faster than it is producing comparable evidence about them.

### 1.2.5 The Safety Dimension of Acting Systems

A support system that executes commands on user machines consumes untrusted input by construction — user prose, pasted logs, error text, screenshots — and is therefore exposed to prompt injection.

Greshake et al. established that adversarial instructions need not originate with the user at all: content *retrieved* by an LLM-integrated application can itself carry the attack. This **indirect** injection vector applies directly to any system that performs retrieval over a corpus it does not fully control, and the authors demonstrate compromise of real deployed applications [20]. Liu et al. reinforce the empirical breadth of the exposure: applying a black-box injection technique to 36 real-world LLM-integrated applications, they found **31 to be vulnerable**, with ten vendors subsequently confirming the findings [21].

Where a model is permitted to call tools, the exposure changes character from an information risk to an execution risk. AgentDojo, an evaluation environment populated with **97 realistic tool-using tasks and 629 security test cases**, finds that existing attacks break some security properties while existing defences close some but not all, and that state-of-the-art models fail a substantial share of tasks even with no adversary present [22]. ToolEmu makes the complementary methodological point that identifying such risks by hand does not scale: using an LM-emulated sandbox over 36 high-stakes toolkits and 144 test cases, its authors find that **68.8% of the failures it surfaces are judged by human evaluators to be valid real-world agent failures**, and that even the safest agent evaluated fails 23.9% of the time [23].

Read together, these four results support a single design conclusion, which this research adopts as an axiom rather than a preference:

> **Safety for an acting system cannot rest on model behaviour, because the model is the component under attack.** It must rest on mechanisms that continue to hold even when the model is fully compromised.

A defence expressed as a system-prompt instruction is defeated by an injection that rewrites the instruction. A defence expressed as an enumerated whitelist in application code is not, because no persuasion of the model can expand the set of operations the application is capable of executing.

### 1.2.6 Summary of the Background Argument

The chain of reasoning that motivates this research can now be stated compactly. Measured field evidence establishes that knowledge-access assistance improves support productivity by approximately 15%, concentrated among less experienced workers, from a system that advises rather than acts [1]. ITSM practice depends on resolution knowledge whose maintenance and application are documented as persistent difficulties [2]. The academic literature automates upstream sub-tasks in isolation — categorisation [3] and resolution-time prediction [4] — leaving the model as a terminal artefact. The enabling technologies for end-to-end support are individually mature: conditional reasoning [5], retrieval grounding [6]–[11] and agent decomposition [12]–[14]. Benchmark and production evidence nevertheless shows that the composed task is largely unachieved, at 11.4% resolution on realistic SRE scenarios [15] and a 0.766 accuracy ceiling in a deployed root-cause system [17]. A recent industrial pilot demonstrates that governed remediation is viable and valuable but reports aggregate outcomes without decomposing them [18], within a field that surveys characterise as fragmented and inconsistently evaluated [19]. And any system that acts must be governed by model-independent controls, because the adversarial exposure is demonstrated, practical and applies specifically to retrieval-based architectures [20]–[23].

What is missing is therefore not a further demonstration that such a system can be built. What is missing is **open, component-level evidence about which architectural decisions matter, and under what governance action-taking becomes acceptably safe.**

---

## 1.3 Problem Statement

### 1.3.1 The General Problem

Organisations cannot scale human IT support linearly with demand. The repetitive fraction of support work consumes skilled capacity that could otherwise be applied to novel and complex incidents, and the knowledge required to resolve much of that repetitive work already exists within the organisation but is costly to locate, interpret and apply on every recurrence [1], [2].

Automation attempts to date resolve this only partially, and they fail at opposite ends of the same axis. Systems that restrict themselves to information retrieval are safe but shallow: they terminate at a recommendation the user must still carry out, leaving the residual manual effort — which is frequently the larger part of the total effort — untouched. Systems that extend into action-taking are useful but, in the published literature, are not accompanied by governance evidence adequate to justify production deployment. The measured resolution rates on realistic IT tasks — 11.4% of SRE scenarios for agents built on state-of-the-art models [15] — indicate that the deficiency is **architectural rather than merely a matter of model capability**, because the same models perform far better on isolated reasoning tasks than on composed operational ones.

### 1.3.2 The Specific Problems

Within the ITSM domain, this research targets five specific and evidenced shortcomings.

**P1 — Shallow conversational capability.** Intent-classification and decision-tree support bots handle single-turn deflection adequately but degrade in multi-turn, context-dependent diagnosis, where the correct next step depends on the outcome of the previous one. The capability required is conditional reasoning over accumulated dialogue state [5], [12], not intent lookup against a fixed taxonomy.

**P2 — Ungrounded generation.** Assistants that generate advice without retrieval from organisational knowledge produce guidance that is plausible in general but inappropriate for the specific organisation — referencing tools it does not use, procedures it does not follow, or configurations it does not have. Retrieval grounding is the established mitigation [6], [7], [10], [11]. However, the literature predominantly evaluates *retrieval relevance*; the contribution of grounding to *end-to-end resolution outcomes* within a complete support pipeline is rarely isolated and measured.

**P3 — Static ticket lifecycle management.** Ticket creation, prioritisation, categorisation and status transition remain largely manual or governed by static rules. Supervised approaches to ticket classification [3] and resolution-time prediction [4] have been studied, but as standalone models detached from the conversational process that generates the ticket. In the resolution-time case the detachment carries a measurable cost: features available at ticket-open time are demonstrably the weakest configuration, achieving R² = 0.5412 against 0.8318 for lifecycle-aggregated features [4], and a model detached from the conversation has no access to the lifecycle signal that would close that gap.

**P4 — The action gap.** Support systems predominantly *advise* rather than *act*. Even well-defined, low-risk operations — clearing temporary files, flushing a DNS cache, restarting a service — are left to the user to perform manually, with the attendant risk of transcription error and the certainty of consumed user time. Closing this gap requires executing commands on user systems, which introduces genuine security exposure through direct and indirect prompt injection [20]–[22]. Where the gap has been closed in practice, it has been closed under policy governance and explicit consent [18], which confirms both the viability of the approach and the necessity of the governance.

**P5 — Absence of architectural evidence.** Where integrated systems exist — commercially, or as industrial pilots [18] — their internal architecture, per-component contribution and failure characteristics are not publicly decomposed or independently evaluated. Researchers and practitioners consequently have no evidence base on which to decide which architectural decisions actually matter. This fragmentation is identified explicitly at field level [19] but is not resolved there, because a survey can document inconsistency without generating the missing measurements.

### 1.3.3 Statement of the Research Gap

> **The gap addressed by this research is not the absence of an integrated IT support system, but the absence of an openly specified, architecturally transparent and component-wise evaluated reference design for agent-decomposed IT support with model-independent, human-gated remediation.**

This formulation is deliberately narrower than a claim of categorical novelty, and the narrowing is a matter of accuracy rather than modesty. Commercial ITSM platforms already combine conversational AI with ticket automation, and a peer-reviewable industrial pilot already demonstrates consent-governed on-device remediation [18]. A thesis that claimed to introduce this category of system would be making a claim the literature refutes. What the literature genuinely lacks is stated concretely in three unanswered questions.

| ID | Unanswered question | Why it is unanswered |
|---|---|---|
| **G1** | What does agent decomposition contribute, *measurably*, over a monolithic LLM performing the same functions in an ITSM setting? | Agent architectures are well theorised [12]–[14] but their benefit is asserted structurally, not isolated by ablation in this domain. The closest integrated system reports aggregate outcomes only [18]. |
| **G2** | What does retrieval grounding contribute to *end-to-end resolution outcomes* in IT support, as distinct from retrieval relevance measured in isolation? | Domain RAG studies evaluate retrieval and answer quality [10], [11]; neither traces the contribution through to whether the incident was resolved. |
| **G3** | How should a risk-tiered, human-gated remediation mechanism be specified so that action-taking remains safe under adversarial input, and what usability cost does that gating impose? | Human-in-the-loop gating is widely prescribed as a principle in the safety literature [20]–[23] but is rarely instantiated as a concrete mechanism within a domain system and then attacked deliberately. |

These questions are answerable with an implementable artefact and a designed experiment. They constitute the intended contribution of this project.

---

## 1.4 Research Questions

**Primary research question**

> *To what extent does decomposing an LLM-based IT support system into specialised, independently governed agents — combined with retrieval-grounded troubleshooting and risk-tiered, human-gated remediation — improve diagnostic accuracy, resolution effectiveness and operational safety relative to monolithic LLM baselines?*

The question is stated in comparative and testable form. A design-descriptive formulation ("how can such a system be designed?") admits no empirical answer, because any implemented system would satisfy it; the comparative form commits the research to producing evidence that could contradict its own design premise.

**Sub-questions**

| ID | Sub-question | Answered by |
|---|---|---|
| **RQ1** | How accurately can an LLM-based classifier distinguish technical from non-technical requests and assign category and urgency, relative to keyword-based and classical supervised baselines [3]? | Ablation condition A1 (§3.12.2) |
| **RQ2** | What measurable effect does retrieval grounding have on the factual correctness and organisational appropriateness of generated troubleshooting guidance, and on end-to-end resolution outcomes [6], [10], [11]? | Ablation condition A2 (§3.12.2) |
| **RQ3** | Does distributing ticket-lifecycle reasoning across dedicated agents improve lifecycle-state correctness relative to a single-model implementation [13], [14]? | Ablation condition A3 (§3.12.2) |
| **RQ4** | Can a whitelist-constrained, risk-tiered, approval-gated execution mechanism prevent unsafe action execution under adversarial input, including direct and indirect prompt injection [20]–[22], and at what usability cost? | Adversarial protocol (§3.12.3) and usability instrument (§3.8) |
| **RQ5** | What is the contribution of each architectural component to overall system performance, established through systematic ablation? | Ablation family A0–A4 (§3.12.2) |

---

## 1.5 Research Motivation

**The problem is demonstrably worth solving.** The 15% productivity effect observed when 5,172 support agents were given a generative assistant, concentrated among less-experienced workers and attributed to the diffusion of tacit knowledge [1], establishes that improving knowledge access in support work has real and quantified value. This research asks what architecture delivers that value most effectively, and how far it can be extended from advice into action.

**The problem is demonstrably not solved.** The 11.4% SRE resolution rate reported by ITBench for agents built on state-of-the-art models [15] and the ceiling of 0.766 root-cause categorisation accuracy reached by a production system on a year of real incidents [17] together show that applying current models to IT operations does not by itself produce competent automation. Architectural research is therefore warranted rather than redundant, and the deficiency it must address is one of composition and governance rather than of model quality.

**The governance question has reach beyond this domain.** Any AI system permitted to execute commands on real infrastructure raises the question of how autonomy should be bounded, and prompt injection against tool-using agents is a demonstrated, practical attack class rather than a theoretical concern [20]–[23]. IT support is an unusually tractable setting in which to study bounded autonomy, because the action space is *enumerable and risk-classifiable*. Unlike open-ended agent domains, where the set of possible actions cannot be listed in advance, the set of useful endpoint remediation operations can be written down, classified by consequence, and constrained in code. A safety argument that can be stated precisely can also be attacked precisely, and therefore evaluated.

**There is a reproducibility deficit.** Commercial ITSM platforms are not inspectable, and industrial pilots report aggregate outcomes rather than component contributions [18]. If the research community is to reason about how these systems should be built, openly documented architectures with published evaluation methodology are a precondition. This project can supply one at a scale appropriate to an undergraduate thesis, which is a modest contribution but a real one.

**There is practitioner relevance.** Organisations without the budget for enterprise ITSM AI platforms currently have no documented reference design to build against. An open architecture with characterised component contributions and an explicit, tested safety argument has direct practical value independent of whether the empirical findings favour the design.

---

## 1.6 Research Aim

> **To design, implement and empirically evaluate an agent-decomposed, retrieval-grounded IT support framework with risk-tiered, human-gated remediation, and to determine — through systematic ablation and adversarial testing — the measurable contribution of each architectural component to diagnostic accuracy, resolution effectiveness and operational safety.**

The aim is expressed in terms of *determining component contributions*, and this phrasing is a substantive methodological commitment rather than a stylistic choice. An aim expressed as demonstrating improvement "compared to conventional IT support" would invite comparison against published industry averages drawn from different populations, different ticket mixes and different measurement definitions — a comparison that cannot support the conclusion it appears to support. The aim adopted here commits the research instead to internal comparisons in which the confounds are controlled by construction: the same scenarios, the same scoring rubric, the same timing protocol, with system configuration as the only manipulated variable (§3.4, §3.12.2).

---

## 1.7 Research Objectives

Objectives are stated in the identify / analyse / design–develop / evaluate progression, each with a criterion by which its completion can be verified rather than asserted.

| # | Objective | Verifiable completion criterion | Addressed in |
|---|---|---|---|
| **O1** | **To identify** the limitations of existing automated IT support approaches, both academic and commercial, through a structured review of the literature | A comparative analysis distinguishing academic from commercial approaches, tabulating strengths, limitations and whether component contributions were isolated | §2.5, §2.9, §2.10 |
| **O2** | **To analyse** the architectural suitability of LLM, RAG and agent-decomposition paradigms for ITSM, including their documented failure modes | A technological analysis at algorithmic, design and workflow levels, each strand terminating in an explicitly justified design decision | §2.6–§2.8 |
| **O3** | **To design and develop** an agent-decomposed IT support framework with retrieval grounding and model-independent remediation governance | An operational system comprising five specialised agents under deterministic orchestration, with seven governance controls verified end-to-end | §3.7; Chapter 4 |
| **O4** | **To design** an evaluation methodology capable of isolating individual component contributions and of testing the safety claim adversarially | An ablation protocol, an adversarial protocol, metric definitions and a statistical analysis plan, specified before any data is collected | §3.12; Chapter 5 |
| **O5** | **To evaluate** the framework empirically and characterise the contribution of each architectural component | Ablation results reported with effect sizes, confidence intervals and significance testing under multiplicity correction | Chapters 6–7 |
| **O6** | **To evaluate** the adversarial robustness of the remediation governance mechanism | Results of the five-class injection and bypass suite, including any successful bypass and its mechanism | Chapters 6–7 |

O5 and O6 are stated separately rather than merged because they are answerable independently and can fail independently. A system may show a clear component-contribution profile while its governance layer is breached, or vice versa; collapsing them into a single evaluation objective would obscure which of the two outcomes occurred.

---

## 1.8 Rich Picture of the Proposed Solution

The proposed system, *Auto-Ops-AI*, routes every user interaction through an orchestration layer that invokes five specialised agents in a fixed, deterministic sequence, grounds generated guidance in an organisational knowledge corpus, and permits remediation only through an enumerated whitelist behind a mandatory human approval gate.

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
        │            │        (similarity threshold, top-k retained)    │
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

**Workflow narrative.** A user reports a problem in natural language, optionally attaching a screenshot. If an image is present it is described first and merged into the textual message, so that image-originated requests rejoin the same downstream path as text and no separate, unvalidated decision route exists. The merged message is classified as technical or non-technical, with a category and an urgency score. Technical messages trigger retrieval over the knowledge corpus; passages above the similarity threshold are supplied to the conversation agent, which conducts a multi-turn diagnostic dialogue conditioned upon them. From the third conversational turn onward, the ticket intelligence agent decides whether a ticket is warranted and generates its metadata; the turn threshold exists to prevent a ticket being raised from an incomplete problem description. If escalation is signalled, the assignment service allocates a human agent by specialisation and current workload. The status agent then reconciles the ticket's lifecycle state against the conversation evidence using deterministic rules. Finally — and only when the user has explicitly enabled Agent Mode — the action executor proposes a *single* next remediation action drawn from the whitelist, together with its risk tier. Nothing executes until the user approves, and approval is checked against the requesting user's ownership of the request.

**The governance boundary is the design's centre of gravity.** Every path that leads to execution passes through the action whitelist, parameter validation and the approval gate, and all three are enforced in application code rather than by prompt instruction. This is what makes the safety claim testable (§3.12.3) rather than merely asserted, and it is the direct design consequence of the axiom stated in §1.2.5.

---

## 1.9 Resource Requirements

### 1.9.1 Hardware

| Resource | Minimum | Recommended | Justification |
|---|---|---|---|
| Processor | Intel Core i5 (8th generation) or equivalent | Intel Core i7 (10th generation) / AMD Ryzen 7 | Model inference is cloud-hosted; local load is API orchestration and the frontend build |
| RAM | 8 GB DDR4 | 16 GB DDR4 | Backend, frontend development server, database and browser run concurrently; the embedding cache is held in process memory |
| Storage | 256 GB SSD (50 GB free) | 512 GB SSD (100 GB free) | Container images, dependencies, knowledge corpus and evaluation trial logs |
| Network | 5 Mbps stable | 25+ Mbps broadband | Every generative and embedding call is a network round trip; end-to-end latency measurements are sensitive to link quality |
| GPU | Not required | Optional | No local model hosting is in scope (§1.10) |
| Evaluation VMs | 1 isolated Windows VM with snapshot capability | 2 VMs | Remediation actions mutate system state; §3.12.1 requires restoration to a uniform baseline between trials, and §3.12.3 requires adversarial testing on isolated, researcher-controlled machines only |

### 1.9.2 Software

| Category | Tool | Purpose |
|---|---|---|
| Language | Python 3.11 | Backend, agents, machine learning |
| Runtime | Node.js 18+ | Frontend tooling |
| Backend framework | FastAPI | REST API and OpenAPI schema |
| Frontend framework | React 19.2 | User interface |
| Build tool | Vite 7.2 | Frontend build and development server |
| LLM provider | Hosted Google Gemini API (version recorded with all results, §3.12.1) | Conversational reasoning, ticket metadata generation, multimodal image analysis |
| Embedding model | Google `text-embedding-004` | Semantic similarity for retrieval |
| Vector store | ChromaDB | Persistent embedding index (see §3.7.4 on the in-memory and persistent retrieval paths) |
| Relational database | SQLite 3.x | Users, tickets, chat history, audit log |
| ORM | SQLAlchemy | Database abstraction and migration path |
| ML libraries | scikit-learn, NumPy, Pandas | Predictive models, similarity computation, data handling |
| Execution | Windows PowerShell via subprocess, without shell interpretation | Remediation action execution |
| Authentication | PyJWT (HS256) with bcrypt | Token issuance and password hashing |
| Containerisation | Docker and Docker Compose | Reproducible development and deployment environments |
| Version control | Git and GitHub | Source management; supports the reproducibility claim in §1.11 |
| Statistical analysis | Python (SciPy, statsmodels) | Analysis plan in §3.12.5 |

---

## 1.10 Project Scope

The scope boundary is drawn to protect the internal validity of the ablation experiment. Several exclusions below remove capability the system could technically support; in each case the justification is that including it would confound a measured comparison or would add engineering surface without addressing any stated gap.

| Aspect | In scope | Out of scope | Justification for the boundary |
|---|---|---|---|
| Conversational AI | Multi-turn, context-retaining dialogue via a hosted LLM; escalation detection; 20-message memory window | Slack / Teams / WhatsApp integration; voice input | Channel integration is engineering surface, not research surface; it would not alter any measured outcome |
| Knowledge retrieval | Embedding-based semantic retrieval over a curated organisational corpus | Web crawling; external internet search | The research claim concerns grounding in *organisational* knowledge; open-web retrieval would confound the retrieval ablation (§3.12.2) by introducing an uncontrolled second knowledge source |
| Input modalities | Text; images (screenshots, device photographs) via a multimodal LLM | Video; live screen sharing | Multimodal fault description is demonstrated in the literature [24] and is inexpensive to support; video adds cost without addressing a stated gap |
| Ticket management | Automated creation, prioritisation, categorisation, assignment and lifecycle transition | ServiceNow / Jira / Zendesk integration | Integration would make lifecycle behaviour depend on an external system's rules, destroying internal validity for RQ3 |
| Remediation | Whitelisted, risk-tiered Windows diagnostic and remediation actions under mandatory human approval | macOS / Linux; destructive operations; remote machine access | Single-platform scope is a stated limitation (§1.12); destructive operations are excluded on ethical grounds (§3.15) |
| Agent architecture | Five specialised agents under centralised deterministic orchestration | Agent-to-agent negotiation; dynamic agent creation; self-modifying agents | Deterministic orchestration is a precondition for reproducible ablation; autonomous negotiation would make trials non-comparable across repetitions |
| Security | RBAC (5 roles, 24 permissions), JWT authentication, audit logging, adversarial input testing | SSO, OAuth2 federation, Active Directory, MFA | Enterprise identity federation is a deployment concern that does not bear on the safety property under test |
| Predictive analytics | Resolution-time estimation and system-health classification, as a secondary objective | Real-time anomaly detection; capacity planning | Retained as a secondary objective only; it does not answer any of RQ1–RQ5 |
| Evaluation | Controlled scenario-based ablation; adversarial safety testing; usability assessment | Longitudinal production study; cross-organisational benchmarking; production A/B testing | Out of reach at undergraduate scale; the resulting external-validity limit is stated in §1.12 rather than concealed |
| Data | Curated synthetic IT support corpus with human-authored ground truth | Real production data from live enterprises | No ethical route exists to production support transcripts at this scale; the consequent limitation is reported in §1.12 |

---

## 1.11 Significance of the Research

**Academic significance.** The study addresses three questions the reviewed literature leaves open (G1–G3, §1.3.3). Its primary academic output is not the system but the *evidence about the system*: a component-wise characterisation of what agent decomposition and retrieval grounding contribute to end-to-end IT support outcomes, and an adversarial characterisation of the conditions under which human-gated remediation holds. Existing work supplies either the components in isolation [3], [4], [6]–[14] or an integrated outcome without decomposition [18], while infrastructure-tier benchmarks [15] do not cover the conversational support tier at which the majority of support interactions occur.

**Methodological significance.** The evaluation protocol — a five-condition ablation with a matched human baseline, human-authored ground truth fixed before any system execution, repeated trials to characterise generative non-determinism, and a five-class adversarial suite — is reusable by other researchers evaluating support automation. Two of its design decisions address validity threats that recur widely in this literature and are therefore worth stating explicitly. Ground truth is authored by humans before execution rather than generated by a model, which avoids the circularity of evaluating a model against labels a model produced — a circularity that reference-free automated RAG evaluation makes convenient without eliminating [25]. And the human comparison uses the *same* scenarios under the same timing protocol rather than an externally published mean, which removes population and measurement-definition differences as confounds.

**Practical significance.** Organisations that cannot procure enterprise ITSM AI platforms gain a documented reference design with an explicit, testable safety argument, together with an account of which components carry their weight and which do not. The set of governance controls specified in §3.7.6 is transferable to any system that permits a language model to act, independently of the IT support domain.

**Significance of negative and partial results.** The project commits in advance to reporting configurations that did not perform as designed, and any successful adversarial bypass, as findings rather than omissions. Given that field-level surveys identify inconsistent and selective evaluation as a systemic problem in this literature [19], transparent reporting of partial failure is itself a contribution, if a modest one.

**Explicit limitation of the contribution.** This work does not claim to introduce a previously non-existent category of system, and does not claim to outperform commercial platforms or the industrial pilot described in [18]. Its claim is narrower and defensible: to make architectural knowledge in this space open, measured and reproducible at a scale that permits independent reimplementation.

---

## 1.12 Delimitations and Limitations

A delimitation is a boundary the researcher chose; a limitation is a constraint the research must accept. Both are stated here so that the claims made in later chapters can be read against them.

**Delimitations (chosen boundaries).** The scope table in §1.10 records the principal choices, of which three carry the greatest consequence for interpretation. First, orchestration is **centralised and deterministic**: agents are invoked in a fixed sequence and do not negotiate or select their successors. This is required for reproducible ablation, but it means the findings apply to orchestrated specialist-agent pipelines and not to the autonomous, negotiating multi-agent systems surveyed in [13]. Second, remediation is confined to **Windows endpoints via PowerShell**, so results do not transfer to macOS or Linux estates without re-evaluation. Third, the evaluation is **controlled and scenario-based** rather than longitudinal and in-production, which trades external validity for the experimental control that component isolation requires.

**Limitations (accepted constraints).**

| # | Limitation | Consequence for the claims |
|---|---|---|
| **L1** | The evaluation corpus is **synthetic and human-authored** rather than drawn from real production support transcripts | Real support conversations differ from authored scenarios in ambiguity, incompleteness and noise; external validity is correspondingly constrained. The trade is accepted because no ethically available route exists to production transcripts at this scale (§3.9) and because synthetic scenarios permit a defined ground truth that real transcripts would not |
| **L2** | The system depends on a **single commercial LLM family** | Findings are conditioned on one provider's models and may not transfer across model families. The model version and generation parameters are recorded with every result so that the dependency is explicit and the study is at least reproducible in principle |
| **L3** | Retrieval operates over **flat text** rather than a structured representation of the corpus | Structured retrieval over ticket corpora is a demonstrated improvement path [11]; not adopting it means the retrieval configuration evaluated here is a reasonable baseline rather than a state-of-the-art retriever, and the measured contribution of grounding should be read as a lower bound |
| **L4** | The predictive subsystem is a **secondary objective** with a small synthetic training set and features drawn from ticket-open time | This is the configuration the literature identifies as weakest [4]. No predictive performance claim is made anywhere in this thesis on the basis of the current specification |
| **L5** | Participant numbers for the usability instrument and the human baseline are **small by design constraint** | The sample is adequate for usability signal but under-powered for small effects in the human comparison; effect sizes with confidence intervals are reported rather than p-values alone, and under-powering is reported rather than concealed (§3.12.5) |
| **L6** | The safety evaluation tests the **implemented control set** against a constructed adversarial suite | A suite that finds no bypass demonstrates that these controls resisted these attacks; it does not prove the absence of a bypass. The claim is bounded accordingly, and the attack classes are specified in §3.12.3 so that the boundary is inspectable |

---

## 1.13 Structure of the Thesis

| Chapter | Content |
|---|---|
| **1. Introduction** | Research context and background, problem statement, research gap, research questions, motivation, aim, objectives, rich picture of the proposed solution, resources, scope, significance, delimitations and limitations |
| **2. Literature Review** | Review method, conceptual map, ITSM domain overview, comparative assessment of existing systems and frameworks, technological analysis at algorithmic, design and workflow levels, critical comparison, confirmation of the research gap |
| **3. Methodology** | Research paradigm, approach and hypotheses, research design and strategy, DSR execution workflow, methodological specification of the proposed system (architecture, agents, RAG pipeline, reasoning workflow, human gating), data collection methods and sources, development methodology, tools and technologies, evaluation methodology and metrics, project management, timeline, ethics, and threats to validity |
| **4. System Design and Implementation** | Detailed architecture, agent specifications, orchestration workflow, retrieval subsystem, remediation governance, predictive subsystem, data layer, and implementation verification |
| **5. Evaluation Design** | Evaluation objectives, experimental setup, corpus construction, ablation design, adversarial protocol, metric definitions, statistical analysis plan |
| **6. Results** | Measured outcomes across classification, retrieval, grounding, resolution, lifecycle, safety, usability and efficiency dimensions, including negative and null results |
| **7. Discussion** | Interpretation of component contributions, interpretation of the safety findings, the usability cost of governance, comparison with existing approaches, answers to RQ1–RQ5, validity threats revisited, and implications |
| **8. Conclusions** | Accomplishment of objectives, problems encountered, self-reflection, real-world applicability, and recommendations for future work |

---

## 1.14 Chapter Summary

This chapter established that IT support automation remains a genuinely unsolved problem despite the maturity of its enabling technologies, and set out the specific form the research response will take.

The background argument proceeded from measured field evidence that knowledge-access assistance raises support productivity by approximately 15% across 5,172 agents, concentrated among the least experienced [1], through the documented difficulty of sustaining resolution knowledge in ITSM practice [2] and the terminal-artefact character of existing academic automation [3], [4], to benchmark and production evidence that composed IT automation resolves only 11.4% of realistic SRE scenarios [15] and reaches at best 0.766 root-cause accuracy in deployment [17]. A recent industrial pilot demonstrates that consent-governed remediation is viable and valuable [18] but reports aggregate outcomes rather than component contributions, within a field that surveys characterise as fragmented and inconsistently evaluated [19]. Adversarial research establishes that any acting system must be governed by model-independent controls, because retrieval-based architectures carry an indirect injection surface by construction [20]–[23].

From this evidence the chapter derived a research gap concerning the absence of open, component-wise evaluated architectural evidence (G1–G3); a comparative and testable primary research question with five sub-questions; an aim expressed as determining component contributions rather than demonstrating superiority over an external population; and six objectives with verifiable completion criteria. The rich picture of *Auto-Ops-AI*, the resource requirements, the scope boundary, the significance of the work, and its delimitations and limitations complete the foundation on which Chapter 2 builds by examining the literature in detail.
