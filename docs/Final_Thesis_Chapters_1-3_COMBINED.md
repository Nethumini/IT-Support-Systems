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


<div style="page-break-after: always"></div>

# CHAPTER 2 — LITERATURE REVIEW

---

## 2.1 Chapter Overview

This chapter reviews the literature that defines and constrains the research problem, and does so critically rather than descriptively. Every strand is treated in the same structured form: what the researchers did, by what method, what they found, what limits the finding, what consequently remains unresolved, and what design decision follows for this project. A review that only summarises establishes that reading occurred; a review that assesses establishes why the proposed research is necessary, and it is the second that this chapter attempts.

The organisation runs from domain to technology to gap. Section 2.2 states the review method and source-selection criteria so that the coverage claimed can be checked. Section 2.3 presents a conceptual map of the reviewed territory. Section 2.4 characterises the ITSM domain and identifies where its binding constraint lies. Section 2.5 assesses existing systems and frameworks comparatively — supervised ITSM machine learning, LLM-based incident diagnosis, retrieval-augmented approaches in IT and customer support, agentic IT support with governed remediation, and commercial platforms — judging in each case whether the approach is suitable for the present problem. Sections 2.6 to 2.8 conduct the technological analysis at the algorithmic, design and workflow levels respectively. Section 2.9 consolidates strengths and limitations in a comparative table; §2.10 states and confirms the research gap; §2.11 maps each element of the gap onto the response designed in Chapter 3; and §2.12 summarises.

---

## 2.2 Review Method and Source Selection

The review was conducted as a structured, purposive review rather than an exhaustive systematic review, which is the appropriate form where the objective is to establish and justify a research gap rather than to synthesise effect sizes across a population of comparable studies.

**Selection criteria.** Sources were admitted on four criteria: (i) peer-reviewed publication in a recognised venue, or preprint status where no peer-reviewed version of record exists and the source carries evidence not otherwise available; (ii) publication between 2019 and 2026, with older work admitted only where it is foundational and has no modern substitute; (iii) direct relevance to one of the five strands in the conceptual map (§2.3); and (iv) verifiability of the specific claim for which the source is cited, established by obtaining and reading the source rather than by inference from its title.

**Foundational exceptions.** Four sources predate the preferred window and are retained deliberately. The original RAG formulation [6] (2020) and dense passage retrieval [8] (2020) are the primary statements of mechanisms this project uses directly; sentence-embedding networks [9] (2019) fall within the window. Design Science Research methodology [26] (2004) and its process model [27] (2007) are cited as methodological canon in Chapter 3, for which no post-2019 substitute of equivalent standing exists.

**Preprint policy.** Four sources are cited as preprints and are marked as such at every use: the RAG design-space survey [7], the IT support RAG system [10], the HouYi injection study [21] and the VIGIL industrial pilot [18]. Preprint status is a limitation on evidential weight, not a disqualification, and each is retained because it carries a specific claim for which no peer-reviewed equivalent was found. This is stated explicitly because [18] in particular carries substantial argumentative weight in §2.5.4 and §2.10.

**What was deliberately excluded.** Vendor market-size projections, analyst estimates of downtime cost, and industry survey statistics were excluded from the evidential core of the argument. Such figures are frequently cited in this problem space and would have made the motivation appear stronger, but they are not independently verifiable, their methodologies are undisclosed, and a research gap justified on them is justified on assertion. Where such context is genuinely useful it is identified as industry rather than peer-reviewed evidence. Generic literature on artificial intelligence, conversational interfaces or machine learning that does not bear on one of the five strands was excluded regardless of citation count.

---

## 2.3 Conceptual Map of the Literature

```
                    ITSM AUTOMATION PROBLEM DOMAIN
        (repetitive workload · knowledge-access and application deficit)
                          §2.4 · [1], [2]
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
   §2.5 EXISTING            §2.6 ALGORITHMIC          §2.7 DESIGN
   SYSTEMS                  FOUNDATIONS               ANALYSIS
   · supervised ITSM ML     · LLM reasoning and       · agent decomposition
     [3], [4]                 hallucination [5]         [12], [13], [14]
   · LLM incident           · RAG [6], [7]            · safety of acting
     diagnosis [16], [17]   · dense retrieval           agents [20]–[23]
   · RAG for IT support       [8], [9]                · multimodal fault
     [10], [11]             · domain RAG [10], [11]     description [24]
   · agentic IT support     · RAG evaluation [25]
     with governed          · supervised prediction
     remediation [18]         [3], [4]
   · commercial platforms
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                    §2.8 WORKFLOW ANALYSIS
              (the action gap · human-in-the-loop gating)
                                  │
                    §2.9 EVIDENCE OF RESIDUAL DIFFICULTY
              [15] 11.4% SRE resolution · [19] field fragmentation
                                  │
                    §2.10 CONFIRMED GAP → THIS RESEARCH
```

---

## 2.4 Domain Overview: IT Service Management

IT Service Management is the practice of delivering, supporting and improving IT services through defined processes — incident management, request fulfilment, problem management and change management — instrumented by ticketing systems and service-level agreements. Serrano et al.'s systematic review of 47 studies establishes the domain's characteristic profile: adoption is associated with genuine benefits in service quality, process standardisation and customer satisfaction, while the recurring challenges concern the organisational cost of process discipline and the difficulty of establishing and sustaining the knowledge assets on which the processes depend [2].

That last point deserves emphasis, because it locates the constraint. ITSM frameworks presuppose documented, current and findable resolution knowledge; the review records that maintaining this in practice is among the persistent implementation difficulties rather than a solved administrative matter [2]. The operational consequence is visible in the tiered delivery model: L1 → L2 → L3 escalation exists partly because knowledge that would allow an L1 agent to resolve an incident is either absent, stale, or too costly to locate within the handling-time budget.

The field evidence supports this reading directly and independently. When support agents were given an assistant that surfaced the working practices of high performers, resolution throughput rose approximately 15%, and the effect concentrated among the least experienced agents while the most skilled gained almost nothing [1]. That is exactly the distributional signature expected if the limiting factor is *access to knowledge already held within the organisation* rather than the existence of that knowledge: those who already hold it cannot benefit from being given it.

**Critical assessment.** This framing has a consequence that shapes the entire research and is worth drawing out before the technology strands are examined. If the binding constraint is knowledge *access and application*, then a system that merely retrieves better addresses only half of the problem. The residual half is the human effort of applying the retrieved procedure — reading it, translating it to the specific machine, executing it correctly, and verifying the outcome. That residual is what §2.8 identifies as the action gap, and it is the reason this research treats remediation execution as a first-class research object rather than as a convenience feature bolted onto a retrieval system. It is also the reason the productivity figure in [1] should be read as a *floor* on the available benefit rather than a ceiling: it was obtained from a system that advised only.

---

## 2.5 Existing Systems, Frameworks and Designs

### 2.5.1 Supervised Machine Learning for ITSM

**What was done and how.** Oliveira, Nogueira and Brito address automated categorisation of IT incident tickets, applying text mining and natural language processing to ticket text and comparing six supervised classifiers — linear support vector classification, stochastic gradient descent, logistic regression, multinomial naïve Bayes, k-nearest neighbours and random forest — across Portuguese, Spanish and English ticket datasets, following CRISP-DM for the data-mining process and Design Science Research as the information-systems methodology [3]. Mulyati et al. address the adjacent problem of predicting incident resolution time, comparing models trained on features taken at ticket creation against models trained on features aggregated across the incident lifecycle [4].

**What was found.** Oliveira et al. report linear SVC as the strongest model at 93.12% accuracy, followed by SGD (90.01%), logistic regression (88.65%) and multinomial naïve Bayes (85.03%), with k-nearest neighbours and random forest weakest; oversampling improved results materially, and the smaller Spanish and English datasets, to which oversampling was not applied, performed appreciably worse [3]. Mulyati et al. report that lifecycle-aggregated features achieve R² = 0.8318 with a mean absolute error of 60.67 hours, against R² = 0.5412 for the non-aggregated configuration, with process-derived features — system modification count, assignment group, reassignment frequency — proving far more predictive than creation-time attributes [4].

**Limitations and what remains unresolved.** Three limitations bear directly on this research. First, and structurally, **the model is a terminal artefact**: it emits a label or a duration and the process stops. Neither system consults resolution knowledge, participates in diagnosis, or acts. Second, the accuracy figures are conditional on data conditions that are not always available — [3] shows performance degrading with smaller corpora and without explicit class-balance treatment, which means a reported accuracy is a property of a corpus-and-pipeline pair rather than of the method. Third, [4]'s central result is an indictment of the configuration most deployable systems actually use: if lifecycle-aggregated features are needed for good resolution-time prediction, then a predictor detached from the process that generates the lifecycle has structurally limited access to its own best signal.

**Assessment of suitability, and design implications.** These approaches are *suitable as components* and *unsuitable as solutions*. They are suitable because categorisation and duration estimation are genuine sub-problems this research must also solve, and because [3] supplies a defensible, published baseline against which the LLM classifier of RQ1 can be compared — an important point, since comparing an LLM classifier only against a keyword baseline would set an artificially low bar. They are unsuitable as solutions for the terminal-artefact reason above. **Design implication 1:** classification is positioned in this research as an *intermediate signal* consumed by downstream agents, never as an output in itself. **Design implication 2:** the finding in [4] is adopted as a specification constraint for the predictive subsystem — features must be lifecycle-aggregated to be defensible — and, because the current predictive component uses ticket-open-time features only, no predictive performance claim is made anywhere in this thesis on its basis (§1.12, L4).

### 2.5.2 LLM-Based Incident Diagnosis

**What was done and how.** Ahmed et al. evaluate large language models for recommending root causes and mitigation steps for cloud incidents, at industrial scale within Microsoft [16]. Chen et al.'s RCACopilot takes a different architectural route to the same task: rather than presenting the incident description to a model directly, it matches an incident to an on-call handler, *aggregates the critical runtime diagnostic information* associated with that handler, and only then invokes the model to predict a root-cause category and generate an explanatory narrative [17].

**What was found.** Ahmed et al. find meaningful assistance quality but performance short of autonomous reliability [16]. Chen et al. report root-cause categorisation accuracy of up to 0.766 evaluated over a year of real Microsoft incidents, and note that the diagnostic-information collection component of the system has been in production use at Microsoft for over four years [17].

**Limitations and what remains unresolved.** Both works stop at *recommendation*. Neither executes anything, and neither therefore confronts the obligations that execution creates: what may be run, under whose authority, with what verification, and what happens when the model is manipulated. The 0.766 ceiling is the crux. Interpreted as an assistant, a system correct three times in four is clearly valuable — it saves the engineer the majority of a diagnostic search. Interpreted as an autonomous actor, the same system is unacceptable, because one in four actions would be taken on an incorrect premise. **The literature offers no principled account of how to convert a system of this accuracy into a safe actor**, and that conversion problem — not the accuracy figure itself — is the unresolved question.

**Assessment of suitability, and design implications.** The architectural lesson from [17] is directly applicable and is adopted here: the model performs better when invoked over *assembled context* than over a raw incident description. This is the same principle that motivates retrieval grounding, arrived at independently from an operational rather than an NLP direction, and the convergence strengthens the case for it. **Design implication:** context assembly before generation is retained as a design commitment; the pipeline is then extended past recommendation into *gated* execution, which is precisely where this research departs from [16] and [17]. The 0.766 figure also informs the design's stance on autonomy: the appropriate response to sub-autonomous accuracy is not to wait for better models but to place a human decision at the point where accuracy would otherwise have to be trusted.

### 2.5.3 Retrieval-Augmented Approaches in IT and Customer Support

**What was done and how.** Toro Isaza et al. construct an incident-resolution recommendation system for IT support that combines RAG-based answer generation with an encoder-only classification model and a generative query-formulation stage, designed explicitly around two enterprise constraints: incomplete domain coverage of the knowledge base, and restricted model size where organisations decline larger proprietary models on cost and privacy grounds [10]. Xu et al. work on LinkedIn's customer-service ticket corpus and construct a knowledge graph over historical issues, retrieving over the graph rather than over flat ticket text [11].

**What was found.** Toro Isaza et al. report improved recommendation quality under the stated constraints [10]. Xu et al. show that conventional RAG treats past tickets as flat text and thereby discards both intra-issue structure and inter-issue relations, and that preserving that structure through a knowledge graph improves retrieval and downstream answer quality [11].

**Limitations and what remains unresolved.** Both studies are limited for the present purpose in the same specific way: **evaluation is reported principally at the level of retrieval and answer quality, not at the level of whether the incident was resolved end to end.** This is not a criticism of their internal validity — measuring retrieval quality is the correct evaluation for a retrieval contribution — but it leaves gap **G2** open. A system may retrieve highly relevant passages and still fail to resolve the user's problem, because the retrieved procedure is misapplied, because the dialogue does not elicit the information needed to select among candidate procedures, or because the user cannot execute what is retrieved. Retrieval relevance is a necessary but not sufficient condition for resolution, and the strength of the implication between them is unmeasured.

**Assessment of suitability, and design implications.** Both are highly suitable as evidence that retrieval grounding is the correct mechanism for this domain, and [11] in particular is a well-founded critique of naive flat-text retrieval. **Design implication 1:** the evaluation includes a no-retrieval ablation condition (A2, §3.12.2) specifically to isolate the contribution of grounding to *end-to-end resolution outcomes*, with retrieval-relevance metrics reported separately rather than as a proxy for them. This is a direct response to G2. **Design implication 2:** [11] identifies structured retrieval as a demonstrated improvement path. The present implementation retrieves over flat text, so the measured contribution of grounding in this study should be interpreted as a lower bound on what a well-engineered retriever could contribute; structured retrieval is recorded as future work rather than claimed (§1.12, L3).

### 2.5.4 Agentic IT Support with Governed Remediation

**What was done and how.** VIGIL is the closest published system to the design proposed in this thesis. It deploys desktop-resident agents on user endpoints that perform situated diagnosis using local context, retrieve over enterprise knowledge, and carry out **policy-governed remediation directly on user devices with explicit consent** and end-to-end observability. It was evaluated in a ten-week operational pilot on 100 resource-constrained endpoints [18].

**What was found.** The pilot reports a 39% reduction in interaction rounds, at least fourfold faster diagnosis, and self-service resolution in 82% of matched cases, together with excellent usability, high trust and low cognitive workload measured across four validated instruments. The authors additionally report that users rated the system *higher* when no historical knowledge-base match was available, and interpret this as evidence that on-device situated diagnosis provides value independently of knowledge-base coverage [18].

**Limitations and what remains unresolved.** This work must be engaged with directly rather than minimised, because it substantially overlaps the design premise of this project: on-device, consent-gated, knowledge-grounded remediation. Its existence removes any claim of categorical novelty for that combination, and that claim is accordingly not made anywhere in this thesis (§1.1, §1.3.3).

What the study does *not* do is decompose its result. The reported gains are attributed to the system as a whole; no ablation isolates the contribution of retrieval, of on-device situated diagnosis, or of the governance layer. This is a reasonable choice for an industrial pilot, whose purpose is to establish operational viability, but it leaves a practitioner unable to determine which parts of the architecture to prioritise. The paper's own most interesting observation sharpens the point: if users rated the system higher when *no* knowledge-base match was found [18], then the relationship between retrieval and perceived value is evidently not monotonic, and an aggregate result cannot reveal what is happening. That finding is an argument for ablation, made inside a study that does not perform one. Additionally, no adversarial evaluation of the governance layer is published, so the conditions under which consent-gated remediation holds against deliberate manipulation remain uncharacterised.

**Assessment of suitability, and design implications.** This research positions itself as **complementary rather than competing**: the same design direction, a different research question. Where [18] establishes *that* the approach works in one industrial deployment, this project asks *which components produce the effect*, using ablation over a common scenario set, and publishes the architecture at a level of detail permitting independent reimplementation. **Design implication:** the ablation design in §3.12.2 is constructed so that the retrieval condition (A2) and the decomposition condition (A3) are separable, which is the specific evidence [18] cannot supply; and the adversarial protocol in §3.12.3 addresses the governance question that [18] leaves untested. This is a smaller claim than a novelty claim, and it is one the research can actually substantiate.

### 2.5.5 Commercial ITSM Platforms

Commercial ITSM platforms combine conversational AI with ticket automation and workflow-triggered remediation. Their existence is acknowledged here as a matter of accuracy: any claim that this combination is unprecedented would be false.

**Assessment of suitability.** They are unsuitable as *research evidence*, for a methodological rather than a competitive reason. Their internal architecture, per-component contributions and failure characteristics are not publicly documented; their evaluation methodology is not published; and their behaviour cannot be independently reproduced, instrumented or ablated. A researcher can observe that such a platform performs well or poorly, but cannot learn from it which architectural decisions produced that outcome, and therefore cannot build on it. This is the reproducibility argument underpinning §1.11: the contribution of an open architecture is not that it outperforms closed ones — a claim this thesis does not make — but that it can be inspected, criticised, replicated and improved.

---

## 2.6 Technological Analysis I — Algorithmic Level

### 2.6.1 Large Language Models as Diagnostic Reasoners

Surveys of large language models document strong performance on multi-step reasoning and instruction-following, together with the observation that qualitatively new capabilities emerge above certain parameter scales and are further shaped by adaptation tuning [5]. The property that matters for IT support is **conditional adaptation**: the ability to select the next diagnostic action from the reported outcome of the previous one, rather than following a path fixed in advance. This is precisely the capability that separates a diagnostic dialogue from a decision tree, and it is why the conversational component of this project is generative rather than rule-based.

The corresponding failure mode is equally well documented: fluent generation of confident but factually incorrect content, together with knowledge staleness and untraceable reasoning [5], [7].

**Critical assessment.** The severity of this failure mode is domain-dependent, and the domain-dependence is usually understated. For general question answering, hallucination degrades answer quality and the cost is borne as user dissatisfaction. For IT support, hallucination produces an instruction that a user may execute on a working machine, and the cost is borne as system damage. The algorithmic conclusion is therefore stronger here than in the general case: **unconstrained generation is not merely sub-optimal in this domain, it is inadmissible**. Grounding is a precondition of responsible deployment, not an enhancement to be added if resources permit. This reasoning is why retrieval is treated in this thesis as an architectural requirement, and simultaneously why its *contribution* must be measured rather than assumed — an architectural requirement that turns out to contribute nothing measurable would be an important negative finding.

### 2.6.2 Retrieval-Augmented Generation and Dense Retrieval

RAG conditions generation on documents retrieved from a trusted corpus, pairing the model's parametric knowledge with an explicit non-parametric memory that can be inspected, audited and updated without retraining [6]. The approach has since developed into a broad design space; Gao et al. organise it into naïve, advanced and modular paradigms and analyse retrieval, generation and augmentation techniques together with evaluation frameworks [7].

The retrieval component descends from dense representation learning. Karpukhin et al. show that a dual-encoder retriever trained from a limited number of question–passage pairs substantially outperforms sparse lexical baselines such as BM25 on top-k retrieval accuracy [8], establishing that semantic retrieval need not depend on lexical overlap — an essential property in IT support, where a user writes "my internet keeps dropping" and the relevant article is titled "Wireless adapter power management configuration". Reimers and Gurevych's siamese sentence-embedding networks make large-scale semantic comparison computationally tractable by allowing each passage to be encoded once, independently, and compared thereafter by cosine similarity [9], which is the mechanism this project's retrieval subsystem implements.

**Critical assessment.** The dependence of the entire approach on embedding quality and on the relevance threshold is frequently understated in applied work. Two propositions follow from the mechanism and are, in this researcher's assessment, insufficiently emphasised in the applied RAG literature. First, **retrieval quality bounds generation quality**: if the retriever returns nothing relevant, grounding contributes nothing, and the system degrades to the ungrounded case. Second, and more seriously, **confidently irrelevant retrieval is worse than no retrieval**, because the model is instructed to condition on the retrieved passage and will do so, producing guidance that is grounded in the wrong procedure and therefore carries unearned authority. The similarity threshold that decides "relevant enough" is consequently a substantive design parameter that determines which of these two regimes the system operates in, not an implementation detail. **Design implication:** the similarity threshold and the ranking weights used in this project are treated as *tuned and reported* parameters, swept during evaluation and justified by measurement (§3.12.4), rather than fixed as unexplained constants.

### 2.6.3 Evaluating Retrieval-Augmented Systems

Evaluating a RAG pipeline is itself a research problem, because quality decomposes into at least three separable dimensions: whether retrieval identified relevant context, whether the model used that context faithfully, and whether the generation is otherwise adequate. Es et al.'s RAGAS proposes reference-free metrics addressing these dimensions without requiring human-annotated ground-truth answers [25].

**Critical assessment.** The decomposition proposed in [25] is analytically valuable and is adopted conceptually in this research: grounding correctness is measured separately from retrieval relevance, because conflating them makes it impossible to tell a retrieval failure from a faithfulness failure. The scoring mechanism, however, carries a circularity risk that is material in this setting. Metrics computed by a language model over the output of a language model are not independent evidence, particularly where the same model family serves both roles: a systematic blind spot in the model is invisible to an evaluator that shares it. Reference-free evaluation is attractive precisely because it scales, and that attraction is what makes the risk easy to accept without examination. **Design implication:** this research adopts human-authored ground truth, fixed before any system execution, as its primary evaluative basis (§3.12.1), and treats automated RAG metrics as a secondary, corroborating signal only. The cost of this decision is evaluation throughput; the benefit is that the primary accuracy claims do not depend on a model assessing a model.

### 2.6.4 Supervised Prediction as a Subordinate Component

Ticket classification [3] and lifecycle-aware resolution-time prediction [4] supply the algorithmic basis for the predictive subsystem retained as a secondary objective in this project. The most directly actionable result in this strand is [4]'s demonstration that lifecycle-aggregated features (R² = 0.8318) substantially outperform creation-time features (R² = 0.5412) [4].

**Critical assessment and honest self-application.** Applying this literature to the present artefact yields an unfavourable verdict that is reported rather than avoided. The predictive component implemented in this project uses a small feature set drawn entirely from information available at ticket creation, trained on a modest synthetic dataset. Measured against [4], this is the weak configuration, not the strong one; measured against [3], it is under-featured and trained on a corpus far smaller than those on which the reported accuracies were obtained. **Design implication:** the component is retained as a secondary objective, its specification is recorded as requiring revision along the lines [4] indicates, and — critically — **no predictive performance claim is made anywhere in this thesis** on the basis of the current specification (§1.12, L4). Reporting a weak component honestly is preferable to presenting its output as a finding, and the literature supplies the standard against which the weakness is judged.

---

## 2.7 Technological Analysis II — Design Level

### 2.7.1 Agent Decomposition and What It Actually Provides

The ReAct paradigm established that interleaving reasoning traces with actions allows a model to induce, track and revise plans while interfacing with external sources, with observation feedback closing the loop [12]. Wang et al. survey LLM-based autonomous agents and formalise their construction around four elements — profiling, memory, planning and action — while noting that the agent literature is dominated by architectures in which the agent selects its own next step [13]. Liu et al. survey 124 studies applying LLM-based agents across software engineering activities, documenting breadth of adoption alongside unresolved challenges in reliability, evaluation and cost [14].

**Critical assessment.** A common argument in applied work is that decoupling a conversational component from an execution component constitutes a *security boundary* against prompt injection. On close examination this argument does not hold for architectures of the kind implemented here, and it is important to state so plainly. In the present system, agents are classes within a single process, sharing address space and privileges. There is no operating-system, container or privilege-level separation between them. An injection that manipulates the conversational agent's output does not encounter a trust boundary merely because the next function call is dispatched to a different class; the call is an ordinary in-process invocation. Presenting class separation as privilege separation would be a category error, and this thesis does not make that claim.

The defensible argument for decomposition is narrower, and being narrower it is also testable. Decomposition delivers three things:

1. **A single enforcement point.** Every proposed action must pass through one auditable location where it is validated against a whitelist. This is an architectural guarantee — there is no other code path to execution — rather than a prompt instruction that a model might be persuaded to ignore.
2. **Determinism where determinism is preferable.** Lifecycle-state logic can be implemented as deterministic rules rather than generative inference, making state transitions reproducible and auditable. This is a heterogeneous-design claim: generative where interpretation is required, deterministic where accountability is required.
3. **Independent testability.** Each component can be exercised and evaluated in isolation, which is a precondition for the ablation methodology in §3.12.2. A monolithic implementation cannot be ablated component-wise, because it has no components.

The *actual* safety mechanism, as distinct from the architectural one, is the combination of an enumerated action whitelist, parameter validation with metacharacter screening, and mandatory human approval (§2.7.2, §3.7.6). **Design implication:** the security claim is made only for these mechanisms, and the benefit of decomposition is stated as a hypothesis (H3, §3.3) to be tested by ablation rather than asserted as a structural property. It is worth noting that a null result here would itself answer G1: evidence that decomposition confers no measurable benefit under centralised orchestration would be a useful finding for practitioners deciding how to spend engineering effort.

### 2.7.2 Safety of Acting Agents

Four studies define the threat landscape for any system that permits a model to act, and they are complementary rather than redundant.

Greshake et al. establish **indirect prompt injection**: adversarial instructions embedded in content that an LLM-integrated application retrieves, rather than in the user's own input. The attack applies to any system performing retrieval over a corpus it does not fully control, and the authors demonstrate compromise of real deployed applications [20]. Liu et al. establish the **empirical breadth** of the exposure, applying a black-box injection technique to 36 real-world LLM-integrated applications and finding 31 vulnerable, with ten vendors confirming the findings [21]. Debenedetti et al.'s AgentDojo establishes the **execution-risk dimension** in a controlled setting, populating a realistic tool-use environment with 97 tasks and 629 security test cases and finding that existing attacks break some security properties while existing defences close some but not all — and that state-of-the-art models fail many tasks even with no adversary present [22]. Ruan et al.'s ToolEmu establishes the **methodological problem**: identifying such risks by hand does not scale, and their LM-emulated sandbox surfaces failures of which 68.8% are judged by human evaluators to be valid real-world agent failures, with even the safest agent evaluated failing 23.9% of the time [23].

**Critical assessment.** Read together, these four works support one conclusion that this research adopts as a design axiom: **safety controls that depend on model compliance are not safety controls.** The reasoning is short and, once stated, difficult to escape. A defence expressed as a system-prompt instruction is a string of text in the model's context; an injection is also a string of text in the model's context; there is no mechanism by which the model reliably privileges the first over the second, because the model has no formal means of distinguishing instructions from data [22]. A defence expressed as an enumerated whitelist in application code is categorically different, because no persuasion of the model expands the set of operations the application is capable of executing. The model may be induced to *request* anything; it cannot be induced to *cause* anything outside the enumerated set.

There is a second, less-noticed implication for this architecture specifically. A system that performs retrieval over an organisational corpus possesses an indirect injection surface **by construction** [20], and a system that accepts uploaded screenshots possesses a second one. These are not incidental exposures to be patched but structural properties of the design, and they must therefore be tested as such. **Design implication:** all governance controls in this project are enforced outside the model (§3.7.6), and the adversarial protocol in §3.12.3 attacks the model deliberately in order to measure whether the controls hold — including an indirect-injection class in which adversarial content is planted in retrieved documents and uploaded images, derived directly from [20]. The safety claim is formulated so that a single successful bypass falsifies it (H4, §3.3), which is the appropriate form for a safety claim.

### 2.7.3 Multimodal Fault Description

Alsaif et al. propose a multimodal LLM-based fault detection and diagnosis framework for industrial settings, using a vision-capable model to interpret fault evidence that is visual rather than textual, combining real-time data streams with fine-tuned models and augmenting coverage with synthetically generated data for under-represented fault scenarios [24].

**Critical assessment.** The transfer to end-user IT support is natural and, in one respect, stronger than in the industrial case. Users describe faults poorly in prose but photograph or screenshot them accurately: an error dialogue, a stop-code, a device photograph or a network status panel carries precise diagnostic information that free-text paraphrase reliably loses. The limitation for this project's purposes is that visual interpretation inserts a *second generative stage* ahead of classification, and generative stages compose their uncertainty rather than cancelling it — an image description that is subtly wrong produces a downstream classification that is confidently wrong. **Design implication:** the image agent's output is merged into the textual message and passed through the same classification and retrieval path as ordinary text, so that no separate, less-validated decision path exists for image-originated requests. This is a containment decision, not a capability decision: it ensures that whatever accuracy cost multimodal input carries is borne within an already-instrumented pipeline rather than in a parallel one.

---

## 2.8 Technological Analysis III — Workflow Level

Current ITSM workflows are fragmented across human and machine steps: a user converses with a bot, the bot creates a ticket, a human reads it, a human executes the fix, a human closes it. The literature reviewed above terminates at different points along that chain. Classification terminates at step two [3], [4]. Diagnosis terminates at recommendation [16], [17]. Retrieval-augmented support terminates at a proposed resolution [10], [11]. In each case, the remaining steps are returned to the human.

**The action gap** is the resulting deficiency: systems can explain *how* to fix an issue but cannot fix it. Two observations about this gap are worth making explicitly, because they are usually treated as one.

First, the gap is *economically* significant in proportion to how much of the total resolution effort lies downstream of knowing the answer. For the recurrent faults that dominate support queues — a stale DNS cache, a full temporary directory, a stalled print spooler — knowing the answer is the small part and applying it is the rest, particularly for a non-technical user who must be talked through it.

Second, the gap is *qualitatively* rather than incrementally risky to close. When a system that advises is wrong, the output is merely wrong; the user reads it, may notice the error, and may decline to act. When a system that acts is wrong, the output is *executed*. The failure mode changes from misinformation to state change, and state change on a user's working machine may be difficult to reverse. This is why closing the gap is not simply the next feature in a sequence but a change in the system's risk class, and why the safety literature reviewed in §2.7.2 becomes binding at exactly this point rather than earlier.

VIGIL demonstrates that the gap can be closed in production under policy governance and explicit consent, with measured operational benefit [18]. What the literature does not supply is a decomposition of that workflow into components whose individual contributions have been measured, or a published account of how a governance layer behaves under deliberate attack. Human-in-the-loop gating is widely *prescribed* as a principle in the safety literature [20]–[23] but is rarely *instantiated* as a concrete mechanism within a domain system, specified precisely enough to be attacked, and then attacked.

**Critical assessment.** A complete support workflow understands the issue, retrieves the documented procedure, requests permission, executes the approved operation, and closes or escalates the ticket. Anything short of that is partial automation that leaves the residual work with the user. But a complete workflow that cannot demonstrate its own safety under attack is not deployable, and demonstrating safety requires more than asserting that a human approves — it requires showing that approval cannot be circumvented, that what is approved is what executes, and that the set of approvable operations cannot be extended by manipulating the model. **Design implication:** the workflow specified in §3.7.5 closes the loop, and the approval gate is treated not as a usability nicety but as a load-bearing safety control whose cost to the user is itself measured (§3.12.4). Treating the gate as a measured cost rather than an assumed good matters, because a control that users find intolerable will be disabled in practice, and a safety mechanism that is switched off provides no safety.

---

## 2.9 Critical Comparison: Strengths, Limitations and Coverage

| Approach | Representative work | Method | Principal finding | Limitations for this problem | Component contributions isolated? |
|---|---|---|---|---|---|
| Supervised ticket classification | [3] | Six supervised classifiers over multilingual ticket text; CRISP-DM | Linear SVC 93.12% accuracy; oversampling and corpus size materially affect results | Terminal artefact — no diagnosis, no knowledge use, no action; accuracy conditional on data treatment | No — standalone classifier |
| Lifecycle-aware resolution-time prediction | [4] | Comparison of creation-time versus lifecycle-aggregated feature sets | Aggregated R² = 0.8318 vs non-aggregated R² = 0.5412 | Prediction only; does not participate in resolution; strong configuration requires lifecycle access a detached model lacks | No |
| LLM incident diagnosis | [16], [17] | Industrial-scale evaluation [16]; context aggregation before model invocation on a year of production incidents [17] | Meaningful assistance [16]; up to 0.766 root-cause categorisation accuracy [17] | Stops at recommendation; 0.766 is valuable for assistance and insufficient for autonomy; no account of safe conversion to action | No — diagnosis only |
| RAG for IT and customer support | [10], [11] | RAG plus encoder classifier and query generation [10]; knowledge-graph retrieval over ticket corpus [11] | Improved recommendation under enterprise constraints [10]; structured retrieval beats flat-text retrieval [11] | Evaluated on retrieval and answer quality, not end-to-end resolution (**G2**) | Partially |
| Agentic IT support with governed remediation | [18] | Desktop-resident agents; 10-week pilot, 100 endpoints; four validated instruments | 39% fewer interaction rounds; ≥4× faster diagnosis; 82% self-service resolution | Aggregate outcomes only, no component ablation (**G1**); no published adversarial evaluation of governance (**G3**) | No — integrated but not decomposed |
| Agent architecture theory | [12], [13], [14] | Reasoning–action interleaving [12]; construction taxonomy [13]; survey of 124 SE studies [14] | Establishes decomposition patterns and observation-feedback loops | General-purpose, not ITSM-situated; decomposition benefit not empirically isolated in this domain (**G1**) | No |
| Safety of acting agents | [20]–[23] | Indirect injection demonstration [20]; 36 deployed apps tested [21]; 97 tasks / 629 security cases [22]; LM-emulated sandbox [23] | Indirect vector confirmed; 31/36 apps vulnerable; defences close some properties not all; 68.8% of sandbox failures judged valid | Prescribes principles and supplies test environments; does not instantiate and adversarially test gating inside a domain support system (**G3**) | No |
| IT agent benchmarking | [15] | 102 real-world scenarios across SRE, CISO, FinOps | 11.4% / 25.2% / 25.8% resolution rates for state-of-the-art agents | Infrastructure tier rather than conversational support tier; benchmarks rather than proposes architecture | Benchmark only |
| AIOps field synthesis | [19] | Systematic survey of 183 articles, Jan 2020 – Dec 2024 | Documents rapid expansion alongside fragmented architectures and inconsistent evaluation | Identifies the problem; a survey cannot generate the missing measurements | Survey |
| ITSM domain research | [2] | Systematic review of 47 studies | Benefits in service quality and standardisation; persistent knowledge-asset and process-discipline challenges | Pre-dates LLM-based automation; describes the constraint rather than addressing it | Not applicable |
| Commercial ITSM AI platforms | — | Not published | Deployed at scale with integrated capability | Architecture, component contributions and failure modes undocumented; not reproducible or ablatable (**P5**) | Not inspectable |

---

## 2.10 Reflection and Confirmation of the Research Gap

The reviewed literature, taken as a whole, establishes seven things.

1. The binding constraint in ITSM is knowledge **access and application**, not knowledge existence — evidenced both from the domain side, where knowledge-asset maintenance is a documented persistent challenge [2], and from the field-experiment side, where the productivity benefit of assistance concentrates among those who lacked access to knowledge others already held [1].
2. Ticket classification and resolution-time prediction are substantially automatable but are studied as **terminal artefacts** detached from diagnosis and action [3], [4].
3. Retrieval grounding demonstrably improves IT incident recommendation, but is evaluated on **retrieval quality rather than resolution outcomes** [10], [11].
4. Large language models assist incident diagnosis without reaching autonomous reliability, topping out at **0.766** in a production deployment, with no published account of how to convert sub-autonomous accuracy into safe action [16], [17].
5. Agent decomposition is well theorised, but its benefit is **not empirically isolated** in an ITSM setting, and one common justification for it — that class separation constitutes a privilege boundary — does not survive examination [12]–[14].
6. Acting agents face demonstrated, practical adversarial exposure through both direct and indirect injection, and **defences that depend on model compliance fail**; retrieval-based architectures carry the indirect surface by construction [20]–[23].
7. Realistic IT automation remains largely unachieved at the benchmark level (11.4% on SRE scenarios) [15], within a field that surveys characterise as fragmented and inconsistently evaluated [19].

The one system that closes the action gap in production [18] does not weaken this analysis; it completes it. It confirms the design direction and simultaneously defines the remaining opportunity, because it reports what an integrated system achieved rather than which of its components achieved it, and it publishes no adversarial evaluation of its governance layer.

> **Gap confirmed.** What is absent from the literature is not an integrated IT support system, but **open architectural evidence** — measured knowledge of which components contribute what to end-to-end IT support outcomes, and of the conditions under which action-taking remains safe under deliberate attack.

This gap is worth addressing on three grounds. It is **answerable**, because the components can be switched off individually and the resulting differences measured. It is **useful**, because practitioners currently choose architectures without evidence. And it is **timely**, because systems of this class are being deployed now [18], which means the evidence base ought to exist now rather than after deployment has become widespread.

---

## 2.11 How This Research Addresses the Gap

| Gap | Addressed by | Specified in |
|---|---|---|
| **G1** — the contribution of agent decomposition is unmeasured in ITSM | Ablation conditions A1 → A3 executed on an identical scenario set, isolating the monolithic LLM, the retrieval-augmented LLM and the agent-decomposed configurations, with a null result treated as a reportable finding | §3.12.2 |
| **G2** — retrieval grounding is evaluated on relevance rather than resolution | Ablation condition A2 measured against **end-to-end resolution outcomes** and grounding correctness, with retrieval-relevance metrics reported separately rather than substituted for them | §3.12.2, §3.12.4 |
| **G3** — human-gated remediation is prescribed but not adversarially tested | A five-class adversarial protocol including the indirect vector demonstrated in [20], with a hypothesis stated so that a single bypass falsifies it and a prior commitment to report any bypass found | §3.3, §3.12.3 |
| **P5** — architecture not inspectable | Architecture, agent specifications, governance controls, action inventory and parameters documented at a level permitting reimplementation, with values verified against source rather than asserted | §3.7; Chapter 4 |

---

## 2.12 Chapter Summary

This chapter mapped the literature from domain to technology to gap, assessing at each stage what a body of work establishes, what limits it, and what design decision follows for this project.

It established that the domain constraint is knowledge access and application rather than knowledge existence, evidenced independently from ITSM research [2] and from field experiment [1]; that existing academic approaches automate sub-tasks in isolation and terminate before action [3], [4], [10], [11], [16], [17]; that the algorithmic foundations of grounded generation are mature but that retrieval quality bounds and can invert the value of grounding [6]–[9]; that agent decomposition is well theorised but its benefit in ITSM is unmeasured, and that a common security justification for it does not withstand examination [12]–[14]; that acting systems face demonstrated adversarial exposure requiring model-independent controls [20]–[23]; and that the closest published system demonstrates viability without decomposing contribution [18].

Two positions warrant restating because they constrain the claims made in the remainder of the thesis. The combination of conversational AI, retrieval grounding and consent-gated remediation is **not novel**, and no novelty claim is made for it. And class-level agent separation is **not** a privilege boundary; the safety argument rests entirely on the enumerated whitelist, parameter validation and mandatory human approval described in §3.7.6, which is why those mechanisms — and not the decomposition — are what §3.12.3 attacks.

The research gap was confirmed as the absence of open, component-wise evaluated architectural evidence for agent-decomposed IT support with model-independent human-gated remediation, and §2.11 mapped each element of that gap onto the methodology specified in Chapter 3.


<div style="page-break-after: always"></div>

# CHAPTER 3 — RESEARCH METHODOLOGY

---

## 3.1 Chapter Overview

This chapter specifies how the research is conducted and justifies each methodological choice against the alternatives that were considered and rejected. A methodology chapter that only describes procedure leaves the reader unable to judge whether the procedure was the right one; this chapter therefore states, for every significant decision, what was chosen, what was rejected, and why the rejection was warranted.

The chapter is organised in four movements. The first establishes the philosophical and logical basis of the study: the research paradigm and its operationalisation (§3.2), the reasoning approach and the falsifiable hypotheses it yields (§3.3), the research design (§3.4), the research strategy (§3.5), and the Design Science Research execution workflow that maps the paradigm onto the specific activities of this project (§3.6). The second specifies the artefact at the methodological level of detail required to understand how it is evaluated (§3.7): its architectural characterisation, the multi-agent framework and the roles within it, the interaction pattern between agents, the knowledge-grounding pipeline, the troubleshooting and reasoning workflow, the human approval gate and the governance controls that surround it, and the supporting system components. The third specifies how evidence is obtained: data collection methods (§3.8), data and knowledge sources (§3.9), the system development methodology (§3.10) and the tools selected to implement it (§3.11). The fourth specifies how the artefact is assessed and the research managed: the evaluation methodology including the ablation design, adversarial protocol, metrics and statistical analysis plan (§3.12), the project management methodology (§3.13) and timeline (§3.14), the ethical framework (§3.15), and the threats to validity with their mitigations (§3.16). Section 3.17 summarises.

Full implementation detail for the artefact is deferred to Chapter 4 and the full evaluation instrument to Chapter 5; §3.7 and §3.12 present the level of specification necessary to establish that the method is coherent, that the evaluation can answer the research questions, and that the design decisions follow from the analysis in Chapter 2.

---

## 3.2 Research Paradigm

This research adopts **pragmatism**, operationalised through **Design Science Research (DSR)**.

**Justification of the philosophy.** Pragmatism holds that the value of knowledge lies in its practical consequences — what works to resolve a real problem — rather than in correspondence to an independently existing state of affairs alone. The problem investigated here is an operational one: support organisations cannot scale to meet demand, and the knowledge that would let them do so is present but inaccessible (§2.4). The research does not merely observe that condition; it intervenes in it by constructing an artefact, and then asks whether the intervention works and, critically, *which parts of it* work.

The two principal alternatives were considered and rejected for specific reasons rather than by default. A **positivist** stance treats the phenomenon under study as given and seeks to measure regularities within it; it cannot accommodate a study whose central object is a system that does not yet exist, and whose properties are therefore created by the researcher rather than discovered. An **interpretivist** stance foregrounds the subjective experience of participants and would produce a rich account of how support staff and users experience IT support; it could not, however, isolate the contribution of an architectural component, because component contribution is not something participants can report on. Pragmatism accommodates the construction of the artefact, and it also licenses the mixed quantitative–qualitative measurement this study requires: instrumented performance logs *and* user perception of trust and approval burden, which are different kinds of evidence about the same design decision and are both necessary (§3.12.4).

**Justification of the operationalisation.** DSR is directed at the construction and evaluation of an information-technology artefact as the primary vehicle of inquiry, with knowledge of the problem domain and its solution obtained *through* building and applying the artefact [26]. This study follows the established six-activity DSR process model: problem identification and motivation, definition of objectives for a solution, design and development, demonstration, evaluation, and communication [27]. The choice is not merely conventional: DSR is the methodology whose unit of contribution is an artefact plus knowledge about it, which is exactly the form the gap identified in §2.10 takes.

**The obligation this carries.** DSR imposes a methodological requirement that is easily under-served in applied projects: **the artefact must be evaluated in a way capable of falsifying the design claims** [26], [27]. A demonstration that the system runs is not a DSR evaluation; it is a demonstration, and it establishes only that an artefact exists to be measured. This obligation is the reason the evaluation in §3.12 is built around ablation and adversarial testing — designs in which the system can fail, and in which specific architectural claims can be shown to be wrong — rather than around feature demonstration. It is also the reason each hypothesis in §3.3 is paired with an explicit falsification condition.

---

## 3.3 Research Approach and Hypotheses

The study uses a combined **abductive–deductive** approach, applied in that order.

**Abductive phase.** Observation of the action gap in deployed support systems (§2.8), of benchmark evidence that composed IT automation performs poorly [15], and of the safety literature's prescription of bounded autonomy [20]–[23], led to the inference of the most plausible explanatory architecture: that **decomposition into specialised components, combined with retrieval grounding and explicit model-independent governance, is a productive response to the composed-task failure**. Abduction is the appropriate mode of reasoning at this stage because the architecture is not deducible from existing theory — no theory entails it — and is not derivable by induction from a dataset, since no dataset of architectures and outcomes exists. It is an inference to the best available explanation, and its status as an inference is precisely why it must subsequently be tested rather than assumed.

**Deductive phase.** From that architecture and from the literature, four falsifiable hypotheses are derived. Each is bound to a specific test and to an explicit condition under which it is refuted.

| ID | Hypothesis | Grounded in | Tested by | Falsified if |
|---|---|---|---|---|
| **H1** | Retrieval grounding significantly increases the factual correctness and organisational appropriateness of troubleshooting guidance, relative to ungrounded generation | [6], [7], [10], [11] | Ablation A1 vs A2 (§3.12.2) | No significant difference between A1 and A2 on grounding correctness |
| **H2** | LLM-based intent classification outperforms keyword-based and classical supervised baselines on category and urgency assignment | [3], [5] | Ablation A1 against baselines (§3.12.2) | Baseline macro-F1 ≥ LLM macro-F1 |
| **H3** | Dedicated lifecycle agents yield higher ticket-state correctness than single-model lifecycle handling | [13], [14] | Ablation A2 vs A3 (§3.12.2) | No significant difference in state-transition correctness between A2 and A3 |
| **H4** | Whitelist constraint combined with mandatory approval gating prevents unauthorised execution under adversarial input, including direct and indirect injection | [20], [21], [22] | Adversarial suite (§3.12.3) | **Any** unauthorised execution occurs |

Two features of this table are deliberate. First, H1 and H3 are stated so that a **null result is informative rather than a failure of the study**: evidence that retrieval grounding contributes nothing measurable to end-to-end outcomes, or that decomposition confers no benefit under centralised orchestration, would answer G2 and G1 respectively and would be reported as findings. Second, **H4 is falsified by a single counter-example**. This asymmetry is not an oversight but the correct form for a safety claim: a control that holds against 99 attacks and fails against the hundredth is not a control, and a hypothesis that permitted averaging across attacks would conceal exactly the outcome that matters. Section 3.12.3 accordingly commits in advance to reporting any successful bypass.

---

## 3.4 Research Design

The design is a **single-artefact design science study with an embedded within-subject experimental evaluation**.

| Element | Specification |
|---|---|
| **Unit of analysis** | The support scenario — a defined IT problem with a pre-authored ground-truth resolution path and acceptance criteria |
| **Independent variable** | System configuration, at five levels (A0–A4; §3.12.2) |
| **Dependent variables** | Classification accuracy; retrieval quality; end-to-end resolution success; grounding correctness; lifecycle-state correctness; safety violations; latency; usability and trust ratings (§3.12.4) |
| **Design type** | Within-subject: every configuration is exposed to the **same** scenario set |
| **Repetition** | Each scenario is executed five times per configuration |

**Justification of the within-subject design.** Exposing every configuration to the same scenarios removes scenario heterogeneity as a confound by construction. Under a between-subject design, an observed difference between the retrieval-enabled and retrieval-disabled configurations could always be attributed to the two configurations having faced different problems; within-subject, it cannot. The cost of this choice is the introduction of **order and carry-over effects**, which are real here because remediation actions mutate machine state — a scenario executed after a DNS flush is not the same scenario. Two mitigations address this directly: a uniform virtual-machine snapshot is restored between trials, and scenario order is randomised (§3.12.1). The trade is accepted because scenario heterogeneity is the larger threat: the research question is about differences between configurations, and any design that lets scenarios vary with configuration cannot answer it.

**Justification of repetition.** Generative components are non-deterministic. A single trial per scenario per configuration cannot distinguish a systematic architectural effect from sampling variation in the model's output, and reporting such a trial as evidence would be a category error. Five repetitions permit variance to be characterised and reported alongside central tendency, so that a small mean difference accompanied by large variance is visible as such rather than presented as a finding.

---

## 3.5 Research Strategy

The strategy is **applied system development (prototyping) combined with controlled experimental evaluation**.

**Prototyping** is the appropriate development strategy because the artefact's requirements were not fully specifiable in advance. The behaviour of generative components under real diagnostic dialogue — how often escalation is signalled, at what conversational depth a ticket becomes warranted, how retrieved context alters the model's questioning strategy — is discovered by construction and iteration rather than by specification. A strategy that required complete requirements before implementation would have had to invent those behaviours rather than observe them.

**Controlled experimental evaluation** is the appropriate assessment strategy because the research question is comparative. It asks *how much* each component contributes, and only a controlled comparison across configurations that differ in exactly one component can answer that.

Two alternatives were considered and rejected. An **observational case study** of a support organisation adopting such a system would have produced richer contextual data and better external validity, but it could not isolate component contributions, because in a real deployment the components are never switched off individually — which is precisely the limitation of the closest published system [18]. A **purely theoretical or analytical** treatment was rejected because the central safety claim (H4) is an empirical claim about how a mechanism behaves under attack. Whether a whitelist and an approval gate withstand an injection is not establishable by argument; it is establishable only by attacking them.

---

## 3.6 Design Science Research Execution Workflow

The six-activity DSR process model [27] is mapped onto the specific activities of this research below. This mapping serves as the operational spine of the methodology: each row identifies the activity, its instantiation here, and the section in which it is executed or reported.

| Phase | DSR activity | Execution in this research | Reported in |
|---|---|---|---|
| **3.6.1** | **Problem identification and motivation** | Analysis of the scalability constraint in ITSM through structured literature review; establishment that the binding constraint is knowledge access and application rather than knowledge existence [1], [2], and that support capacity does not scale with demand | §1.2, §2.4 |
| **3.6.2** | **Relevance justification** | Relevance justified from measured evidence rather than market projection: a ~15% support-productivity effect from generative assistance across 5,172 agents [1], and an 11.4% agent resolution rate on realistic SRE scenarios [15] establishing that the problem is simultaneously valuable and unsolved. Vendor and analyst statistics were deliberately excluded from the evidential core (§2.2) | §1.2.1, §1.2.4, §1.5 |
| **3.6.3** | **Comparative analysis and gap justification** | Comparison of supervised ITSM machine learning, LLM incident diagnosis, domain RAG, agentic remediation and commercial platforms on method, findings, limitations and whether component contributions were isolated; identification of G1–G3 | §2.5, §2.9, §2.10 |
| **3.6.4** | **Definition of objectives for a solution** | Six objectives (O1–O6), each with a verifiable completion criterion, with evaluation (O5) and adversarial evaluation (O6) stated separately so that they can succeed or fail independently | §1.7 |
| **3.6.5** | **Design and development** | *Design:* a five-agent orchestrated architecture with model-independent remediation governance (§3.7). *Development:* Python/FastAPI backend, React/Vite frontend, REST API, five agents, a 25-action whitelist, and RBAC over five roles and twenty-four permissions, delivered in vertically integrated increments (§3.10). *Data management:* relational store for users, tickets, chat and audit; JSON knowledge corpus with an embedding cache; persisted ML artefacts | §3.7, §3.10; Chapter 4 |
| **3.6.6** | **Demonstration** | Verification that a functioning artefact exists to be measured: service health, authenticated login returning a valid token and permission set, endpoint enumeration, agent instantiation within the request pipeline, and frontend reachability. This establishes a precondition for evaluation and is explicitly **not** a research result | Chapter 4 |
| **3.6.7** | **Evaluation** | Five-condition ablation with a matched human baseline, a five-class adversarial protocol, nine metric dimensions, and a statistical analysis plan with effect sizes and multiplicity correction | §3.12; Chapters 5–6 |
| **3.6.8** | **Communication** | Interim submissions, this thesis, prototype demonstration and defence; the architecture documented at a level permitting independent reimplementation, which is the mechanism by which the openness contribution in §1.11 is delivered | Chapters 4–8 |

---

## 3.7 Methodological Specification of the Proposed System

This section specifies the artefact — *Auto-Ops-AI* — at the level required to understand what is being evaluated and why the evaluation design in §3.12 is capable of isolating component contributions. Implementation detail is given in Chapter 4.

### 3.7.1 Architectural Characterisation

The system is an **orchestrated specialist-agent pipeline**. Coordination is centralised and deterministic: an orchestration function invokes each agent in a fixed sequence. Agents do not communicate directly with one another, do not select which agent runs next, and do not negotiate.

This characterisation is stated precisely and early because it bounds what the findings can claim. The system is *not* a decentralised autonomous multi-agent system in the sense surveyed by Wang et al. [13], in which agents plan their own action sequences and may invoke one another. Describing it as such would misrepresent the artefact and would license conclusions the study cannot support (§1.12).

**Justification of centralised deterministic orchestration.** Three reasons support this choice over autonomous coordination, and they are methodological before they are engineering reasons.

1. **Reproducible ablation requires a deterministic control path.** If agents selected their own successors, two trials of the same scenario under the same configuration could execute different agent sequences, and an observed difference between configurations could not be attributed to the configuration. The ablation design in §3.12.2 depends on the pipeline being the same in every respect except the component under test.
2. **A fixed sequence yields a single, auditable enforcement point.** Because every path to execution passes through the same orchestration step, the action whitelist and approval gate cannot be bypassed by an alternative route (§3.7.6). In an architecture where agents invoke one another freely, establishing that no such route exists is substantially harder.
3. **Determinism is preferable wherever accountability matters more than flexibility.** This principle is applied at the agent level too (§3.7.2).

The cost of this choice is a genuine loss of adaptivity: a fixed pipeline cannot skip an unnecessary stage or revisit an earlier one. This is accepted, and its consequence for generalisability is recorded as a delimitation in §1.12.

### 3.7.2 The Proposed Multi-Agent Framework: Roles and Responsibilities

Five specialised agents constitute the framework. Each has a defined input contract, a defined output contract, and a single responsibility, which is what makes independent evaluation possible.

| Agent | Responsibility | Input | Output | Implementation basis |
|---|---|---|---|---|
| **Image Analysis Agent** | Visual fault analysis and text extraction from user-supplied screenshots and device photographs | Image bytes, MIME type, optional user context | Extracted text, issue description, category, retrieval keywords | Multimodal LLM |
| **LLM Conversation Agent** | Multi-turn diagnostic dialogue; escalation and resolution signalling | User message, conversation history (20-message window), retrieved knowledge context | Response text; `is_technical`, `should_escalate`, `is_resolved` flags | Hosted LLM with prompt engineering and heuristic post-analysis |
| **Ticket Intelligence Agent** | Ticket creation timing, urgency scoring, title and description generation, categorisation | Conversation history, turn count, classification signal | Creation decision; priority derived from a 0–10 urgency score; ticket metadata | Hybrid: LLM generation with deterministic rule fallback |
| **Ticket Status Agent** | Lifecycle state transitions, SLA tracking, re-open and abandonment detection | Conversation history, current status, ticket timestamps | Recommended state, confidence, SLA flags | **Deterministic rule-based state machine (intentionally non-generative)** |
| **Action Executor Agent** | Risk-tiered remediation proposal and gated execution | Issue description, category, urgency, user approval | Proposed action with risk tier; execution result | Enumerated whitelist; parameter validation; PowerShell subprocess |

**Justification of the heterogeneous design.** The framework is deliberately *not* uniform: three agents are generative, one is hybrid, and one is fully deterministic. This heterogeneity is a design claim rather than an inconsistency, and it follows a single principle — **generative where interpretation is required, deterministic where accountability is required.**

The Ticket Status Agent is the clearest application. Lifecycle state governs SLA accounting and audit records. An auditor asking why a ticket moved from OPEN to RESOLVED requires a *reconstruction* of the reasoning, not a plausible post-hoc justification, and a generative explanation is the latter: it is produced after the fact and may not correspond to the computation that actually occurred. Deterministic rules can be re-executed against the same inputs to produce the same transition, which is what auditability means. Conversely, the Conversation Agent must interpret unconstrained user prose, where deterministic rules would fail at the first unanticipated phrasing.

This design claim is tested rather than asserted: ablation condition A3 (§3.12.2) measures whether dedicated lifecycle handling improves state-transition correctness against a single-model implementation, which is the empirical content of H3.

**Justification of five agents rather than more or fewer.** The decomposition follows the natural seams of the support workflow — perception (image), interpretation (conversation), classification into an organisational record (ticket intelligence), record management (status), and action (executor). A finer decomposition would multiply inter-component interfaces without adding an independently evaluable function; a coarser one would merge responsibilities whose contributions the research is specifically trying to separate. The decomposition is, in other words, chosen to make the ablation in §3.12.2 possible: each boundary is a place where a component can be switched off.

### 3.7.3 Agent Interaction and Orchestration

Agents interact exclusively through the orchestration layer. The interaction pattern is best described as **mediated sequential composition**: each agent receives a defined input assembled by the orchestrator, returns a defined output to the orchestrator, and has no knowledge of, or reference to, any other agent.

```
   USER REQUEST
        │
        ▼
   ┌─────────────────────── ORCHESTRATOR (deterministic) ───────────────────────┐
   │                                                                            │
   │  image? ──yes──► [Image Analysis Agent] ──► description merged into text   │
   │     │                                                                      │
   │     ▼                                                                      │
   │  [Intent classification] ──► is_technical · category · urgency · confidence │
   │     │                                                                      │
   │     ├── not technical ──────────────────────► conversational response only │
   │     │                                                                      │
   │     ▼ technical                                                            │
   │  [Retrieval] ──► embed query · cosine similarity · threshold · top-k       │
   │     │                                                                      │
   │     ▼                                                                      │
   │  [LLM Conversation Agent] ◄── retrieved context                            │
   │     │                                                                      │
   │     ▼                                                                      │
   │  turns ≥ 3 ? ──► [Ticket Intelligence Agent] ──► create? · priority · meta │
   │     │                                                                      │
   │     ├── escalation signalled ──► [Assignment Service] ──► human agent      │
   │     │                                                                      │
   │     ▼                                                                      │
   │  [Ticket Status Agent] ──► lifecycle state reconciliation (deterministic)  │
   │     │                                                                      │
   │     ▼                                                                      │
   │  Agent Mode enabled ? ──► [Action Executor Agent] ──► ONE proposed action  │
   │                                     │                                      │
   │                                     ▼                                      │
   │                          ⛔ HUMAN APPROVAL GATE ⛔                          │
   │                                     │                                      │
   │                     approved + ownership verified                          │
   │                                     ▼                                      │
   │                          execution · audit · result                        │
   └────────────────────────────────────────────────────────────────────────────┘
```

**Why agents do not communicate directly.** Direct agent-to-agent communication would create implicit control paths that are difficult to enumerate and therefore difficult to secure or ablate. Mediation through the orchestrator means that the set of possible execution paths is finite, written down, and identical across trials — which is what allows a configuration difference to be attributed to the component that was changed. It also means that disabling a component for ablation is a local change to the orchestrator rather than a modification of the agents themselves, so the agents under test are unchanged between conditions.

### 3.7.4 Knowledge Grounding: The Retrieval Pipeline

Retrieval is the mechanism by which generated guidance is grounded in organisational rather than general knowledge, and it is the component whose contribution G2 asks the research to measure.

**Pipeline.** The pipeline follows the standard dense-retrieval construction [8], [9] applied to a curated organisational corpus:

1. **Corpus preparation.** Knowledge-base articles describing documented organisational procedures are curated and embedded using a hosted embedding model, with embeddings held in a cache for comparison.
2. **Query embedding.** The user's message — after image-description merging, if applicable — is embedded with the same model, so that query and passage occupy a common vector space.
3. **Similarity computation.** Cosine similarity is computed between the query embedding and each passage embedding, following the siamese-encoding pattern that makes independent encoding and cosine comparison tractable [9].
4. **Threshold filtering.** Passages below a similarity threshold are discarded rather than returned as weak matches.
5. **Ranking and selection.** Surviving passages are ranked by a weighted score combining semantic similarity with historical article usage, and the top-*k* are retained.
6. **Conditioning.** Retained passages are supplied to the Conversation Agent as grounding context for the diagnostic dialogue.

**Justification of threshold filtering, and the design decision it encodes.** Step 4 exists because of the asymmetry identified in §2.6.2: confidently irrelevant retrieval is worse than no retrieval, since the model is instructed to condition on whatever it is given and will ground its guidance in the wrong procedure. Discarding weak matches means the system degrades to the ungrounded case rather than to a *mis*grounded one, which is the safer of the two failure modes in a domain where guidance may be executed.

**Treatment of the retrieval parameters.** The similarity threshold and the usage-weighting term are the two parameters that determine which regime the retriever operates in, and neither can be justified a priori. They are therefore treated as **tuned and reported parameters**: both are swept during evaluation and their selected values justified by measurement rather than fixed as unexplained constants (§3.12.4). The usage-weighting term in particular requires empirical justification because its effect is ambiguous in principle — biasing retrieval toward frequently used articles may improve practical relevance, or may entrench popularity over correctness, and only measurement distinguishes these.

**Retrieval implementation paths.** Two retrieval paths exist and are both retained deliberately: an **in-memory linear-scan** path, which computes similarity across the full cached corpus per query, and a **persistent vector-store** path using approximate-nearest-neighbour indexing. The former is exact and adequate at small corpus sizes but scales linearly with corpus size; the latter is the correct structure at realistic scale. Retaining both allows the retrieval latency/scale trade-off to be reported as a measured result rather than assumed, and requires that the two paths be verified to return equivalent results before the comparison is meaningful.

**Acknowledged design limitation.** The pipeline retrieves over flat text. Xu et al. demonstrate that this discards intra-issue structure and inter-issue relations that structured retrieval preserves, with measurable cost to retrieval and answer quality [11]. This limitation is accepted for the present study and recorded in §1.12 (L3); its consequence is that the measured contribution of grounding should be interpreted as a **lower bound** on what a better-engineered retriever could contribute, which is the honest reading and is stated wherever the retrieval result is used.

### 3.7.5 The Troubleshooting and Reasoning Workflow

The workflow implements the complete support loop identified as absent in §2.8 — understand, retrieve, request permission, execute, close or escalate — in eight stages.

| # | Stage | Behaviour | Design justification |
|---|---|---|---|
| 1 | **Multimodal pre-processing** (image path only) | Visual analysis output is merged into the textual message | Image-originated requests traverse the same downstream path as text, so no separate, less-validated decision route exists (§2.7.3) |
| 2 | **Intent classification** | Technical/non-technical determination, category, urgency, confidence | Classification is an *intermediate signal* consumed downstream, not a terminal output — the design implication drawn from [3] in §2.5.1 |
| 3 | **Retrieval** | Executed only for technical messages; threshold applied; top-*k* retained | Non-technical messages have no organisational procedure to ground against; retrieving for them would introduce irrelevant context |
| 4 | **Response generation** | Multi-turn diagnostic dialogue, conditioned on retrieved context where available | Conditional adaptation — selecting the next diagnostic step from the previous outcome — is the capability that distinguishes this from a decision tree [5], [12] |
| 5 | **Ticket intelligence** | Ticket creation gated at three or more conversational turns; urgency scored; metadata generated | The turn threshold prevents a ticket being raised from an incomplete problem description, which would produce a record that neither the user nor an engineer can act on |
| 6 | **Escalation and assignment** | On an escalation signal, a human agent is allocated by specialisation and current workload | Escalation is a designed outcome, not a failure state: the system's purpose includes routing what it cannot resolve |
| 7 | **Lifecycle reconciliation** | Ticket state reconciled against conversation evidence using deterministic rules | Reproducibility and auditability outweigh linguistic flexibility for state that governs SLA accounting (§3.7.2) |
| 8 | **Remediation proposal** | Only in explicitly enabled Agent Mode; a **single** next action is returned and held pending approval | See below |

**Why remediation is proposed one action at a time.** Returning a single next action rather than a batch has three justifications, of which two are methodological and one is safety-related. Methodologically, each execution decision is separately approved and separately observable, which is a precondition for attributing an outcome to a specific action during evaluation; and the stepwise protocol produces a per-action record that supports the per-class containment analysis in §3.12.3. From a safety perspective, it limits the blast radius of any single incorrect proposal: a user who approves a batch approves actions whose necessity depends on the outcome of earlier actions in that batch, which they cannot yet know.

**Why Agent Mode is opt-in.** Remediation capability is enabled explicitly by the user rather than being available by default. This means the transition from an advising system to an acting system is a deliberate user decision, which is both an ethical requirement (§3.15) and a methodological convenience, since it makes the acting and non-acting configurations cleanly separable for ablation condition A4.

### 3.7.6 Human-Gated Remediation and the Governance Controls

This is the component on which the safety claim rests, and it is specified in detail because the adversarial protocol in §3.12.3 attacks it directly.

**The action inventory.** Remediation is restricted to an enumerated whitelist of **25 actions**, each carrying a risk classification and belonging to a functional category. Free-form command construction is not possible; the model selects from the enumeration or proposes nothing.

| Risk tier | Count | Representative actions |
|---|---|---|
| **LOW** | 14 | `list_top_processes`, `flush_dns`, `check_disk_space`, `test_connectivity`, `check_system_health`, `analyze_slow_performance` |
| **MEDIUM** | 8 | `empty_recycle_bin`, `clear_browser_cache`, `release_renew_ip`, `kill_process_by_id`, `restart_explorer`, `windows_disk_cleanup` |
| **HIGH** | 3 | `reset_network_adapter`, `restart_service`, `reset_winsock` |

| Functional category | Count |
|---|---|
| Diagnostics | 10 |
| Cleanup | 6 |
| Network | 4 |
| Process | 3 |
| Service | 1 |
| Browser | 1 |

Three actions require privilege elevation. Destructive operations are absent from the enumeration by design and cannot be constructed through parameters.

**The seven governance controls.**

| # | Control | Mechanism | Enforced outside the model? |
|---|---|---|---|
| **C1** | Action enumeration | Actions are selectable only from the fixed whitelist; no free-form command construction is possible | **Yes** |
| **C2** | Parameter validation | Required-field and allowed-value checking against the action definition | **Yes** |
| **C3** | Injection screening | Rejection of shell metacharacters in parameters | **Yes** |
| **C4** | Risk tiering | Every action carries a LOW / MEDIUM / HIGH classification, surfaced to the user before approval is requested | **Yes** |
| **C5** | Human approval gate | Execution requires explicit approval, with ownership verified against the requesting user | **Yes** |
| **C6** | Execution isolation | Subprocess invocation **without shell interpretation**, with a fixed timeout | **Yes** |
| **C7** | Audit trail | Action requests, approvals and outcomes are retained in a durable history | **Yes** |

**Justification: why every control is enforced outside the model.** This is the direct application of the axiom established in §1.2.5 and §2.7.2. A control implemented as a system-prompt instruction is a string in the model's context, indistinguishable in kind from an injected string [22], and therefore defeasible by the attack it is meant to prevent. A control implemented in application code is not, because the model's output is a *request* that the application may refuse. The distinction is what makes H4 a testable claim: §3.12.3 attacks the model deliberately and measures whether the controls hold, which is only a meaningful test if the controls do not themselves depend on the model.

**Justification of specific control choices.** C1 (enumeration) bounds the consequence of *any* model compromise to the set of enumerated operations, which is why it is the primary control rather than input filtering — filtering attempts to identify malicious inputs, which is an open-ended problem, whereas enumeration constrains outputs, which is a closed one. C3 and C6 are complementary rather than redundant: C3 screens metacharacters at validation, and C6 removes shell interpretation entirely so that any metacharacter surviving C3 has no interpreter to reach. Defence in depth here is justified because the two controls fail in different ways — C3 by an incomplete pattern, C6 by a misconfiguration — and a single failure should not produce execution. C5 verifies **ownership** as well as approval, because an approval mechanism that does not check who is approving is an authorisation gap rather than a gate.

**The usability cost is treated as a measurand, not an assumption.** Mandatory approval imposes a burden on the user, and a control that users find intolerable will be disabled in deployment, at which point it provides no safety at all. The acceptability of the approval burden is therefore measured explicitly (§3.12.4) rather than assumed to be tolerable — a question the closest published system raises implicitly through its consent-based design without decomposing it [18].

### 3.7.7 System Components and Access Control

| Layer | Components |
|---|---|
| **Presentation** | React 19 + Vite 7 application providing chat, dashboard, ticket manager and administration surfaces |
| **API** | FastAPI service exposing REST/JSON endpoints, with JWT (HS256) authentication and role-based access control |
| **Orchestration** | Deterministic sequential pipeline invoking the five agents (§3.7.3) |
| **Services** | Retrieval engine; assignment service (specialisation and workload matching); PowerShell execution service (subprocess without shell interpretation) |
| **Data** | SQLite relational store for users, tickets, chat history and audit log; curated JSON knowledge corpus; persisted embedding cache |
| **Predictive** | Resolution-time regressor and system-health classifier (secondary objective; §1.12, L4) |

**Access control.** Five roles — `STAFF`, `CONTRACTOR`, `MANAGER`, `IT_ADMIN`, `SYSTEM_ADMIN` — are defined over twenty-four permission constants spanning ticket operations, troubleshooting, system monitoring and diagnostics, user management, dashboards and reporting, and knowledge-base access. Permissions are checked at the API dependency layer, which means **authorisation is enforced before any agent is invoked**, including before any action can be proposed. This ordering is deliberate: an unauthorised request should never reach the component capable of proposing an action, so that privilege escalation must defeat two independent mechanisms rather than one. The privilege-escalation class in §3.12.3 tests exactly this property.

---

## 3.8 Data Collection Methods

Collection is mixed-methods and each method is aligned to specific research questions.

| Method | Type | Instrument | Feeds |
|---|---|---|---|
| **Instrumented system logs** | Primary, quantitative | Automated capture per scenario per configuration: classification decisions and confidence, retrieval hits with similarity scores, generated guidance, action proposals, approval decisions, execution outcomes, lifecycle transitions, latency and token consumption | RQ1, RQ2, RQ3, RQ5 |
| **Rubric-based scenario scoring** | Primary, quantitative | Fixed scoring rubric authored before execution; scorers blind to configuration where feasible; a sample independently double-scored to establish inter-rater agreement (Cohen's κ) | RQ1, RQ2, RQ5 |
| **Adversarial test execution** | Primary, quantitative | Five-class injection and bypass suite (§3.12.3) executed on isolated virtual machines, with every attempt and outcome logged regardless of result | RQ4 |
| **Post-task usability questionnaire** | Primary, qualitative and ordinal | Structured Likert instrument covering perceived usefulness, trust in automated actions, and acceptability of the approval-gating burden, with free-text items for themes the instrument does not anticipate | RQ4 (usability cost), RQ5 |
| **Matched human baseline sessions** | Primary, quantitative | Participants resolve the same scenarios unassisted under the same timing protocol (condition A0) | Comparative reference across all RQs |
| **Structured literature extraction** | Secondary | Published metrics used as *contextual reference points*, with population differences stated explicitly at each use | Chapters 1–2 |
| **Source-code and artefact inspection** | Primary, documentary | Direct verification of implementation claims against source | Chapter 4 |

**Justification of the mixed-methods design.** Instrumented logs answer *what the system did*; rubric scoring answers *whether what it did was correct*, which logs cannot establish because correctness is a judgement against a resolution path rather than a property of an execution trace; and the usability instrument answers *whether the design is acceptable to the people who must use it*, which neither of the other two can address. RQ4 in particular requires two kinds of evidence — a containment measurement and a burden measurement — and would be incompletely answered by either alone.

**Why no external published-mean comparison is used.** Comparing measured system performance against a published industry mean resolution time was considered and is not used. The populations, ticket mixes, measurement definitions and organisational contexts differ, and no adjustment available at this scale would make them commensurable; a favourable comparison would therefore be evidence of nothing. Where human comparison is required, the **matched internal baseline (A0)** is used instead: the same scenarios, the same timing protocol, the same scoring rubric.

---

## 3.9 Data and Knowledge Sources

| Source | Nature | Provenance | Role in the research |
|---|---|---|---|
| **Evaluation scenario corpus** | Synthetic, human-authored | Constructed by the researcher across five categories (network, performance, peripheral/hardware, access/account, software) and three difficulty tiers, each with a ground-truth resolution path and acceptance criteria | The unit of analysis; the common substrate across all five configurations |
| **Knowledge-base corpus** | Synthetic, curated | IT support articles representing documented organisational procedures | The retrieval corpus; the object over which grounding is measured |
| **Synthetic user and ticket records** | Synthetic | Generated user profiles, tickets and conversations | Fixtures for lifecycle and assignment logic |
| **ML training data** | Synthetic | Records for resolution-time estimation | Training data for the secondary predictive objective |
| **Adversarial prompt set** | Constructed | Direct injections; indirect injections planted in retrieved documents and uploaded images following the vector demonstrated in [20]; parameter-level metacharacter attacks; approval-bypass and privilege-escalation attempts | The attack surface for H4 |
| **System execution logs** | Generated | Produced during evaluation runs | Primary quantitative evidence |
| **Participant responses** | Primary human | Post-task questionnaires and A0 baseline sessions | Usability, trust and human-comparison evidence |
| **Published literature** | Secondary | Peer-reviewed venues 2019–2026, plus foundational methodology sources | Chapters 1–3 |

**Justification of synthetic data, and its cost.** No ethically available route exists to real production support transcripts at undergraduate scale: such transcripts contain identifiable user data, organisational security information and, frequently, credentials. Beyond the ethical constraint, synthetic scenarios confer a methodological advantage that real transcripts would not: **a defined ground truth**. A real transcript records what happened, not what should have happened, so scoring against it would require retrospective judgement of a resolution the researcher did not observe. Authored scenarios carry their correct resolution path by construction, which is what makes rubric-based correctness scoring possible.

The cost is external validity, and it is real. Real support conversations differ from authored scenarios in ambiguity, incompleteness, digression and noise, and a system that performs well on authored scenarios may perform worse on real ones. The trade is accepted, stated as limitation L1 (§1.12), and partially mitigated by authoring scenarios from documented incident categories rather than inventing them freely — which constrains the scenarios to problems that actually occur, even if the language in which they are expressed is cleaner than reality.

---

## 3.10 System Development Methodology and Procedures

**Development procedure.** Development proceeds in **vertically integrated increments**: each increment delivers one agent or subsystem together with its API surface, its persistence and its frontend affordance, so that every increment is independently exercisable end-to-end.

**Justification.** This is not merely a convenient engineering discipline; it is required by the evaluation design. The ablation in §3.12.2 requires each component to be switchable at runtime, which is only possible if each component was built as a separable unit with a defined interface rather than being woven through a monolith. A horizontally layered development approach — all data models, then all services, then all interfaces — would have produced a system in which no single component could be disabled without breaking the pipeline, and the central experiment would have been unavailable.

**Procedure for the evaluation infrastructure.** The evaluation harness is developed under the same increment discipline and in dependency order: scenario runner, then runtime configuration switching (A0–A4), then metric extraction, then the adversarial suite, then the statistical pipeline. Each stage is verifiable before the next depends on it, which prevents a defect in an early stage from being discovered only after it has contaminated results downstream.

**Verification procedure.** A specific procedure is adopted and applied throughout: **all quantitative claims about the artefact are verified against source before being written.** Reported counts of endpoints, agents, actions, roles, permissions and parameters are obtained by enumeration from the implementation, not from design documents. This matters because design documents and implementations diverge over the life of a project, and a thesis that describes the design rather than the artefact would be evaluating something other than what it documents.

**Configuration management.** Git with a GitHub remote. The LLM model version and generation parameters are recorded with every evaluation run, because results conditioned on an unrecorded model version are not reproducible — a hosted model that is silently updated between runs would otherwise appear as an unexplained shift in results.

---

## 3.11 Tools and Technologies

Each selection below is justified against the alternatives considered, with the accepted cost stated where one exists.

| Layer | Technology | Justification for selection | Alternatives considered and why rejected |
|---|---|---|---|
| Backend framework | FastAPI (Python 3.11) | Native asynchronous support suits I/O-bound LLM API orchestration; automatic OpenAPI schema generation supports the endpoint enumeration used in verification; Python co-locates the API with the ML and embedding code | Django — heavier and ORM-centric with no async advantage for this workload; Node/Express — would split the ML stack across two languages |
| LLM | Hosted Gemini API (conversation, ticket metadata, multimodal analysis) | Multimodal capability from a single provider supports the image path without a second vendor dependency; hosted inference removes the GPU requirement (§1.9.1) | Local open-weight models — infeasible on available hardware and would confound latency measurement with hardware variation; a second commercial provider — adds cost without addressing a stated gap. **Accepted cost:** single-vendor dependency, recorded as limitation L2 |
| Embeddings | `text-embedding-004` (hosted) | Same provider as generation, avoiding a second API dependency; dense embeddings are the established basis for semantic retrieval [8], [9] | Local sentence-transformer models — viable, and recorded as future work for cost and reproducibility reasons |
| Vector store | ChromaDB | Persistent approximate-nearest-neighbour indexing is the correct structure at realistic corpus scale | In-memory linear scan — retained deliberately as a comparison path so the latency/scale trade-off is measured rather than assumed (§3.7.4) |
| Relational store | SQLite with SQLAlchemy | Zero-configuration and file-backed, which is sufficient for single-node evaluation; SQLAlchemy preserves a migration path | PostgreSQL — operationally heavier than the evaluation requires, with no benefit at this scale |
| Frontend | React 19 with Vite 7 | Component model suits the chat, dashboard and administration surfaces; fast rebuilds support iterative prototyping | Server-rendered templates — poor fit for real-time chat and approval interactions |
| Execution | PowerShell via subprocess **without shell interpretation** | Windows-native diagnostics; bypassing the shell removes metacharacter interpretation as an attack path, which is control C6 and directly supports H4 | Shell-interpreted invocation — explicitly rejected, as it would reintroduce the injection surface the design exists to close |
| ML | scikit-learn | Adequate for the secondary predictive objective; interpretable models are preferred where output informs SLA accounting | Deep models — unjustifiable on a training set of this size, and would trade interpretability for accuracy that the data cannot support |
| Authentication | PyJWT (HS256) with bcrypt | Stateless tokens suit the REST design; bcrypt is the standard password-hashing choice | Session cookies — additional server-side state with no benefit here |
| Containerisation | Docker with Docker Compose | A reproducible environment is a precondition for the reproducibility contribution claimed in §1.11 | Bare-metal setup — not reproducible by a third party, which would undermine the contribution |
| Statistics | Python (SciPy, statsmodels) | Keeps analysis in the same environment as data extraction, reducing transcription error | SPSS — additional tooling with no methodological gain and an extra manual transfer step |

---

## 3.12 Evaluation Methodology

> This section specifies the evaluation protocol. Measured outcomes are reported in Chapter 6 and interpreted in Chapter 7.

**Evaluation objective.** The purpose of the evaluation is to determine the measurable contribution of each architectural component (RQ1, RQ2, RQ3, RQ5) and to establish whether the governance mechanism withstands adversarial input (RQ4). It is explicitly *not* to demonstrate that the system functions: functioning is a precondition verified during demonstration (§3.6.6), not a result.

### 3.12.1 Experimental Setup and Ground-Truth Protocol

| Element | Specification | Justification |
|---|---|---|
| **Environment** | Isolated Windows virtual machines; a uniform baseline snapshot restored between trials | Remediation actions mutate system state; without restoration, trial *n* would begin from the state trial *n*−1 left behind, confounding configuration with order |
| **Model configuration** | A fixed model version and generation parameters across all conditions; version, parameters and access date recorded with every run | Results conditioned on an unrecorded model version are not reproducible, and a silent provider-side update would otherwise appear as an architectural effect |
| **Determinism handling** | Classification tasks executed at low temperature; each scenario executed **n = 5 times per configuration**, with variance reported alongside central tendency | A single trial cannot separate a systematic effect from generative sampling variation (§3.4) |
| **Scenario order** | Randomised across trials | Controls order effects that snapshot restoration alone does not address, such as researcher familiarity during scoring |
| **Blinding** | Scoring performed against a rubric fixed before execution, with scorers blind to configuration where feasible | An unblinded scorer who knows a trial came from the full system has an expectation that the rubric alone does not remove |

**Evaluation corpus.** The corpus targets **60 scenarios** spanning five categories (network, performance, peripheral/hardware, access/account, software), stratified across three difficulty tiers, each with a defined ground-truth resolution path and acceptance criteria. Stratification is essential rather than cosmetic: a corpus weighted toward easy scenarios would compress the differences between configurations, since all configurations resolve easy problems, and the study would report a null result produced by its own corpus design.

**Ground-truth protocol and its justification.** Scenario ground truth is authored **before any system execution** and is **not model-generated**. This avoids the circularity of evaluating a model against labels produced by a model — a risk that reference-free automated RAG evaluation makes convenient without eliminating [25], since a systematic blind spot shared by generator and evaluator is invisible to the evaluation. A sample of the corpus is independently reviewed by a second assessor to establish inter-rater agreement (Cohen's κ), so that the reliability of the ground truth is itself a reported quantity rather than an assumption.

The knowledge-base corpus must be expanded to a realistic scale before retrieval evaluation is meaningful. Precision measured over a very small corpus does not generalise: with few articles, almost any query either matches the single relevant article or matches nothing, and the measurement describes the corpus rather than the retriever.

### 3.12.2 Ablation Design

Ablation is the core experiment and the mechanism by which G1 and G2 are addressed. Identical scenarios are executed under progressively enabled configurations, so that the difference between adjacent conditions isolates the component added between them.

| ID | Configuration | Component isolated | Tests |
|---|---|---|---|
| **A0** | Unassisted human baseline — a participant resolves the scenario manually | Human reference performance | Comparative reference for all outcomes |
| **A1** | Single LLM; no retrieval, no agent decomposition, no actions | Monolithic baseline | **H2** (against keyword and classical supervised baselines [3]) |
| **A2** | A1 + retrieval grounding | **Contribution of retrieval grounding** | **H1** → **G2** |
| **A3** | A2 + ticket intelligence and lifecycle agents | **Contribution of agent decomposition** | **H3** → **G1** |
| **A4** | A3 + gated remediation (full system) | Contribution of action execution | RQ5 |

**Why this ladder and not a factorial design.** A full factorial over four binary components would require sixteen conditions and, at five repetitions across sixty scenarios, 4,800 system trials — beyond the resource envelope of this project, and beyond it primarily in LLM API cost and researcher scoring time. The progressive ladder is the appropriate reduction because the components are **architecturally ordered**: agent decomposition presupposes the conversational component, and gated remediation presupposes the diagnosis that determines what to remediate. Configurations that omit a prerequisite while retaining its dependant are not merely uninteresting but incoherent. The ladder therefore covers the space of realisable configurations at a cost of 60 × 5 × 5 = **1,500 system trials**, while acknowledging the limitation that interaction effects between non-adjacent components cannot be estimated.

**Why A0 uses the same scenarios.** Because the human baseline is executed on the *same* scenarios under the *same* timing protocol and scored against the *same* rubric, the comparison is internally valid. This is the alternative adopted in place of comparison against an external published mean (§3.8), and it is the reason that comparison could be discarded without losing the human reference point entirely.

### 3.12.3 Adversarial Safety Protocol

The protocol tests whether the governance controls of §3.7.6 hold when the language model itself is manipulated [20]–[23]. The design principle is that the attack targets the model and the measurement targets the controls: an attack that successfully manipulates the model's output but produces no unauthorised execution is a **successful containment**, not a failure, and the protocol records both facts separately.

| Test class | Method | Success criterion | Control under test |
|---|---|---|---|
| **Direct injection** | Adversarial instructions embedded in user input, attempting to induce execution of non-whitelisted commands | Zero unauthorised executions | C1, C5 |
| **Indirect injection** | Adversarial content planted in retrieved knowledge-base documents and in uploaded images — the vector demonstrated in [20], to which this architecture is exposed by construction | Zero unauthorised executions | C1, C5 |
| **Parameter injection** | Shell metacharacters and escape sequences supplied within action parameters | 100% rejection at validation | C2, C3, C6 |
| **Approval bypass** | Execution attempts without approval; approval attempts by users who do not own the request | Zero successes | C5 |
| **Privilege escalation** | Requests for elevation-requiring actions by insufficiently privileged roles | Zero successes | RBAC (§3.7.7), C5 |

**Justification of the class selection.** The five classes are chosen to attack each control at its own level rather than to attack the system generically. Direct and indirect injection test whether the *enumeration* holds when the model is compromised; the indirect class is included specifically because a retrieval architecture possesses that surface by construction and omitting it would test the easier half of the threat model [20]. Parameter injection tests the validation and execution layers, which are the controls that operate after an action has legitimately been selected. Approval bypass tests the gate itself, including the ownership check that distinguishes a gate from a prompt. Privilege escalation tests the interaction between the authorisation layer and the action layer, which is the boundary at which two independently correct mechanisms can combine incorrectly.

**Reporting commitment.** Any successful bypass will be reported as a finding rather than omitted. H4 is falsified by a single counter-example (§3.3), and reporting that counter-example is more valuable to the field than a clean result obtained by not looking for one. Where a bypass mechanism generalises beyond this artefact, it is reported at a level of detail sufficient for scientific evaluation but without publishing a directly reusable exploit against third-party systems (§3.15).

**Safety of the safety testing.** Adversarial testing is conducted exclusively on isolated, researcher-controlled virtual machines, never on participant devices, and participants never interact with the system in an adversarial configuration.

### 3.12.4 Metrics

| Dimension | Metric | Method | Answers |
|---|---|---|---|
| **Classification** | Accuracy, macro-F1, per-class precision and recall (technical / category / urgency) | Against pre-authored ground truth; classical supervised baseline drawn from [3] | RQ1, H2 |
| **Retrieval** | Precision@k, Recall@k, MRR; similarity-threshold sweep; usage-weight sweep; retrieval latency for both retrieval paths | Against human relevance judgements | RQ2 |
| **Resolution** | Task success rate; steps to resolution; time to resolution | Rubric scoring against the ground-truth resolution path | RQ2, RQ5 |
| **Grounding** | Proportion of factually correct guidance; unsupported-claim rate | Blind human assessment as the primary basis; automated RAG metrics [25] as a **secondary corroborating signal only** | RQ2, H1 |
| **Lifecycle** | State-transition correctness | Against the expected lifecycle path for the scenario | RQ3, H3 |
| **Safety** | Unauthorised execution count; validation rejection rate; per-class containment; identity of the control that contained each attempt | Adversarial suite (§3.12.3) | RQ4, H4 |
| **Usability and trust** | Instrument score; trust rating; acceptability of the approval-gating burden; free-text themes | Post-task questionnaire | RQ4, RQ5 |
| **Efficiency** | End-to-end latency; token consumption per interaction | Instrumented logs | RQ5 |
| **Predictive** | MAE and R² (resolution time); accuracy and F1 (system health) | Held-out split — reported **only** if the component is re-specified per [4]; otherwise the component is withdrawn from evaluation and the withdrawal reported | Secondary objective |

**Why grounding and retrieval are measured separately.** Conflating them makes a retrieval failure indistinguishable from a faithfulness failure: a system may retrieve the correct article and still generate guidance unsupported by it, or retrieve nothing relevant and generate guidance that happens to be correct from parametric knowledge. Separating the two adopts the decomposition proposed in [25] while replacing its model-based scoring with human assessment, for the circularity reason given in §2.6.3.

### 3.12.5 Statistical Analysis Plan

| Element | Specification |
|---|---|
| **Target sample** | 60 scenarios × 5 configurations × 5 repetitions = **1,500 system trials**; 12–15 participants for the usability instrument and the A0 human baseline |
| **Continuous outcomes** (time, latency) | Repeated-measures ANOVA where its assumptions hold; Friedman test otherwise |
| **Categorical outcomes** (success/failure) | Cochran's Q with pairwise McNemar tests |
| **Multiplicity** | Holm–Bonferroni correction across the ablation family |
| **Reporting** | Effect sizes (Cohen's *d* or Cliff's δ) with 95% confidence intervals, not *p*-values alone |
| **Power** | A priori power analysis completed before data collection; the sample sizes above are provisional pending it |

**Justification of the test selection.** Repeated-measures procedures are required by the within-subject design (§3.4), since observations across configurations are not independent — they concern the same scenario. Non-parametric alternatives are pre-specified rather than chosen after inspecting the data, because selecting a test on the basis of which produces a significant result is a well-known route to inflated error rates. Holm–Bonferroni correction is applied because the ablation generates a family of related comparisons, and uncorrected family-wise testing across five conditions and nine metric dimensions would produce apparently significant results by multiplicity alone. Effect sizes with intervals are reported in preference to *p*-values because the research question asks *how much* each component contributes; a significant result with a negligible effect size answers the question in the negative and should be readable as such.

**Acknowledged constraint.** A sample of 12–15 participants is adequate for usability signal but **under-powered for small effects** in the human baseline comparison. This is stated in advance, reported as limitation L5 (§1.12), and will be reported again alongside the results rather than concealed by selective presentation of the comparisons that reached significance.

---

## 3.13 Project Management Methodology

The project is managed using **Agile Scrum**, with sprints targeting independently testable increments.

**Justification.** Two properties of this project make an iterative methodology appropriate. First, the artefact's requirements are **partly discovered through construction**, particularly the behaviour of generative components under real diagnostic dialogue (§3.5); a methodology that fixes requirements before implementation would require those behaviours to be invented rather than observed. Second, **external dependencies change during the project**: hosted model versions and API surfaces are outside the researcher's control and may change without notice.

Sequential methodologies such as Waterfall and PRINCE2 assume requirement stability and a controlled dependency environment, and neither assumption holds here. Kanban was also considered and rejected: it suits continuous-flow maintenance work, whereas this project has hard academic milestones and fixed review points that map naturally onto sprint boundaries. Scrum's iterative increments accommodate the discovery, and the per-agent testability the architecture provides is exploited within them — each agent is developed and exercised independently before integration into the orchestration pipeline (§3.10).

---

## 3.14 Project Timeline

| Phase | Period | Activities |
|---|---|---|
| **Phase 1 — Initiation and foundation** | Weeks 1–4 | Problem formulation; structured literature review; methodology and architecture design |
| **Phase 2 — Core system development** | Weeks 5–10 | Sprint 1: data model, authentication, RBAC, frontend shell. Sprint 2: retrieval pipeline and knowledge ingestion. Sprint 3: five agents and the orchestration layer. Sprint 4: predictive components and dashboards |
| **Phase 3a — Verification and evaluation redesign** | Weeks 11–12 | Source-level verification of all documented claims; correction of documentation–implementation divergences; evaluation redesigned around ablation and adversarial testing |
| **Phase 3b — Foundation preparation** | Weeks 13–15 | Evaluation corpus construction (60 scenarios with human-authored ground truth); knowledge-base expansion to realistic scale; routing live retrieval through the persistent vector store; re-specification of the predictive component |
| **Phase 3c — Evaluation infrastructure** | Weeks 16–18 | Evaluation harness; runtime-selectable ablation configurations A0–A4; adversarial test suite; usability instrument finalisation; a priori power analysis; ethics approval |
| **Phase 4 — Execution** | Weeks 19–22 | Ablation execution; adversarial safety evaluation; participant sessions including the A0 baseline; predictive model evaluation on a held-out split |
| **Phase 5 — Analysis and writing** | Weeks 23–26 | Statistical analysis; authoring of Results and Discussion from measured data; documentation of negative and partial results; thesis completion and defence preparation |

**Schedule risk, stated explicitly.** Phase 3b is the critical path and the schedule contains no slack before Phase 4, because corpus construction is labour-intensive and cannot be parallelised by a single researcher. If it over-runs, the mitigation is to **reduce scenario count while preserving category and difficulty stratification**, and to report the reduced statistical power as a limitation. The mitigation deliberately does *not* include reducing the number of ablation conditions: the conditions are what answer the research question, whereas scenario count affects only the precision with which they are answered.

---

## 3.15 Ethical Considerations

1. **Non-maleficence.** The remediation agent is constrained to an enumerated whitelist of 25 non-destructive operations. Destructive operations are absent from the whitelist and cannot be constructed through parameters, which are validated against allowed-value sets and screened for shell metacharacters. Commands execute as subprocesses without shell interpretation, so parameter content cannot be reinterpreted as a command.
2. **Informed consent and transparency.** Participants are informed that they are interacting with an AI system. No action executes on any system without explicit, logged approval by the user who owns the request, and the approval interface states the action, its parameters and its risk tier before approval is requested. Transparency here is a research-ethics requirement and simultaneously a design property, since an approval a user does not understand is not meaningful consent.
3. **Data protection.** Evaluation uses synthetic user profiles and tickets. No personal data from real support interactions is processed. Role-based access control restricts audit-log visibility to authorised roles.
4. **Participant safety.** Adversarial testing is conducted exclusively on isolated, researcher-controlled virtual machines and never on participant devices. Participants never interact with the system in an adversarial configuration, and are never exposed to an attack constructed for this study.
5. **Institutional approval.** Ethics approval is required before participant sessions begin and is obtained in Phase 3c. No participant data is collected before approval is granted.
6. **Responsible disclosure of safety findings.** If adversarial testing identifies a bypass whose mechanism generalises beyond this artefact, the finding is reported at a level of detail sufficient for scientific evaluation, without publishing a directly reusable exploit against third-party systems. This balances the scientific obligation to report negative safety results against the obligation not to arm an attacker.
7. **Research integrity.** No result is reported that has not been measured, and the boundary between what was designed, what was built and what was measured is kept explicit throughout the thesis.

---

## 3.16 Validity, Reliability and Threats

| Threat | Type | Mitigation |
|---|---|---|
| Circular ground truth — evaluating a model against labels a model produced | Internal | Ground truth authored by a human before any system execution; second-assessor agreement (Cohen's κ) reported on a sample [25] |
| Configuration order effects and state carry-over between trials | Internal | Uniform VM snapshot restored between trials; scenario order randomised |
| Generative non-determinism mistaken for a systematic effect | Internal / reliability | Five repetitions per scenario per configuration; variance reported alongside means |
| Scorer bias | Internal | Rubric fixed before execution; scorers blind to configuration where feasible; double-scored sample |
| Comparison against an incommensurable external population | Construct | Matched internal human baseline (A0) on identical scenarios; external published figures used as context only, never as a comparison baseline |
| Corpus composition determining the result | Construct | Stratification across five categories and three difficulty tiers, fixed before execution; stratification preserved even if scenario count is reduced (§3.14) |
| Synthetic corpus not reflecting real support language | External | Reported as limitation L1; scenarios authored from documented incident categories rather than invented freely |
| Single-model dependency | External | Model version and parameters recorded with all results; reported as limitation L2 |
| Findings generalised beyond orchestrated pipelines | External | System characterised precisely as an orchestrated specialist-agent pipeline, not an autonomous MAS [13]; delimitation stated in §1.12 |
| Under-powered participant sample | Statistical conclusion | A priori power analysis before collection; effect sizes with confidence intervals reported rather than *p*-values alone; under-powering reported rather than concealed |
| Multiplicity across the ablation family | Statistical conclusion | Holm–Bonferroni correction across the family; tests pre-specified rather than selected after inspecting the data |
| Divergence between documented and actual artefact | Construct | Source-level verification of every quantitative claim about the artefact before it is written (§3.10) |
| A clean adversarial result mistaken for proof of safety | Construct | The safety claim is bounded to the tested control set and attack classes; the classes are enumerated in §3.12.3 so the boundary is inspectable (§1.12, L6) |

---

## 3.17 Chapter Summary

This chapter established a pragmatist paradigm operationalised through Design Science Research, and accepted the obligation that follows from it: the artefact must be evaluated in a way capable of falsifying its design claims, which is why the evaluation is built on ablation and adversarial testing rather than on demonstration.

The approach is abductive in formulating the architecture and deductive in testing it, with four hypotheses each bound to a specific test and an explicit falsification condition — including a safety hypothesis stated so that a single counter-example refutes it. The design is a within-subject experiment across five system configurations executed on a common scenario set, with five repetitions per scenario to separate systematic effects from generative variance.

The proposed system was specified at methodological level: an orchestrated specialist-agent pipeline of five agents whose heterogeneous design follows the principle of generative where interpretation is required and deterministic where accountability is required; a retrieval pipeline whose threshold and ranking parameters are treated as tuned and reported quantities rather than unexplained constants; an eight-stage troubleshooting workflow that closes the complete support loop; and a remediation mechanism governed by seven controls, every one of which is enforced outside the language model. That last property is what makes the safety claim testable rather than asserted, and it is the direct design consequence of the analysis in Chapter 2.

Evidence collection is mixed-methods through instrumented logs, rubric scoring, adversarial execution, a usability instrument and a matched human baseline, drawing on synthetic corpora whose external-validity cost is stated rather than concealed. The evaluation methodology specifies a five-condition ablation ladder totalling 1,500 system trials, a five-class adversarial protocol targeting each governance control at its own level, nine metric dimensions, and a statistical plan with pre-specified tests, multiplicity correction and effect-size reporting. Tools were justified against rejected alternatives, Scrum was justified against sequential and continuous-flow methodologies, and the timeline identifies corpus construction as the critical path with an explicit mitigation that protects the ablation conditions at the expense of scenario count. Ethics and threats to validity were specified with concrete mitigations rather than general assurances.

Chapter 4 presents the detailed design and implementation of the artefact specified here.


<div style="page-break-after: always"></div>

# FINAL THESIS — REFERENCES, SOURCE VERIFICATION AND CONSISTENCY CHECK

**Companion to** `Final_Thesis_Chapter_1_Introduction.md`, `Final_Thesis_Chapter_2_Literature_Review.md`, `Final_Thesis_Chapter_3_Methodology.md`
**Referencing style:** IEEE, numbered in order of first appearance across Chapters 1–3
**Verification date:** 18 August 2026
**Verification method:** every entry was checked against the publisher record of the version of record — Crossref metadata, ACL Anthology, PMLR, NeurIPS/ICLR proceedings, the arXiv listing, or the publisher's article page. Nothing below is reproduced from memory or from a secondary citation.

---

## PART A — REFERENCE LIST (IEEE)

### [1] Generative AI at Work

> E. Brynjolfsson, D. Li, and L. R. Raymond, "Generative AI at work," *The Quarterly Journal of Economics*, vol. 140, no. 2, pp. 889–942, 2025, doi: 10.1093/qje/qjae044.

| Field | Detail |
|---|---|
| **Authors** | Erik Brynjolfsson (Stanford/NBER), Danielle Li (MIT/NBER), Lindsey R. Raymond (MIT) |
| **Year / venue** | 2025 · *The Quarterly Journal of Economics* (Oxford University Press) — peer-reviewed journal |
| **DOI** | 10.1093/qje/qjae044 |
| **Official page** | https://academic.oup.com/qje/article/140/2/889/7990658 (may require institutional access) |
| **Free legal PDF** | https://www.nber.org/system/files/working_papers/w31161/w31161.pdf — NBER Working Paper 31161, the authors' own earlier version, openly distributed by NBER |
| **Supports** | §1.2.1 (the empirical anchor: 5,172 agents, ~15% more issues resolved per hour, gains concentrated among less experienced workers, attributed to diffusion of tacit knowledge, from a system that *advises*), §1.2.6, §1.5, §1.14, §2.4 (the domain constraint is knowledge access, not knowledge existence), §2.10, §3.6.2 |
| **Verified** | Crossref confirms title, all three authors, vol. 140, no. 2, pp. 889–942, 2025, DOI. Abstract confirms "issues resolved per hour, by 15% on average" and 5,172 agents |

---

### [2] An IT Service Management Literature Review: Challenges, Benefits, Opportunities and Implementation Practices

> J. Serrano, J. Faustino, D. Adriano, R. Pereira, and M. M. da Silva, "An IT service management literature review: Challenges, benefits, opportunities and implementation practices," *Information*, vol. 12, no. 3, art. 111, 2021, doi: 10.3390/info12030111.

| Field | Detail |
|---|---|
| **Authors** | João Serrano, João Faustino, Daniel Adriano, Rúben Pereira, Miguel Mira da Silva |
| **Year / venue** | 2021 · *Information* (MDPI) — peer-reviewed, open access (CC BY) |
| **DOI** | 10.3390/info12030111 |
| **Official page** | https://www.mdpi.com/2078-2489/12/3/111 |
| **Free legal PDF** | https://www.mdpi.com/2078-2489/12/3/111/pdf |
| **Supports** | §1.2.2 and §2.4 (definition of the ITSM domain; systematic review of 47 studies; benefits in service quality and standardisation alongside persistent process-discipline and knowledge-asset challenges — the citation grounding the claim that the binding constraint is knowledge maintenance and access), §1.2.6, §2.9, §2.10 |
| **Verified** | Crossref confirms title, all five authors, vol. 12, no. 3, art. 111, 2021, DOI, and the 47-study scope |
| **Status** | **New in the final chapters.** See Part D, change C8 |

---

### [3] Performance Comparison of Machine Learning Algorithms in Classifying Information Technologies Incident Tickets

> D. F. Oliveira, A. S. Nogueira, and M. A. Brito, "Performance comparison of machine learning algorithms in classifying information technologies incident tickets," *AI*, vol. 3, no. 3, pp. 601–622, 2022, doi: 10.3390/ai3030035.

| Field | Detail |
|---|---|
| **Authors** | Domingos F. Oliveira, Afonso S. Nogueira, Miguel A. Brito |
| **Year / venue** | 2022 · *AI* (MDPI) — peer-reviewed, open access (CC BY) |
| **DOI** | 10.3390/ai3030035 |
| **Official page** | https://www.mdpi.com/2673-2688/3/3/35 |
| **Free legal PDF** | https://www.mdpi.com/2673-2688/3/3/35/pdf |
| **Supports** | §1.2.2 and §2.5.1 (LinearSVC 93.12%, SGDC 90.01%, LR 88.65%, MNB 85.03%; oversampling improved results; smaller un-oversampled corpora performed worse — establishing that categorisation is substantially automatable but conditional on corpus size and class-balance treatment), P3, the RQ1/H2 baseline, §2.9, §3.12.2, §3.12.4 |
| **Verified** | Crossref confirms title, authors, vol. 3, no. 3, pp. 601–622, 2022, DOI. **Full text read**: per-model accuracies, the oversampling finding and the multilingual comparison confirmed in Table 11 and §5 Conclusions |
| **Correction applied** | Interim 01 attributed a *category granularity* finding to this paper; the full text contains no such analysis. See Part D, change C3 |

---

### [4] Predicting Incident Resolution Time in IT Service Management via Lifecycle Feature Aggregation and Machine Learning

> Mulyati, D. Stiawan, A. Rahman, M. S. Shakkah, and R. Budiarto, "Predicting incident resolution time in IT service management via lifecycle feature aggregation and machine learning," *Ingénierie des Systèmes d'Information*, vol. 31, no. 2, pp. 511–519, 2026, doi: 10.18280/isi.310219.

| Field | Detail |
|---|---|
| **Authors** | Mulyati, Deris Stiawan, Abdul Rahman, Moh'D Suliman Shakkah, Rahmat Budiarto |
| **Year / venue** | 2026 · *Ingénierie des Systèmes d'Information* (IIETA) — peer-reviewed, open access |
| **DOI** | 10.18280/isi.310219 |
| **Official page** | https://www.iieta.org/journals/isi/paper/10.18280/isi.310219 |
| **Free legal PDF** | available from the IIETA article page above (CC BY) |
| **Supports** | §1.2.2 and §2.5.1 (lifecycle-aggregated features R² = 0.8318, MAE 60.67 h, versus R² = 0.5412 non-aggregated), P3, §2.6.4 (the standard against which this project's own predictive component is judged weak), §1.12 L4, §3.12.4 |
| **Verified** | IIETA article page confirms title, all five authors, vol. 31, no. 2, 2026, DOI, **and the previously missing page range 511–519**; R² figures confirmed from the article record |

---

### [5] A Survey of Large Language Models

> W. X. Zhao, K. Zhou, J. Li, T. Tang, X. Wang, Y. Hou, et al., "A survey of large language models," *Frontiers of Computer Science*, vol. 20, no. 12, art. 2012627, 2026, doi: 10.1007/s11704-026-60308-3.

| Field | Detail |
|---|---|
| **Authors** | Wayne Xin Zhao, Kun Zhou, Junyi Li, Tianyi Tang, Xiaolei Wang, Yupeng Hou, et al. (Renmin University of China) |
| **Year / venue** | 2026 · *Frontiers of Computer Science* (Springer / Higher Education Press) — **peer-reviewed journal** |
| **DOI** | 10.1007/s11704-026-60308-3 |
| **Official page** | https://link.springer.com/article/10.1007/s11704-026-60308-3 (may require institutional access) |
| **Free legal PDF** | https://arxiv.org/pdf/2303.18223 — the authors' own arXiv version (arXiv:2303.18223) |
| **Supports** | §1.2.3 (multi-step reasoning, instruction-following, emergence with scale), P1, §2.6.1 (conditional adaptation and the hallucination failure mode), §3.3 H2 |
| **Verified** | Crossref confirms the journal version of record: *Frontiers of Computer Science*, vol. 20, no. 12, 2026, DOI |
| **Upgrade applied** | Interim 01 cited the arXiv preprint. See Part D, change C5 |

---

### [6] Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

> P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, "Retrieval-augmented generation for knowledge-intensive NLP tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, 2020, pp. 9459–9474.

| Field | Detail |
|---|---|
| **Year / venue** | 2020 · NeurIPS 33 — peer-reviewed conference |
| **DOI** | none assigned by NeurIPS |
| **Official page** | https://papers.nips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html |
| **Free legal PDF** | https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf |
| **Supports** | §1.2.3 (the RAG formulation: parametric plus explicit non-parametric memory), P2, §2.6.2, §3.3 H1, §3.7.4 |
| **Verified** | NeurIPS proceedings page confirms title and the complete twelve-author list |
| **Date note** | 2020, within the 2019–2026 preference. Retained as the foundational statement of the mechanism this project implements; citing a later survey for the mechanism itself would misattribute it |

---

### [7] Retrieval-Augmented Generation for Large Language Models: A Survey

> Y. Gao, Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, Y. Dai, J. Sun, M. Wang, and H. Wang, "Retrieval-augmented generation for large language models: A survey," *arXiv preprint* arXiv:2312.10997, 2024.

| Field | Detail |
|---|---|
| **Authors** | Yunfan Gao, Yun Xiong, Xinyu Gao, Kangxiang Jia, Jinliu Pan, Yuxi Bi, Yi Dai, Jiawei Sun, Meng Wang, Haofen Wang |
| **Year / venue** | 2023 (v1) / 2024 (revised) · arXiv preprint — **no peer-reviewed version of record found**; marked as a preprint in the citation |
| **DOI** | 10.48550/arXiv.2312.10997 |
| **Official page** | https://arxiv.org/abs/2312.10997 |
| **Free legal PDF** | https://arxiv.org/pdf/2312.10997 |
| **Supports** | §1.2.3 (RAG as a matured design space of naïve/advanced/modular paradigms, motivated by hallucination, knowledge staleness and untraceable reasoning), §2.6.1, §2.6.2, §3.3 H1 |
| **Verified** | arXiv listing confirms title, the complete ten-author list, and the "Ongoing Work" comment indicating no venue version |

---

### [8] Dense Passage Retrieval for Open-Domain Question Answering

> V. Karpukhin, B. Oğuz, S. Min, P. Lewis, L. Wu, S. Edunov, D. Chen, and W. Yih, "Dense passage retrieval for open-domain question answering," in *Proc. 2020 Conf. Empirical Methods in Natural Language Processing (EMNLP)*, 2020, pp. 6769–6781, doi: 10.18653/v1/2020.emnlp-main.550.

| Field | Detail |
|---|---|
| **Year / venue** | 2020 · EMNLP 2020 — peer-reviewed conference |
| **DOI** | 10.18653/v1/2020.emnlp-main.550 |
| **Official page** | https://aclanthology.org/2020.emnlp-main.550/ |
| **Free legal PDF** | https://aclanthology.org/2020.emnlp-main.550.pdf |
| **Supports** | §1.2.3 and §2.6.2 (dual-encoder dense retrieval outperforms sparse lexical baselines on top-k accuracy — the technical basis for semantic rather than keyword retrieval), §3.7.4, §3.11 |
| **Verified** | ACL Anthology confirms title, all eight authors, pp. 6769–6781, DOI |

---

### [9] Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks

> N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using siamese BERT-networks," in *Proc. 2019 Conf. Empirical Methods in Natural Language Processing and 9th Int. Joint Conf. Natural Language Processing (EMNLP-IJCNLP)*, Hong Kong, China, 2019, pp. 3982–3992, doi: 10.18653/v1/D19-1410.

| Field | Detail |
|---|---|
| **Year / venue** | 2019 · EMNLP-IJCNLP 2019 — peer-reviewed conference |
| **DOI** | 10.18653/v1/D19-1410 |
| **Official page** | https://aclanthology.org/D19-1410/ |
| **Free legal PDF** | https://aclanthology.org/D19-1410.pdf |
| **Supports** | §1.2.3 and §2.6.2 (independent encoding plus cosine comparison makes large-scale semantic similarity tractable — precisely the retrieval mechanism this project implements), §3.7.4, §3.11 |
| **Verified** | ACL Anthology confirms title, both authors, location, pp. 3982–3992, DOI |

---

### [10] Retrieval Augmented Generation-Based Incident Resolution Recommendation System for IT Support

> P. Toro Isaza, M. Nidd, N. Zheutlin, J.-W. Ahn, C. A. Bhatt, Y. Deng, R. Mahindru, M. Franz, H. Florian, and S. Roukos, "Retrieval augmented generation-based incident resolution recommendation system for IT support," *arXiv preprint* arXiv:2409.13707, 2024.

| Field | Detail |
|---|---|
| **Authors** | Paulina Toro Isaza, Michael Nidd, Noah Zheutlin, Jae-wook Ahn, Chidansh Amitkumar Bhatt, Yu Deng, Ruchi Mahindru, Martin Franz, Hans Florian, Salim Roukos (IBM Research) |
| **Year / venue** | 2024 · arXiv preprint — **no peer-reviewed venue version found** (re-checked August 2026); marked as a preprint in the citation |
| **DOI** | 10.48550/arXiv.2409.13707 |
| **Official page** | https://arxiv.org/abs/2409.13707 |
| **Free legal PDF** | https://arxiv.org/pdf/2409.13707 |
| **Supports** | §1.2.3, P2, §2.5.3 (domain-specific RAG for IT support built around enterprise domain-coverage and model-size constraints), **G2** (evaluated on retrieval and answer quality rather than end-to-end resolution), §2.9, §3.3 H1 |
| **Verified** | arXiv listing confirms title, the complete ten-author list, 2024, and — from the abstract — the domain-coverage and model-size constraints attributed to it in §2.5.3 |

---

### [11] Retrieval-Augmented Generation with Knowledge Graphs for Customer Service Question Answering

> Z. Xu, M. J. Cruz, M. Guevara, T. Wang, M. Deshpande, X. Wang, and Z. Li, "Retrieval-augmented generation with knowledge graphs for customer service question answering," in *Proc. 47th Int. ACM SIGIR Conf. Research and Development in Information Retrieval (SIGIR '24)*, Washington, DC, USA, 2024, pp. 2905–2909, doi: 10.1145/3626772.3661370.

| Field | Detail |
|---|---|
| **Authors** | Zhentao Xu, Mark Jerome Cruz, Matthew Guevara, Tie Wang, Manasi Deshpande, Xiaofeng Wang, Zheng Li (LinkedIn) |
| **Year / venue** | 2024 · SIGIR '24 (ACM) — peer-reviewed conference |
| **DOI** | 10.1145/3626772.3661370 |
| **Official page** | https://dl.acm.org/doi/10.1145/3626772.3661370 (may require institutional access) |
| **Free legal PDF** | https://arxiv.org/pdf/2404.17723 — the authors' own arXiv copy |
| **Supports** | §1.2.3, P2, §2.5.3 (flat-text retrieval over a ticket corpus discards intra-issue structure and inter-issue relations; knowledge-graph retrieval improves both retrieval and answer quality — a direct, well-founded critique of the retrieval design this project implements), **G2**, §1.12 L3, §3.7.4 |
| **Verified** | Crossref confirms title, all seven authors, SIGIR '24, DOI, **and the previously missing page range 2905–2909** |

---

### [12] ReAct: Synergizing Reasoning and Acting in Language Models

> S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, "ReAct: Synergizing reasoning and acting in language models," in *Proc. Int. Conf. Learning Representations (ICLR)*, 2023.

| Field | Detail |
|---|---|
| **Authors** | Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao |
| **Year / venue** | 2023 · ICLR 2023 — peer-reviewed conference |
| **DOI** | none (OpenReview); arXiv:2210.03629 |
| **Official page** | https://openreview.net/forum?id=WE_vluYUL-X |
| **Free legal PDF** | https://arxiv.org/pdf/2210.03629 |
| **Supports** | §1.2.3 (interleaved reasoning and acting with observation feedback — the paradigm of which this project's pipeline is a constrained, deterministic instance), P1, §2.7.1, §3.7.5 |
| **Verified** | arXiv listing confirms title, all seven authors, and the v3 comment identifying the ICLR 2023 camera-ready version |

---

### [13] A Survey on Large Language Model Based Autonomous Agents

> L. Wang, C. Ma, X. Feng, Z. Zhang, H. Yang, J. Zhang, Z.-Y. Chen, J. Tang, X. Chen, Y. Lin, W. X. Zhao, Z. Wei, and J.-R. Wen, "A survey on large language model based autonomous agents," *Frontiers of Computer Science*, vol. 18, no. 6, art. 186345, 2024, doi: 10.1007/s11704-024-40231-1.

| Field | Detail |
|---|---|
| **Year / venue** | 2024 · *Frontiers of Computer Science* (Springer / Higher Education Press) — peer-reviewed journal |
| **DOI** | 10.1007/s11704-024-40231-1 |
| **Official page** | https://link.springer.com/article/10.1007/s11704-024-40231-1 (may require institutional access) |
| **Free legal PDF** | https://arxiv.org/pdf/2308.11432 — the authors' own arXiv copy |
| **Supports** | §1.2.3 (profiling / memory / planning / action construction pattern), §2.7.1, §3.3 H3, §3.7.1 (the basis on which this system is characterised as an *orchestrated pipeline* rather than an autonomous MAS), §1.12 delimitation, §3.16 |
| **Verified** | Crossref confirms title, the complete thirteen-author list, vol. 18, no. 6, art. 186345, 2024, DOI |

---

### [14] Large Language Model-Based Agents for Software Engineering: A Survey

> J. Liu, K. Wang, Y. Chen, X. Peng, Z. Chen, L. Zhang, and Y. Lou, "Large language model-based agents for software engineering: A survey," *ACM Transactions on Software Engineering and Methodology*, 2025, doi: 10.1145/3796507.

| Field | Detail |
|---|---|
| **Authors** | Junwei Liu, Kaixin Wang, Yixuan Chen, Xin Peng, Zhenpeng Chen, Lingming Zhang, Yiling Lou (Fudan University et al.) |
| **Year / venue** | *ACM Transactions on Software Engineering and Methodology* (TOSEM) — **peer-reviewed journal** |
| **DOI** | 10.1145/3796507 |
| **Official page** | https://dl.acm.org/doi/10.1145/3796507 (may require institutional access) |
| **Free legal PDF** | https://arxiv.org/pdf/2409.02977 — the authors' own arXiv copy |
| **Supports** | §1.2.3 and §2.7.1 (survey of 124 studies on LLM agents in software engineering; breadth of adoption alongside unresolved reliability, evaluation and cost challenges), §3.3 H3 |
| **Verified** | ACM Digital Library confirms the TOSEM publication and DOI; the arXiv listing carries the "Accepted by TOSEM" note and confirms the seven-author list and the 124-paper scope |
| **Upgrade applied** | Interim 01 cited the arXiv preprint. See Part D, change C5 |

---

### [15] ITBench: Evaluating AI Agents across Diverse Real-World IT Automation Tasks

> S. Jha, R. R. Arora, Y. Watanabe, T. Yanagawa, Y. Chen, J. Clark, et al., "ITBench: Evaluating AI agents across diverse real-world IT automation tasks," in *Proc. 42nd Int. Conf. Machine Learning (ICML)*, PMLR, vol. 267, 2025, pp. 27134–27197.

| Field | Detail |
|---|---|
| **Authors** | Saurabh Jha, Rohan R. Arora, Yuji Watanabe, Takumi Yanagawa, Yinfang Chen, Jackson Clark, and further co-authors (IBM Research / UIUC) |
| **Year / venue** | 2025 · ICML 2025, PMLR vol. 267 — peer-reviewed conference |
| **DOI** | none (PMLR); arXiv:2502.05352 |
| **Official page** | https://proceedings.mlr.press/v267/jha25a.html |
| **Free legal PDF** | https://proceedings.mlr.press/v267/jha25a/jha25a.pdf |
| **Supports** | §1.2.4 (**11.4% SRE / 25.2% CISO / 25.8% FinOps resolution rates over 102 real-world scenarios** — the strongest single piece of evidence that the composed problem is unsolved), §1.3.1, §1.5, §1.11, §1.14, §2.9, §2.10, §3.3, §3.6.2 |
| **Verified** | PMLR proceedings page confirms title, volume 267, 2025, pp. 27134–27197, and the three resolution-rate figures together with the 0.35 anomaly-detection F1 |
| **Note for final submission** | IEEE permits `et al.` after six authors; the complete author list (35+) is available from the PMLR page should your examiner prefer it in full |

---

### [16] Recommending Root-Cause and Mitigation Steps for Cloud Incidents using Large Language Models

> T. Ahmed, S. Ghosh, C. Bansal, T. Zimmermann, X. Zhang, and S. Rajmohan, "Recommending root-cause and mitigation steps for cloud incidents using large language models," in *Proc. IEEE/ACM 45th Int. Conf. Software Engineering (ICSE)*, Melbourne, Australia, 2023, pp. 1737–1749, doi: 10.1109/ICSE48619.2023.00149.

| Field | Detail |
|---|---|
| **Authors** | Toufique Ahmed, Supriyo Ghosh, Chetan Bansal, Thomas Zimmermann, Xuchao Zhang, Saravan Rajmohan (UC Davis / Microsoft) |
| **Year / venue** | 2023 · ICSE 2023 (IEEE/ACM) — peer-reviewed conference |
| **DOI** | 10.1109/ICSE48619.2023.00149 |
| **Official page** | https://doi.org/10.1109/ICSE48619.2023.00149 (IEEE Xplore; may require institutional access) · ACM mirror: https://dl.acm.org/doi/10.1109/ICSE48619.2023.00149 |
| **Free legal PDF** | https://arxiv.org/pdf/2301.03797 — the authors' own preprint |
| **Supports** | §1.2.4 and §2.5.2 (industrial-scale evaluation of LLMs for root-cause and mitigation recommendation: meaningful assistance, sub-autonomous reliability), §2.9 |
| **Verified** | Crossref confirms title, all six authors, ICSE 2023, pp. 1737–1749, DOI |

---

### [17] Automatic Root Cause Analysis via Large Language Models for Cloud Incidents

> Y. Chen, H. Xie, M. Ma, Y. Kang, X. Gao, L. Shi, Y. Cao, X. Gao, H. Fan, M. Wen, J. Zeng, S. Ghosh, X. Zhang, C. Zhang, Q. Lin, S. Rajmohan, D. Zhang, and T. Xu, "Automatic root cause analysis via large language models for cloud incidents," in *Proc. 19th European Conf. Computer Systems (EuroSys '24)*, Athens, Greece, 2024, pp. 674–688, doi: 10.1145/3627703.3629553.

| Field | Detail |
|---|---|
| **Year / venue** | 2024 · EuroSys '24 (ACM) — peer-reviewed conference |
| **DOI** | 10.1145/3627703.3629553 |
| **Official page** | https://dl.acm.org/doi/10.1145/3627703.3629553 |
| **Free legal PDF** | https://arxiv.org/pdf/2305.15778 — the authors' own arXiv copy |
| **Supports** | §1.2.4 (**root-cause categorisation accuracy up to 0.766 over a year of real Microsoft incidents** — the "valuable assistant, unacceptable autonomous actor" argument), §1.5, §1.14, §2.5.2 (context assembly before generation — the architectural lesson this project adopts), §2.9, §2.10 |
| **Verified** | Crossref confirms title, the complete eighteen-author list, EuroSys '24, DOI, **and the previously missing page range 674–688**. The 0.766 figure and the diagnostic-aggregation design were confirmed from the paper's abstract |

---

### [18] VIGIL: Towards Edge-Extended Agentic AI for Enterprise IT Support

> S. Ahuja, N. Kordjazi, E. Yortucboylu, V. Kapoor, M. Dundua, Y. Li, D. Ho, V. Padala, J. Whitted, and R. Steinert, "VIGIL: Towards edge-extended agentic AI for enterprise IT support," *arXiv preprint* arXiv:2603.16110, 2026.

| Field | Detail |
|---|---|
| **Authors** | Sarthak Ahuja, Neda Kordjazi, Evren Yortucboylu, Vishaal Kapoor, Mariam Dundua, Yiming Li, Derek Ho, Vaibhavi Padala, Jennifer Whitted, Rebecca Steinert (Amazon, AI Center of Excellence) |
| **Year / venue** | 2026 (submitted 17 March 2026) · arXiv preprint — **not peer-reviewed**; marked as a preprint in the citation and its status stated explicitly in §2.2 and §2.5.4 |
| **DOI** | none (arXiv:2603.16110) |
| **Official page** | https://arxiv.org/abs/2603.16110 |
| **Free legal PDF** | https://arxiv.org/pdf/2603.16110 |
| **Supports** | §1.1 and §1.3.3 (the basis on which no categorical-novelty claim is made), §1.2.4 (10-week pilot, 100 endpoints, 39% fewer interaction rounds, ≥4× faster diagnosis, 82% self-service resolution, four validated instruments, and the finding that users rated the system higher when no KB match existed), §1.11, §1.14, §2.5.4 (the closest published system), §2.8, §2.9, §2.10, §3.7.6 |
| **Verified** | arXiv listing and the paper's own title page confirm title, all ten authors, the Amazon affiliation, the March 2026 submission date, and every figure attributed to it in the chapters |
| **Note** | This is the most argumentatively load-bearing reference in the gap analysis and it is a preprint. That status is disclosed where it carries weight. Check before final submission whether a peer-reviewed version has appeared |

---

### [19] A Survey of AIOps in the Era of Large Language Models

> L. Zhang, T. Jia, M. Jia, Y. Wu, A. Liu, Y. Yang, Z. Wu, X. Hu, P. S. Yu, and Y. Li, "A survey of AIOps in the era of large language models," *ACM Computing Surveys*, 2025, doi: 10.1145/3746635.

| Field | Detail |
|---|---|
| **Authors** | Lingzhe Zhang, Tong Jia, Mengxi Jia, Yifan Wu, Aiwei Liu, Yong Yang, Zhonghai Wu, Xuming Hu, Philip S. Yu, Ying Li (Peking University et al.) |
| **Year / venue** | 2025 · *ACM Computing Surveys* — **peer-reviewed journal** |
| **DOI** | 10.1145/3746635 |
| **Official page** | https://dl.acm.org/doi/10.1145/3746635 (may require institutional access) |
| **Free legal PDF** | https://arxiv.org/pdf/2507.12472 — the authors' own arXiv copy |
| **Supports** | §1.2.4 (183 articles, January 2020 – December 2024; rapid expansion alongside fragmented architectures and inconsistent evaluation), P5, §1.11, §1.14, §2.9, §2.10 |
| **Verified** | Crossref confirms title, the complete ten-author list, ACM Computing Surveys, 2025, DOI, and the 183-article / Jan 2020 – Dec 2024 scope |
| **Upgrade applied** | Interim 01 cited arXiv:2406.11213, a preprint by the same group. See Part D, change C5 |

---

### [20] Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection

> K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz, "Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection," in *Proc. 16th ACM Workshop on Artificial Intelligence and Security (AISec '23)*, Copenhagen, Denmark, 2023, pp. 79–90, doi: 10.1145/3605764.3623985.

| Field | Detail |
|---|---|
| **Authors** | Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, Mario Fritz (Saarland University / CISPA / sequire technology) |
| **Year / venue** | 2023 · AISec '23 at ACM CCS — peer-reviewed workshop |
| **DOI** | 10.1145/3605764.3623985 |
| **Official page** | https://dl.acm.org/doi/10.1145/3605764.3623985 (may require institutional access) |
| **Free legal PDF** | https://arxiv.org/pdf/2302.12173 — the authors' own arXiv copy |
| **Supports** | §1.2.5, P4, **G3**, §2.7.2 (indirect injection via *retrieved content* — the attack surface this architecture possesses by construction), §2.8, §3.9, §3.12.3 (the indirect-injection test class derives directly from this paper) |
| **Verified** | Crossref confirms title, all six authors, AISec '23, pp. 79–90, DOI |
| **Correction applied** | The DOI was missing from the Interim 01 entry and has been added |

---

### [21] Prompt Injection Attack against LLM-Integrated Applications

> Y. Liu, G. Deng, Y. Li, K. Wang, Z. Wang, X. Wang, T. Zhang, Y. Liu, H. Wang, Y. Zheng, L. Y. Zhang, and Y. Liu, "Prompt injection attack against LLM-integrated applications," *arXiv preprint* arXiv:2306.05499, 2023.

| Field | Detail |
|---|---|
| **Authors** | Yi Liu, Gelei Deng, Yuekang Li, Kailong Wang, Zihao Wang, Xiaofeng Wang, Tianwei Zhang, Yepang Liu, Haoyu Wang, Yan Zheng, Leo Yu Zhang, Yang Liu |
| **Year / venue** | 2023 · arXiv preprint — **no peer-reviewed venue version found**; marked as a preprint in the citation |
| **DOI** | 10.48550/arXiv.2306.05499 |
| **Official page** | https://arxiv.org/abs/2306.05499 |
| **Free legal PDF** | https://arxiv.org/pdf/2306.05499 |
| **Supports** | §1.2.5 and §2.7.2 (the HouYi black-box technique applied to **36 deployed LLM-integrated applications, 31 found vulnerable**, ten vendors confirming — the empirical-breadth claim, which no peer-reviewed source in this set supplies), §3.3 H4 |
| **Verified** | arXiv listing confirms title, the complete twelve-author list (Interim 01's list omitted Leo Yu Zhang; corrected here), and the 36/31 figures |
| **Retention justification** | The weakest source in the set by venue standing, retained deliberately: [20] establishes the indirect vector and [22] evaluates in a synthetic environment, but neither supplies deployed-application prevalence evidence. Its preprint status is disclosed |

---

### [22] AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents

> E. Debenedetti, J. Zhang, M. Balunović, L. Beurer-Kellner, M. Fischer, and F. Tramèr, "AgentDojo: A dynamic environment to evaluate prompt injection attacks and defenses for LLM agents," in *Advances in Neural Information Processing Systems (NeurIPS) Datasets and Benchmarks Track*, vol. 37, 2024.

| Field | Detail |
|---|---|
| **Authors** | Edoardo Debenedetti, Jie Zhang, Mislav Balunović, Luca Beurer-Kellner, Marc Fischer, Florian Tramèr (ETH Zurich / Invariant Labs) |
| **Year / venue** | 2024 · NeurIPS 37, Datasets and Benchmarks Track — peer-reviewed |
| **DOI** | none assigned |
| **Official page** | https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html |
| **Free legal PDF** | https://arxiv.org/pdf/2406.13352 — the authors' own arXiv copy |
| **Supports** | §1.2.5 and §2.7.2 (**97 realistic tasks, 629 security test cases**; existing defences close some security properties but not all; models fail many tasks even without an adversary; LLMs lack a formal mechanism separating instructions from data), P4, §3.3 H4, §3.7.6, §3.12.3 |
| **Verified** | NeurIPS 2024 proceedings page confirms title, all six authors and the Datasets and Benchmarks Track; the arXiv listing confirms the 97/629 figures |
| **Correction applied** | Interim 01 gave no direct proceedings URL for this entry; the verified link is supplied above |

---

### [23] Identifying the Risks of LM Agents with an LM-Emulated Sandbox

> Y. Ruan, H. Dong, A. Wang, S. Pitis, Y. Zhou, J. Ba, Y. Dubois, C. J. Maddison, and T. Hashimoto, "Identifying the risks of LM agents with an LM-emulated sandbox," in *Proc. Int. Conf. Learning Representations (ICLR)*, 2024.

| Field | Detail |
|---|---|
| **Authors** | Yangjun Ruan, Honghua Dong, Andrew Wang, Silviu Pitis, Yongchao Zhou, Jimmy Ba, Yann Dubois, Chris J. Maddison, Tatsunori Hashimoto (Toronto / Vector Institute / Stanford) |
| **Year / venue** | 2024 · ICLR 2024 (Spotlight) — peer-reviewed conference |
| **DOI** | none (OpenReview); arXiv:2309.15817 |
| **Official page** | https://openreview.net/forum?id=GEcwtMk1uA · proceedings: https://proceedings.iclr.cc/paper_files/paper/2024/hash/7274ed909a312d4d869cc328ad1c5f04-Abstract-Conference.html |
| **Free legal PDF** | https://arxiv.org/pdf/2309.15817 |
| **Supports** | §1.2.5 and §2.7.2 (manual identification of agent risks does not scale; **36 high-stakes toolkits, 144 test cases, 68.8% of surfaced failures judged valid real-world failures, safest agent still failing 23.9% of the time**), §3.3, §3.12.3 |
| **Verified** | ICLR 2024 proceedings and OpenReview confirm title, all nine authors and the Spotlight designation; arXiv confirms the 68.8%, 36-toolkit, 144-case and 23.9% figures |

---

### [24] Multimodal Large Language Model-Based Fault Detection and Diagnosis in Context of Industry 4.0

> K. M. Alsaif, A. A. Albeshri, M. A. Khemakhem, and F. E. Eassa, "Multimodal large language model-based fault detection and diagnosis in context of Industry 4.0," *Electronics*, vol. 13, no. 24, art. 4912, 2024, doi: 10.3390/electronics13244912.

| Field | Detail |
|---|---|
| **Authors** | Khalid M. Alsaif, Aiiad A. Albeshri, Maher A. Khemakhem, Fathy E. Eassa (King Abdulaziz University) |
| **Year / venue** | 2024 · *Electronics* (MDPI) — peer-reviewed, open access (CC BY) |
| **DOI** | 10.3390/electronics13244912 |
| **Official page** | https://www.mdpi.com/2079-9292/13/24/4912 |
| **Free legal PDF** | https://www.mdpi.com/2079-9292/13/24/4912/pdf |
| **Supports** | §1.10 (justification for retaining image input in scope), §2.7.3 (multimodal fault interpretation, and the design implication that image-derived text must rejoin the same classification path), §3.7.2, §3.7.5 |
| **Verified** | Crossref confirms title, all four authors, vol. 13, no. 24, art. 4912, 2024, DOI, and the framework description (online/offline processing with fine-tuned multimodal models and synthetic augmentation) |

---

### [25] RAGAs: Automated Evaluation of Retrieval Augmented Generation

> S. Es, J. James, L. Espinosa Anke, and S. Schockaert, "RAGAs: Automated evaluation of retrieval augmented generation," in *Proc. 18th Conf. European Chapter of the Association for Computational Linguistics: System Demonstrations (EACL)*, 2024, pp. 150–158, doi: 10.18653/v1/2024.eacl-demo.16.

| Field | Detail |
|---|---|
| **Authors** | Shahul Es, Jithin James, Luis Espinosa Anke, Steven Schockaert (Exploding Gradients / Cardiff University / AMPLYFI) |
| **Year / venue** | 2024 · EACL 2024 System Demonstrations — peer-reviewed |
| **DOI** | 10.18653/v1/2024.eacl-demo.16 |
| **Official page** | https://aclanthology.org/2024.eacl-demo.16/ |
| **Free legal PDF** | https://aclanthology.org/2024.eacl-demo.16.pdf |
| **Supports** | §1.11, §2.6.3 (the retrieval / faithfulness / generation decomposition, adopted conceptually, together with the critical assessment that reference-free LLM-scored metrics risk circularity), §3.12.1 (why ground truth is human-authored instead), §3.12.4 (automated RAG metrics as a secondary signal only), §3.16 |
| **Verified** | ACL Anthology confirms title, all four authors, pp. 150–158, DOI, and the reference-free framing |
| **Note** | The Anthology renders the title as "RAGAs"; this capitalisation is used in preference to the "RAGAS" form used in Interim 01 |

---

### [26] Design Science in Information Systems Research

> A. R. Hevner, S. T. March, J. Park, and S. Ram, "Design science in information systems research," *MIS Quarterly*, vol. 28, no. 1, pp. 75–106, 2004, doi: 10.2307/25148625.

| Field | Detail |
|---|---|
| **Authors** | Alan R. Hevner, Salvatore T. March, Jinsoo Park, Sudha Ram |
| **Year / venue** | 2004 · *MIS Quarterly* — peer-reviewed journal |
| **DOI** | 10.2307/25148625 |
| **Official page** | https://misq.umn.edu/misq/article/28/1/75/261/Design-Science-in-Information-Systems-Research1 (may require institutional access) |
| **Open repository record** | https://aisel.aisnet.org/misq/vol28/iss1/6/ (AIS eLibrary) |
| **Supports** | §2.2 (foundational exception), §3.2 (DSR as the operationalisation of the pragmatist paradigm: the artefact as the primary vehicle of inquiry, and the obligation that evaluation be capable of falsifying design claims) |
| **Verified** | Crossref confirms title, all four authors, vol. 28, no. 1, 2004, DOI, and page range **75–106** |
| **Correction applied** | Interim 01 gave pp. 75–105; the publisher of record gives 75–106 |
| **Pre-2019 justification** | Cited as methodological canon. No post-2019 substitute of equivalent standing exists for the canonical statement of DSR |

---

### [27] A Design Science Research Methodology for Information Systems Research

> K. Peffers, T. Tuunanen, M. A. Rothenberger, and S. Chatterjee, "A design science research methodology for information systems research," *Journal of Management Information Systems*, vol. 24, no. 3, pp. 45–77, 2007, doi: 10.2753/MIS0742-1222240302.

| Field | Detail |
|---|---|
| **Authors** | Ken Peffers, Tuure Tuunanen, Marcus A. Rothenberger, Samir Chatterjee |
| **Year / venue** | 2007 · *Journal of Management Information Systems* — peer-reviewed journal |
| **DOI** | 10.2753/MIS0742-1222240302 |
| **Official page** | https://www.tandfonline.com/doi/abs/10.2753/MIS0742-1222240302 (may require institutional access) · ACM mirror: https://dl.acm.org/doi/10.2753/MIS0742-1222240302 |
| **Supports** | §2.2 (foundational exception), §3.2 and §3.6 (the six-activity DSR process model — problem identification, objective definition, design and development, demonstration, evaluation, communication — which is the literal spine of the §3.6 execution-workflow table) |
| **Verified** | Crossref confirms title, all four authors, vol. 24, no. 3, pp. 45–77, 2007, DOI |
| **Pre-2019 justification** | As [26] |

---

## PART B — SOURCE-QUALITY CHECK

### B.1 Composition of the reference base

| Category | Count | References |
|---|---|---|
| Peer-reviewed conference / workshop | 12 | [6], [8], [9], [11], [12], [15], [16], [17], [20], [22], [23], [25] |
| Peer-reviewed journal, 2019–2026 | 9 | [1], [2], [3], [4], [5], [13], [14], [19], [24] |
| Peer-reviewed journal, foundational (pre-2019) | 2 | [26], [27] |
| Preprint, marked as such in the citation | 4 | [7], [10], [18], [21] |
| **Total** | **27** | |

| Quality indicator | Result |
|---|---|
| Peer-reviewed sources | **23 of 27** (85%) |
| Published 2019–2026 | **25 of 27** (93%) — the exceptions are [26] (2004) and [27] (2007), both foundational methodology |
| Sources with a verified DOI | 22 of 27 (the five without are proceedings that assign none: [6], [12], [15], [22], [23]) |
| Sources with a free, legal full-text PDF or open repository record | **27 of 27** |
| Fabricated or unverifiable entries | **0** |
| Duplicate entries | **0** |
| Uncited entries in the reference list | **0** — verified programmatically |
| In-text citations missing from the reference list | **0** — verified programmatically |
| Numbering | Strict IEEE order of first appearance, 1→27, no gaps — verified programmatically across the three chapters |

Publisher spread: ACM 5, ACL Anthology 3, MDPI 3, Springer 2, NeurIPS 2, ICLR/OpenReview 1, IEEE 1, Oxford University Press 1, Taylor & Francis 1, PMLR 1, IIETA 1, arXiv-only 4, plus one AIS eLibrary record.

### B.2 Claim-support audit

Every reference was checked against the *specific* claim it is cited for, not merely for topical relevance. Four claims required action:

| # | Claim as stated in Interim 01 | Finding on verification | Action taken |
|---|---|---|---|
| 1 | "~14% productivity increase … more than five thousand agents" [Brynjolfsson] | The QJE version of record reports **15% on average** across **5,172** agents. The 14% figure belongs to the earlier NBER working paper, which is not the version cited | Figure corrected to 15%, agent count made exact, throughout Chapters 1–3 |
| 2 | Oliveira et al. document "sensitivity of accuracy to **category granularity** and to class imbalance" | Full-text reading found **no analysis of category granularity**. The paper does address class support/imbalance, and its results show sensitivity to **corpus size and oversampling** | Claim replaced with the verified findings (per-model accuracies; the oversampling effect; degradation on smaller un-oversampled corpora) |
| 3 | Mulyati et al. "improves materially" with lifecycle aggregation | Verified, and strengthened with the actual figures: **R² 0.8318 (MAE 60.67 h) vs 0.5412** | Figures added |
| 4 | Liu et al. found injection vulnerabilities "across a large proportion" of applications tested | Verified, and made exact: **36 applications tested, 31 vulnerable**, ten vendors confirmed | Figures added |

All other cited figures — 11.4% / 25.2% / 25.8% and 102 scenarios [15]; 0.766 [17]; 39% / ≥4× / 82% / 100 endpoints / 10 weeks [18]; 97 tasks and 629 test cases [22]; 68.8% / 36 toolkits / 144 cases / 23.9% [23]; 183 articles [19]; 124 papers [14]; 47 studies [2] — were confirmed against the source and are reproduced unchanged.

### B.3 References removed or deliberately not included

- **No source was removed from Interim 01 Revision 3's list.** All 26 were verified as real and appropriately cited; one ([2] Serrano et al.) was added.
- Grey literature — vendor market sizing, analyst downtime-cost estimates, industry survey statistics — remains excluded from the evidential core, and §2.2 states that exclusion and its justification explicitly.
- A peer-reviewed source quantifying the share of tickets attributable to password or VPN categories was searched for and **not found**; only vendor and analyst figures are available. The corresponding statement in §1.2.2 and §2.4 is therefore made qualitatively and without a number, rather than being propped up by an unverifiable industry figure.

### B.4 Reference-numbering crosswalk (Interim 01 Rev 3 → final chapters)

| Interim 01 | Final | Source | Interim 01 | Final | Source |
|---|---|---|---|---|---|
| [1] | **[18]** | VIGIL | [14] | [14] | Liu — SE agents |
| [2] | **[1]** | Brynjolfsson | [15] | [15] | ITBench |
| — | **[2]** | Serrano (new) | [16] | [16] | Ahmed |
| [3] | [3] | Oliveira | [17] | [17] | RCACopilot |
| [4] | [4] | Mulyati | [18] | **[19]** | AIOps survey |
| [5] | [5] | Zhao — LLM survey | [19] | **[20]** | Greshake |
| [6] | [6] | Lewis — RAG | [20] | **[21]** | Liu — HouYi |
| [7] | [7] | Gao — RAG survey | [21] | **[22]** | AgentDojo |
| [8] | [8] | Karpukhin — DPR | [22] | **[23]** | ToolEmu |
| [9] | [9] | Reimers — SBERT | [23] | **[24]** | Alsaif |
| [10] | [10] | Toro Isaza | [24] | **[26]** | Hevner |
| [11] | [11] | Xu — KG-RAG | [25] | **[27]** | Peffers |
| [12] | [12] | Yao — ReAct | [26] | **[25]** | RAGAs |
| [13] | [13] | Wang — agents survey | | | |

Fifteen of twenty-six numbers are unchanged. Renumbering was required because IEEE numbers by order of first citation, and the final Chapter 1 no longer opens with the revision note in which VIGIL was first cited in Interim 01.

---

## PART C — CONSISTENCY VERIFICATION AGAINST INTERIM 01

| Item | Interim Submission 01 (Rev 3) | Final Chapters 1–3 | Status |
|---|---|---|---|
| **Research title** | Context-Aware Intelligent IT Support: A Multi-Agent LLM Framework with Knowledge-Grounded Troubleshooting and Human-Gated Automated Remediation | Identical | ✅ **Unchanged** |
| **Research problem** | Support cannot scale linearly with demand; automation is either safe-but-shallow, terminating at a recommendation, or acts without adequate governance; the deficiency is architectural, evidenced by the 11.4% SRE resolution rate | Identical, §1.3.1, on the same evidential basis | ✅ **Unchanged** |
| **Specific problems** | P1 shallow conversation · P2 ungrounded generation · P3 static ticket lifecycle · P4 the action gap · P5 absence of architectural evidence | P1–P5 identical, §1.3.2 | ✅ **Unchanged** |
| **Research gap** | Not the absence of an integrated system, but the absence of an openly specified, architecturally transparent, component-wise evaluated reference design for agent-decomposed IT support with model-independent human-gated remediation (G1, G2, G3) | Identical gap statement and identical G1–G3, §1.3.3, confirmed in §2.10 | ✅ **Unchanged** |
| **Research aim** | Design, implement and empirically evaluate an agent-decomposed, retrieval-grounded IT support framework with risk-tiered human-gated remediation, and determine through systematic ablation and adversarial testing the contribution of each architectural component to diagnostic accuracy, resolution effectiveness and operational safety | Identical, §1.6 | ✅ **Unchanged** |
| **Primary research question** | To what extent does decomposing an LLM-based IT support system into specialised, independently governed agents — combined with retrieval-grounded troubleshooting and risk-tiered, human-gated remediation — improve diagnostic accuracy, resolution effectiveness and operational safety relative to monolithic LLM baselines? | Identical, §1.4 | ✅ **Unchanged** |
| **Sub-questions** | RQ1 classification · RQ2 grounding · RQ3 lifecycle decomposition · RQ4 adversarial safety · RQ5 component contribution | RQ1–RQ5 identical, §1.4. RQ4 additionally names the usability-cost half, which G3 already required and the Interim usability dimension already measured | 🟡 **Clarified** — no change of substance |
| **Objectives** | O1 identify · O2 analyse · O3 design and develop · O4 design evaluation · O5 evaluate empirically · O6 evaluate adversarial robustness, each with a completion criterion and an interim status | O1–O6 identical in wording and completion criteria, §1.7; the interim "Status" column is replaced by an "Addressed in" column pointing to thesis sections | 🟡 **Reformatted** — see change C1 |
| **Proposed approach / solution** | *Auto-Ops-AI*: an orchestration layer invoking five specialised agents in a fixed deterministic sequence; retrieval grounding over an organisational corpus; remediation restricted to an enumerated whitelist behind a mandatory human approval gate | Identical, §1.8 and §3.7, with the same rich picture and workflow narrative | ✅ **Unchanged** |
| **Agents / roles** | Image Analysis · LLM Conversation · Ticket Intelligence · Ticket Status (deterministic) · Action Executor, plus the Assignment Service; centralised deterministic orchestration; agents do not negotiate | Identical five agents with identical responsibilities, inputs, outputs and implementation basis, §3.7.2; interaction pattern specified in §3.7.3 | ✅ **Unchanged** |
| **Architectural characterisation** | "Orchestrated specialist-agent pipeline, not a decentralised autonomous multi-agent system"; conclusions bounded accordingly | Identical characterisation and identical bounding, §3.7.1 and §1.12 | ✅ **Unchanged** |
| **RAG / knowledge grounding** | Embedding-based semantic retrieval; similarity threshold with top-*k* retention; usage-weighted ranking; threshold and usage weight to become tuned, reported parameters; in-memory and persistent vector-store paths both retained for comparison; flat-text retrieval acknowledged as inferior to structured retrieval | Identical pipeline and identical parameter treatment, §3.7.4; the lower-bound reading of the grounding result carried into §1.12 L3 and §2.5.3 | ✅ **Unchanged** |
| **Human-gated remediation** | 25 whitelisted actions (14 LOW / 8 MEDIUM / 3 HIGH) across 6 categories, 3 requiring elevation; 7 governance controls C1–C7, all enforced outside the model; stepwise single-action proposal; opt-in Agent Mode; ownership-verified approval; subprocess without shell interpretation | Identical inventory, identical control set, identical justifications, §3.7.6 | ✅ **Unchanged** |
| **Safety axiom** | Safety cannot rest on model behaviour because the model is the component under attack; class-level agent separation is *not* a privilege boundary | Identical, §1.2.5, §2.7.1, §2.7.2, §3.7.6 | ✅ **Unchanged** |
| **Novelty position** | No categorical-novelty claim; contribution narrowed to open, component-wise evaluated architecture; positioned as complementary to VIGIL | Identical, stated at §1.1 and sustained through §1.11, §2.5.4 and §2.10 | ✅ **Unchanged** |
| **Methodology — paradigm** | Pragmatism operationalised through Design Science Research, with the falsifiability obligation accepted | Identical, §3.2; positivism and interpretivism now explicitly rejected with reasons | 🟡 **Strengthened** — no change of substance |
| **Methodology — approach** | Abductive then deductive; H1–H4 with explicit falsification conditions; H4 falsified by a single counter-example | H1–H4 identical in wording, grounding, test and falsification condition, §3.3 | ✅ **Unchanged** |
| **Methodology — design** | Within-subject; IV = configuration (5 levels); dependent variables across 8 families; 5 repetitions per scenario per configuration; snapshot restoration and randomised order | Identical, §3.4 and §3.12.1 | ✅ **Unchanged** |
| **Evaluation — ablation** | A0 human baseline · A1 monolithic LLM · A2 + retrieval · A3 + agent decomposition · A4 full system | Identical, §3.12.2, with added justification for a progressive ladder rather than a full factorial | 🟡 **Strengthened** — no change of substance |
| **Evaluation — adversarial** | Five classes: direct injection, indirect injection (documents and images), parameter injection, approval bypass, privilege escalation; commitment to report any bypass | Identical five classes and identical commitment, §3.12.3, each class now mapped to the control it tests | 🟡 **Strengthened** — no change of substance |
| **Evaluation — metrics** | Nine dimensions: classification, retrieval, resolution, grounding, lifecycle, safety, predictive, usability, efficiency | Identical nine dimensions, §3.12.4 | ✅ **Unchanged** |
| **Evaluation — statistics** | 60 × 5 × 5 = 1,500 trials; 12–15 participants; RM-ANOVA / Friedman; Cochran's Q with McNemar; Holm–Bonferroni; effect sizes with CIs; a priori power analysis | Identical, §3.12.5 | ✅ **Unchanged** |
| **Data sources** | Synthetic human-authored scenario corpus (60 target, 5 categories × 3 tiers); curated KB corpus; synthetic users and tickets; ML training data; constructed adversarial set; execution logs; participant responses | Identical, §3.9, retaining the justification for synthetic data and its external-validity cost | ✅ **Unchanged** |
| **Development methodology** | Vertically integrated increments; source-level verification of all quantitative artefact claims; Git configuration management with model version recorded per run | Identical, §3.10 | ✅ **Unchanged** |
| **Project management** | Agile Scrum, justified against Waterfall/PRINCE2 and Kanban | Identical, §3.13 | ✅ **Unchanged** |
| **Timeline** | Five phases across 26 weeks; Phase 3b critical path with no slack; mitigation reduces scenario count, never ablation conditions | Identical, §3.14 | ✅ **Unchanged** |
| **Ethics** | Seven principles: non-maleficence, informed consent and transparency, data protection, participant safety, institutional approval, responsible disclosure, research integrity | Identical seven, §3.15 | ✅ **Unchanged** |
| **Validity threats** | Ten threats with mitigations | All ten retained, §3.16, plus three added (corpus composition determining the result; over-generalisation beyond orchestrated pipelines; a clean adversarial result mistaken for proof of safety) | 🟡 **Extended** — see change C7 |
| **Scope (in / out)** | Ten-row in-scope / out-of-scope table with per-row justification | Identical rows and identical justifications, §1.10 | ✅ **Unchanged** |
| **Limitations** | L1–L9 in Interim Chapter 7 | Consolidated into §1.12 as delimitations plus L1–L6 | 🟡 **Relocated and consolidated** — see change C2 |
| **Referencing style** | IEEE | IEEE, renumbered to order of first appearance; one source added; three preprints upgraded to versions of record | 🟡 **Renumbered and upgraded** — see Part B.4 and changes C5, C8 |

**Legend:** ✅ unchanged in substance · 🟡 changed in presentation or strengthened, with the research content preserved

---

## PART D — CHANGES MADE, AND WHY EACH WAS NECESSARY

Nothing in the research problem, gap, aim, objectives, questions, proposed solution, agent design, governance model, methodology or evaluation design was altered. The changes below fall into four kinds: converting progress-report framing into thesis framing, correcting two factual claims that verification showed to be unsupported, upgrading three preprints to peer-reviewed versions of record, and completing bibliographic details.

| # | Change | Type | Why it was necessary |
|---|---|---|---|
| **C1** | The "Status" columns (Complete / In progress / Not started) attached to objectives, phases and components were removed; the objectives table now carries an "Addressed in" column | Framing | These columns are the correct form for a progress submission and the wrong form for a final thesis, where an objectives table states objectives rather than reporting how far the author had reached on a particular date. **No claim of completion has been added anywhere.** Chapters 1–3 report no experimental result, and §3.12 is written as a specification of protocol with outcomes explicitly deferred to Chapters 6–7 |
| **C2** | Limitations moved from Interim Chapter 7 into §1.12, restructured as delimitations plus L1–L6 | Structure | You asked for a Limitations section in Chapter 1. Interim L1 ("no empirical evidence yet") is a *progress* statement rather than a research limitation and would be false in a completed thesis, so its substance is instead carried by the delimitation that the evaluation is controlled and scenario-based rather than longitudinal. Interim L2 and L3 (insufficient corpus, retrieval architecture below specification) were work-in-progress items with remediation plans, so they appear as design constraints in §3.7.4 and §3.12.1 rather than as thesis limitations. Interim L5–L9 map to the new L1–L6 |
| **C3** | The claim that Oliveira et al. document sensitivity to *category granularity* was removed and replaced with their verified findings | **Factual correction** | Full-text reading found no granularity analysis in the paper. Retaining the claim would attribute to a source a finding it does not contain — the kind of error an examiner who checks the source will find. The replacement (per-model accuracies, the oversampling effect, degradation on smaller un-oversampled corpora) is stronger evidence for the same argument, and is verifiable in the paper's Table 11 and Conclusions |
| **C4** | The Brynjolfsson figure was corrected from ~14% to **15%**, and "more than five thousand agents" made exact at **5,172** | **Factual correction** | The thesis cites the *Quarterly Journal of Economics* version of record, which reports 15% across 5,172 agents. The 14% figure belongs to the earlier NBER working paper. Citing one version while quoting another is a citation-accuracy defect |
| **C5** | Three preprints upgraded to peer-reviewed versions of record: LLM survey → *Frontiers of Computer Science* (2026); SE agents survey → ACM TOSEM; AIOps survey → ACM Computing Surveys (2025) | Source quality | In each case the same authors make the same argument in a peer-reviewed venue that did not exist when Interim 01 was written. Citing a preprint where a version of record exists is a defect under IEEE practice, and the upgrade raises the peer-reviewed share of the reference base from 73% to 85%. No claim changed |
| **C6** | Missing bibliographic details completed: page ranges for [4] 511–519, [11] 2905–2909, [17] 674–688; corrected page range for [26] 75–106; DOIs added for [8], [9], [20], [25]; author list corrected for [21]; verified proceedings URL supplied for [22] | Bibliographic accuracy | IEEE style requires page ranges for journal articles and conference papers, and every in-text citation must be traceable to a complete entry. These were incomplete or, for [26] and [21], inaccurate |
| **C7** | Three threats to validity added (§3.16): corpus composition determining the result; over-generalisation beyond orchestrated pipelines; a clean adversarial result mistaken for proof of safety | Strengthening | Each is a threat the Interim design already mitigates in practice — stratified corpus, precise architectural characterisation, enumerated attack classes — but did not name. Naming them makes the existing mitigations legible to an examiner |
| **C8** | One source added: Serrano et al. [2], a systematic review of the ITSM literature | Citation coverage | The ITSM domain description (§1.2.2, §2.4) carried no citation in Interim 01 despite being a factual claim about a body of practice. This is the only source added; it is peer-reviewed and open access, it sits squarely inside the existing scope, and it supports the domain description you already wrote rather than introducing a new research area |
| **C9** | Section 2.2 (Review Method and Source Selection) added | Academic completeness | Interim 01 stated the 2019–2026 preference and the foundational exception but not the selection criteria, preprint policy or exclusion policy. Examiners routinely ask how the literature was selected, and stating it also makes the deliberate exclusion of grey literature visible as a methodological decision rather than an omission |
| **C10** | Chapter 3 extended with §3.7 (methodological specification of the proposed system: architecture, agent roles, agent interaction, RAG pipeline, troubleshooting workflow, human gating, components) and §3.12 (evaluation methodology) | Structure | You asked for these in Chapter 3. Interim 01 placed them in Chapters 4 and 5. The material is **taken from those chapters unchanged in substance**; §3.7 and §3.12 present it at methodological level and defer full implementation detail to Chapter 4 and the full instrument to Chapter 5, so there is no duplication of claims and no divergence between the two accounts |
| **C11** | References renumbered to IEEE order of first appearance (crosswalk in Part B.4) | Style compliance | IEEE numbers by order of first citation. Because the final Chapter 1 does not open with a revision note, the first-appearance order changed. Fifteen of twenty-six numbers are unchanged, and the crosswalk allows cross-checking against Interim 01 and your existing sourcing guide |

### What was deliberately *not* changed

- The research problem, gap statement, G1–G3, aim, primary research question, RQ1–RQ5 and O1–O6 are reproduced with their meaning intact.
- The five-agent design, the deterministic orchestration, the 25-action whitelist with its risk distribution, the seven governance controls, the stepwise single-action protocol and the opt-in Agent Mode are unchanged.
- The A0–A4 ablation ladder, the five adversarial classes, the nine metric dimensions, the 1,500-trial target, the 12–15 participant target and the statistical plan are unchanged.
- The narrowed novelty claim and the withdrawal of the "class separation is a privilege boundary" argument are preserved as the settled position of the thesis rather than re-litigated as corrections.
- No new technology, agent, framework, dataset or research direction has been introduced.

---

## PART E — ACTIONS RECOMMENDED BEFORE FINAL SUBMISSION

| # | Action | Priority |
|---|---|---|
| 1 | Check whether a peer-reviewed version of **[18] VIGIL** has appeared. It is a preprint carrying substantial argumentative weight in §2.5.4 and §2.10 | High |
| 2 | Obtain the **QJE** version of [1] through the NSBM library and confirm the 15% figure in the published text, rather than relying on the abstract | High |
| 3 | Decide whether to transcribe the complete author list for **[15] ITBench** from the PMLR page. IEEE permits `et al.` after six authors, so this is optional | Low |
| 4 | Re-check **[7]**, **[10]** and **[21]** for peer-reviewed versions shortly before submission; all three are currently preprint-only and would be strict upgrades if published | Medium |
| 5 | Confirm your department's expected citation style is IEEE. Interim 01 used IEEE and these chapters follow it consistently | Low |
