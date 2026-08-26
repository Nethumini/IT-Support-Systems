# CHAPTER – 01 [ INTRODUCTION ]

**Research title:** Context Aware Intelligent IT Support Systems: A Multi Agent Framework with Predictive Issue Detection and Automated Resolution

**Author:** P. T. N. Pathirana (28647) — NSBM Green University Town

---

## 1.1 Chapter Overview

This chapter presents the introduction to the research titled **"Context Aware Intelligent IT Support Systems: A Multi Agent Framework with Predictive Issue Detection and Automated Resolution."** It begins by establishing the background of enterprise IT support and the conditions that have made its current difficulties acute. It then narrows to a structured problem statement that separates the general organisational implications of those difficulties from the specific shortcomings of existing technical approaches, and closes that discussion with an explicit statement of the research gap. From that gap follow the research question, the motivation for undertaking the work, the research aim, and four research objectives. A rich picture of the proposed solution, **Auto-Ops-AI**, then presents the multi-agent architecture and its principal workflow, after which the resources required, the boundaries of the investigation, and a chapter summary complete the foundation for the chapters that follow.

The chapter is organised as a single line of argument. Section 1.2 establishes what has actually happened in IT service management and identifies the binding constraint on support work. Section 1.3 converts that evidence into a general problem, six specific problems, and a bounded research gap. Sections 1.4 to 1.7 state the research question, motivation, aim and objectives that follow from that gap, and Sections 1.8 to 1.11 present the proposed solution, its resource requirements, its scope, and a summary.

---

## 1.2 Problem Background

**The IT Service Management context.** IT Service Management (ITSM) is the body of practice through which organisations deliver, support and improve IT services. It is structured around defined processes — incident management, request fulfilment, problem management and change management — and instrumented by ticketing systems and service level agreements (SLAs). A systematic literature review of 47 articles drawn from leading journals and conferences characterises ITSM adoption as delivering measurable benefits in service quality, process standardisation and customer satisfaction, while simultaneously documenting persistent implementation challenges, among them the organisational cost of maintaining process discipline and the difficulty of establishing and sustaining the knowledge assets on which the processes depend [1]. That last challenge locates the problem this research addresses: ITSM frameworks presuppose documented, current and findable resolution knowledge, and the reviewed literature records that maintaining such knowledge in practice remains a persistent difficulty rather than a solved administrative matter [1].

**The operational environment has made this harder.** Enterprise IT estates are heterogeneous by construction, comprising cloud services, on-premises infrastructure, diverse endpoint devices and layered software stacks, and the shift to remote and hybrid working has widened that heterogeneity further. Recent work on enterprise IT support characterises the resulting difficulty precisely: heterogeneous devices, evolving policies and long-tail failure modes that are difficult to resolve centrally, with failures often emerging from subtle local interactions rather than clear global faults [2]. Support is nevertheless still delivered through tiered human escalation (L1 → L2 → L3) mediated by ticketing systems. A user encountering a technical issue — a malfunctioning VPN connection, a slow laptop, a recurring Blue Screen of Death — must submit a ticket, wait in a queue, and interact with support personnel who search knowledge bases, consult documentation and perform diagnostic steps sequentially. This arrangement controls cost, because generalists filter work before it reaches specialists, but it imposes two structural penalties: queuing delay at each tier, and repeated context-gathering at each handoff, since the information a user supplied at L1 is rarely sufficient for L2 and must be elicited again.

**A large share of this workload is repetitive.** Password and access problems, VPN and network connectivity faults, endpoint performance degradation, and peripheral or driver failures recur continuously, and resolutions for much of this work already exist within the organisation's own records. The problem is therefore not primarily one of missing knowledge but of the cost of locating, interpreting and applying existing knowledge on every recurrence. This reading is supported by direct measurement rather than assumption. In the largest field study of generative AI in a support setting conducted to date, Brynjolfsson, Li and Raymond observed the staggered introduction of a generative-AI conversational assistant across **5,179 customer support agents** and measured an increase in productivity, defined as issues resolved per hour, of **14% on average**, comprising a **34% improvement for novice and low-skilled workers** but minimal impact on experienced and highly skilled ones [3]. The authors attribute the effect to the dissemination of the working practice of more able agents, which helps newer agents move down the experience curve [3]. Two implications matter here. First, the improvement is an improvement in **knowledge access** rather than in generative fluency, which confirms from the demand side the constraint that ITSM process research identifies from the supply side [1]. Second, the assistant that produced these gains **recommended; it did not act** — the measured 14% is the value of better advice delivered to a human who must still perform the work. Whether that residual work can itself be automated, and under what conditions doing so would be safe, is the question this research investigates.

**What has been attempted, and where it stops.** The academic response to the repetitiveness of support work has largely taken the form of supervised learning applied to the ticket record. Oliveira, Nogueira and Brito compare six supervised algorithms for classifying IT incident tickets using text mining and natural language processing, and report **93.12% accuracy** for a linear support vector classifier, ahead of stochastic gradient descent (90.01%), logistic regression (88.65%) and multinomial naïve Bayes (85.03%) [4]. Their secondary findings matter more than the headline figure: random oversampling materially improved results, and the smaller datasets to which it was not applied performed appreciably worse [4]. Automated ticket categorisation is therefore substantially achievable, but its accuracy is contingent on corpus size and on explicit treatment of class imbalance rather than being an intrinsic property of the method. Related work extends supervised learning from categorisation to timing: Mulyati et al. show that predicting incident resolution time improves substantially when features are aggregated across the incident lifecycle rather than taken at ticket-open time alone, their lifecycle-aggregated random forest regressor attaining **R² = 0.8318 with a mean absolute error of 60.67 hours**, against **R² = 0.5412** for the non-aggregated configuration [5]. The structural limitation shared by this body of work is that the model is a terminal artefact: a ticket is classified, or a duration predicted, and the process ends. The model does not participate in diagnosis, does not consult resolution knowledge, and does not act. Reported accuracies, however high, therefore measure a sub-task upstream of the work a support engineer actually performs.

**The technological opportunity.** Three developments make the end-to-end problem newly tractable, and each carries a documented limitation that constrains how it may responsibly be used.

- **Large Language Models (LLMs).** Contemporary LLMs exhibit multi-step reasoning and sustained instruction-following, capabilities that emerge above certain parameter scales and are shaped further by adaptation tuning [6]. The property that matters for IT support is conditional adaptation: selecting the next diagnostic step from the reported outcome of the previous one, which a fixed decision tree cannot do beyond the branches its author anticipated. The corresponding weakness is equally well documented — fluent generation of confident but factually incorrect content, together with knowledge staleness and untraceable reasoning [6].

- **Retrieval Augmented Generation (RAG).** RAG conditions generation on documents retrieved from a trusted corpus, pairing the model's parametric knowledge with an explicit non-parametric memory that can be inspected and updated without retraining [7]; the approach has since matured into a design space of retrieval, ranking and integration strategies motivated explicitly by hallucination, knowledge staleness and untraceable reasoning [8]. Its retrieval component rests on dense representation learning: dual-encoder passage retrieval trained from limited question–passage supervision substantially outperforms sparse lexical baselines on top-*k* retrieval accuracy [9], and siamese sentence-embedding networks make large-scale semantic comparison tractable by allowing passages to be encoded independently and compared by cosine similarity [10]. This matters concretely in IT support, where a user writes "my internet keeps dropping" while the relevant article is titled "Wireless adapter power management configuration" — a match lexical search cannot make. Domain-specific evidence exists: Toro Isaza et al. construct an incident-resolution recommendation system for an IT support client that combines RAG-based answer generation with an encoder-only classifier and a generative query-formulation stage, designed explicitly around two enterprise constraints, incomplete domain coverage of the knowledge base and restricted model size where organisations decline larger proprietary models on cost and privacy grounds [11]. Xu et al., working on a production customer-service ticket corpus, show that conventional RAG treats past tickets as flat text and thereby discards intra-issue structure and inter-issue relations; preserving that structure improved retrieval by **77.6% in mean reciprocal rank** and, over approximately six months of production use, reduced **median per-issue resolution time by 28.6%** [12].

- **Multi-Agent Systems (MAS).** Rather than a single model performing every function, the agentic paradigm decomposes a task across specialised components that reason, act, observe the outcome and iterate. The ReAct formulation established that interleaving reasoning traces with actions allows a model to induce, track and revise plans while interfacing with external sources, with observation feedback closing the loop [13]. Wang et al. survey LLM-based autonomous agents and formalise their construction around profiling, memory, planning and action [14], while Liu et al. survey 124 studies applying LLM-based agents across software engineering activities and document both the breadth of adoption and the reliability, evaluation and cost challenges that remain open [15]. For this research the decomposition matters for governance as much as for capability, because it creates explicit, nameable boundaries at which policy can be enforced and at which each component can be tested independently.

**Why the problem nevertheless remains unsolved.** Despite these advances, a gap persists between the demonstrated capability of individual AI components and their reliable application in enterprise IT support, and the evidence for this is measured rather than asserted. ITBench, a benchmark of **102 real-world IT automation scenarios** spanning site reliability engineering (SRE), compliance and security operations, and financial operations, reports that agents built on state-of-the-art models resolve only **11.4% of SRE scenarios, 25.2% of compliance and security-operations scenarios and 25.8% of financial-operations scenarios**, with anomaly-detection tasks reaching an F1 score of only 0.35 [16]. These are not marginal shortfalls to be closed by a larger model; they indicate that *composing* capable components into a system that reliably completes realistic IT work is itself unsolved. Domain studies converge on the same picture nearer the support desk. Ahmed et al. conduct a large-scale study of LLMs for recommending root causes and mitigation steps across more than 40,000 production incidents at Microsoft, and find genuine assistance together with performance short of autonomous reliability [17]. Chen et al.'s RCACopilot, a production on-call system that matches an incident to a handler and aggregates critical runtime diagnostic information *before* invoking the model, achieves root-cause analysis accuracy of **up to 0.766** over a year of real incidents [18]. A system correct roughly three times in four is a valuable assistant and an unacceptable autonomous actor, and the distance between those two roles is where this research is situated; the architectural lesson of [18] — that the model performs better over assembled context than over a raw problem description — is the same principle that motivates retrieval grounding. At field level, a survey analysing **183 research papers published between January 2020 and December 2024** documents rapid expansion of LLM application across failure-management tasks alongside fragmented architectures, uneven data practices and inconsistent evaluation methodology [19]. A recent development sharpens the opportunity rather than removing it: VIGIL, an edge-extended agentic system for enterprise IT support, deploys desktop-resident agents performing situated diagnosis, retrieval over enterprise knowledge and policy-governed remediation on user devices with explicit consent, and reports from a **10-week pilot on 100 resource-constrained endpoints** a **39% reduction in interaction rounds**, at least **fourfold faster diagnosis**, and **self-service resolution in 82% of matched cases** [2]. This confirms that consent-gated, knowledge-grounded remediation is a viable design direction; it equally shows that the direction remains under-characterised, since the gains are attributed to the system as a whole and no decomposition establishes which architectural components produce them.

**The safety dimension of a system that acts.** Any support system that executes commands on user machines consumes untrusted input by construction — user prose, pasted logs, error text, uploaded screenshots — and is therefore exposed to prompt injection. Greshake et al. established that adversarial instructions need not originate with the user at all, since content *retrieved* by an LLM-integrated application can itself carry the attack, an indirect vector that applies to any system performing retrieval over a corpus it does not fully control [20]. Liu et al. establish the breadth of the exposure: applying a black-box injection technique to **36 real-world LLM-integrated applications, 31 were found susceptible**, with 10 vendors subsequently validating the findings [21]. Where a model is permitted to call tools, the exposure changes from an information risk into an execution risk. AgentDojo, an evaluation environment of **97 realistic tool-using tasks and 629 security test cases**, finds that existing attacks break some security properties while existing defences close some but not all [22]; and ToolEmu, using a language-model-emulated sandbox across 36 toolkits and 144 test cases, reports that **68.8% of the failures it surfaces are confirmed by human evaluation as genuine risks**, and that even the safest agent evaluated fails in **23.9%** of test cases [23]. Read together, these results establish that the human-in-the-loop control proposed in this research is a technical necessity rather than a courtesy to the user.

---

## 1.3 Problem Statement

### 1.3.1 General Problem

Enterprise IT support operations face an escalating problem of efficiency, scalability and user satisfaction, and the problem is structural rather than incidental.

First, the volume and complexity of IT support requests continue to grow, driven by remote and hybrid working, bring-your-own-device policies, cloud migration and increasingly layered software ecosystems, producing precisely the heterogeneous, long-tail environment that recent work identifies as difficult to resolve centrally [2]. Support capacity, by contrast, is bounded by the number of trained engineers an organisation can employ and retain. The two quantities do not scale together, and the difference between them is absorbed as queuing delay, deferred resolution and displaced user productivity.

Second, the repetitive and knowledge-intensive nature of IT troubleshooting means that a substantial proportion of tickets concern previously encountered issues whose solutions already exist in organisational records but are costly to locate, interpret and apply on each recurrence [1]. That this is the binding constraint is supported by direct measurement: when support agents were given an assistant that made the working practice of high performers accessible, throughput rose by 14%, and the gain concentrated among the least experienced agents — the distributional signature expected if the limiting factor is access to knowledge the organisation already holds [3].

Automation to date addresses this only partially, and existing approaches fall short at opposite ends of the same axis. Systems restricted to information retrieval are safe but shallow, terminating at a recommendation the user must still carry out and leaving the residual manual effort untouched. Systems that extend into action-taking are useful but are not accompanied, in the published literature, by governance evidence sufficient to justify confident deployment. That agents built on state-of-the-art models resolve only 11.4% of realistic SRE scenarios [16] indicates that the deficiency is **architectural rather than merely a matter of model capability**, since the same models perform considerably better on isolated reasoning tasks than on composed operational ones.

The combined effect of rising demand, constrained supply and under-exploited organisational knowledge is a compounding inefficiency that degrades productivity, increases operational cost, and burdens IT support teams with repetitive workloads.

### 1.3.2 Specific Problem

Within the ITSM domain, six specific shortcomings persist that current solutions fail to address adequately.

**1. Lack of intelligent conversation understanding.** Existing IT support chatbots rely largely on keyword matching or intent classification against a fixed taxonomy, and consequently cannot sustain multi-turn, context-aware troubleshooting dialogue. They fail to distinguish technical from non-technical queries reliably, miss urgency signals, and cannot adapt their troubleshooting path in response to what the user reports back. The capability actually required is conditional reasoning over accumulated dialogue state — selecting the next diagnostic action from the outcome of the previous one [6], [13] — which is a different capability from intent lookup, and one the supervised ticket-classification literature does not supply, because it classifies a completed record rather than participating in an unfolding conversation [4].

**2. Absence of knowledge-grounded reasoning.** Conventional chatbot systems generate responses without grounding them in organisation-specific knowledge, producing guidance that is plausible in general but inappropriate for the particular organisation: referencing tools it does not use, procedures it does not follow, or configurations it does not have. Retrieval grounding is the established mitigation [7], [8], and domain implementations demonstrate its value under realistic enterprise constraints of knowledge coverage and model size [11], [12]. What the literature predominantly reports, however, is *retrieval and answer quality*; the contribution of grounding to **end-to-end resolution outcomes** within a complete support pipeline is rarely isolated and measured [11], [12].

**3. Manual and static ticket management.** Ticket creation, classification, prioritisation and assignment remain predominantly manual, or governed by static rules that take no account of agent specialisation, current workload, or the nuanced context of the reported issue. Supervised approaches to ticket classification [4] and resolution-time prediction [5] exist, but as standalone models detached from the conversational process that generates the ticket. In the resolution-time case the detachment carries a measurable cost, because the features available at ticket-open time are demonstrably the weakest configuration, while lifecycle-derived features are the strongest [5].

**4. No autonomous remediation capability.** Current IT support systems function predominantly as information-retrieval tools: they can suggest a solution but cannot execute diagnostic or remediation actions on the user's system, even for safe, well-defined operations such as clearing temporary files, flushing the DNS cache or restarting a Windows service. The value of closing this gap is evidenced both by the productivity gain an advice-only assistant already produces [3] and by a pilot in which consent-governed on-device remediation supported self-service resolution in 82% of matched cases [2]. Closing it, however, requires executing commands on user systems, which introduces demonstrated security exposure through direct and indirect prompt injection [20], [21], [22], [23]. The shortcoming is therefore not simply that systems do not act, but that the governance under which they could act safely has not been specified and tested within an end-user IT support system.

**5. Fragmented agent architecture.** Existing solutions lack a cohesive multi-agent architecture in which specialised agents collaboratively handle distinct aspects of the support workflow — conversation management, ticket intelligence, action execution, image analysis and status tracking — resulting in monolithic and inflexible systems. Agent decomposition patterns are well established in the general literature [13], [14], [15], but their benefit has not been isolated empirically within an ITSM setting, and the closest integrated system in this domain reports aggregate outcomes rather than per-component contributions [2].

**6. Insufficient predictive and proactive capability.** Most IT support systems are purely reactive, responding only after an issue is reported. They lack predictive components for resolution-time and SLA-breach risk estimation and for system-health monitoring. Predictive modelling of incident resolution time is demonstrably feasible but sensitive to feature specification, with lifecycle-aggregated features substantially outperforming those available at ticket creation [5] — a finding that a system integrating prediction with the conversational process is better positioned to exploit than a standalone predictor.

**Research gap.** The paradigms that would address these six shortcomings have been developed and evaluated largely in isolation from one another. Ticket classification and resolution-time prediction are studied as terminal artefacts [4], [5]; retrieval grounding is evaluated on retrieval and answer quality rather than on resolution outcomes [11], [12]; LLM-based incident diagnosis stops at recommendation and reaches at best 0.766 accuracy in production [17], [18]; agent decomposition is well theorised but not empirically isolated in this domain [13], [14], [15]; and the safety obligations of an acting system are documented as principles without being instantiated and tested inside a domain support system [20]–[23]. Field-level survey evidence characterises the resulting picture as fragmented and inconsistently evaluated [19], and benchmark evidence confirms that the composed task remains largely unachieved [16].

> **Statement of the research gap.** There exists no *openly documented and independently evaluable* integrated IT support platform that combines LLM-driven conversational intelligence, RAG-based knowledge retrieval, human-gated system remediation, intelligent multi-agent ticket management, visual analysis of error screenshots, and predictive analytics within a single secure and auditable framework. This research intends to address that gap.

The gap is stated in this bounded form deliberately. An unqualified claim that no integrated platform of this kind exists cannot be sustained, because VIGIL reports an industrial pilot of an integrated system combining situated diagnosis, retrieval over enterprise knowledge and consent-governed remediation on user devices [2]. What the literature genuinely lacks is an integrated architecture published at a level that permits inspection, reimplementation and independent evaluation, and whose components can be assessed individually rather than only in aggregate — which is precisely what [2] does not provide and what [19] identifies as a field-level deficiency.

---

## 1.4 Research Question

**Primary research question**

> *How can a multi-agent AI system leveraging Large Language Models (LLMs) and Retrieval Augmented Generation (RAG) be designed, implemented and evaluated to handle end-to-end IT support operations — conversational issue understanding, knowledge-grounded troubleshooting, automated ticket lifecycle management, human-approved system remediation, and predictive analytics — while maintaining security, auditability and human-in-the-loop control?*

The question is design-oriented, which is appropriate to a study whose primary output is an artefact together with knowledge about it; its empirical component is supplied by the fourth objective (§1.7.4), which requires the constructed system to be evaluated rather than merely demonstrated. The final clause is a substantive constraint rather than a qualification: because a system permitted to act faces demonstrated adversarial exposure [20]–[23], a design satisfying the first part of the question without the second would not answer it.

**Sub-questions**

1. **How** can LLM-powered conversational agents classify, understand and respond to diverse IT support queries through natural, multi-turn dialogue, given that conditional multi-step reasoning is a documented LLM capability [6], [13] whereas supervised ticket classification addresses only the categorisation sub-task [4]?
2. **How** can Retrieval Augmented Generation be employed to ground AI-generated troubleshooting advice in organisation-specific knowledge, thereby improving accuracy and reducing hallucination [7], [8], and **to what extent** does that grounding affect end-to-end resolution outcomes rather than retrieval quality alone [11], [12]?
3. **How** can a multi-agent architecture be designed to orchestrate specialised agents for conversation management, ticket intelligence, action execution, image analysis and status tracking within one coherent IT support workflow, given that decomposition patterns are established generally [13], [14], [15] but not isolated within ITSM [2], [19]?
4. **How** can system remediation actions be executed safely under explicit user consent, risk assessment and comprehensive audit logging, given that direct and indirect prompt injection against tool-using applications is demonstrated and practical [20], [21], [22], [23]?
5. **To what extent** can machine learning models integrated with the conversational process predict resolution time and SLA-breach risk, given that such prediction is feasible but strongly sensitive to feature specification [5]?

---

## 1.5 Research Motivation

**Observed inefficiency in IT support practice.** Firsthand observation in organisational IT environments indicated that support teams spend a disproportionate share of their time on repetitive issues — password resets, VPN connectivity faults, software configuration errors — that appear amenable to intelligent automation. This observation prompted the investigation, and it is corroborated by ITSM process research that documents the maintenance and application of resolution knowledge as a persistent rather than a solved challenge [1].

**Measured evidence that improving knowledge access has value.** The motivation does not rest on observation alone. A field study across 5,179 support agents measured a 14% increase in issues resolved per hour when a generative assistant was introduced, with a 34% gain among novice and low-skilled workers and minimal effect on the most experienced [3]. This establishes that improving knowledge access in support work has real and quantified value — and it does so for a system that only advised, which raises directly the question this research pursues: what architecture delivers that value most effectively, and how far can it be extended from advice into action?

**Measured evidence that the problem is not already solved.** The 11.4% resolution rate reported for agents built on state-of-the-art models against realistic SRE scenarios [16], and the ceiling of 0.766 root-cause accuracy reached by a production system over a year of real incidents [18], together show that applying current models to IT operations does not by itself produce competent automation. Architectural research is therefore warranted rather than redundant.

**The promise of retrieval grounding for domain-specific knowledge.** Retrieval augmentation combines the generative capability of LLMs with grounding in curated organisational knowledge, addressing the hallucination risk that makes unconstrained generation inadmissible in a domain where an incorrect instruction may be executed on a working machine [7], [8]. Domain implementations show that this is practical under real enterprise constraints and can shorten resolution time in production use [11], [12].

**The multi-agent paradigm.** The growing body of research on LLM-based agents [13], [14], [15] motivates a collaborative architecture in which specialised agents each handle a distinct aspect of the support workflow. Decomposition additionally creates explicit boundaries at which governance can be enforced and each component tested independently — a property a monolithic implementation cannot offer, and one that matters given the demonstrated exposure of tool-using systems to prompt injection [20]–[23].

**Bridging the theory–practice gap.** While academic work on LLMs, RAG and multi-agent systems is abundant, openly documented implementations integrating these technologies into a coherent IT support platform remain scarce; the closest published system reports aggregate outcomes without decomposing them [2], within a field that surveys characterise as fragmented and inconsistently evaluated [19]. This research is motivated by the opportunity to produce an openly documented and inspectable architecture at a scale appropriate to an undergraduate thesis.

---

## 1.6 Research Aim

> The aim of this research is to design, develop and evaluate an intelligent multi-agent IT support system (**Auto-Ops-AI**) that leverages Large Language Models and Retrieval Augmented Generation to automate end-to-end IT support operations — conversational issue understanding, knowledge-grounded troubleshooting, intelligent ticket lifecycle management, human-approved system remediation, visual error analysis and predictive analytics — within a secure, auditable and human-in-the-loop framework, and to determine its effect on resolution time, support efficiency and user satisfaction relative to a matched manual baseline evaluated on the same scenarios.

The final clause states the comparison in the form the study can actually substantiate. Comparing measured system performance against published industry averages for L1 resolution time would not support the conclusion it appears to support, because the population, ticket mix, organisational context and measurement definition all differ. The comparison is therefore internal: the same scenarios, the same scoring criteria and the same timing protocol, with system assistance as the manipulated variable.

---

## 1.7 Research Objectives

### 1.7.1 To Identify

To identify the key challenges, limitations and inefficiencies of existing IT support systems and chatbot-based support tools through a structured review of the literature, and thereby to establish the functional and safety requirements for an intelligent multi-agent IT support platform.

*Assessable outcome:* a comparative analysis of existing approaches — supervised ITSM machine learning [4], [5], LLM-based incident diagnosis [17], [18], retrieval-augmented support [11], [12] and integrated agentic IT support [2] — stating for each what was done, what was found, what limits the finding, and what remains unresolved, concluding in an explicit requirements list that Chapter 4 can be checked against.

### 1.7.2 To Analyze

To analyse the capabilities, architectural patterns and documented failure modes of Large Language Models, Retrieval Augmented Generation and multi-agent systems in the context of IT service management, and to evaluate their suitability for conversational troubleshooting, knowledge-grounded response generation, intelligent ticket management and human-approved remediation.

*Assessable outcome:* a technological analysis at the algorithmic [6]–[10], design [13], [14], [15], [20]–[23] and workflow levels, in which each strand terminates in an explicitly justified design decision for the proposed system.

### 1.7.3 To Design and Develop

To design and develop the multi-agent IT support system **Auto-Ops-AI**, comprising five specialised AI agents:

- **LLM Conversation Agent** — natural language understanding, contextual dialogue management and response generation;
- **Ticket Intelligence Agent** — automated ticket creation, priority analysis, metadata generation and resolution detection;
- **Action Executor Agent** — safe, permission-based execution of diagnostic and remediation actions on user systems;
- **Image Analysis Agent** — visual analysis of error screenshots, device photographs and technical images using multimodal AI;
- **Ticket Status Agent** — ticket lifecycle transitions, SLA tracking, escalation detection and auto-closure;

integrated with RAG-based knowledge retrieval over a vector store, role-based access control (RBAC), audit logging, and a React-based frontend dashboard.

*Assessable outcome:* an operational system in which each of the five agents is implemented as a discrete, independently exercisable module within the request pipeline, and in which remediation is constrained by an enumerated action whitelist, parameter validation and a mandatory user-approval gate enforced in application code rather than by model instruction [20]–[23].

### 1.7.4 To Evaluate

To evaluate the developed system through quantitative metrics (ticket resolution time, classification accuracy, resolution-time and SLA-risk prediction accuracy, RAG retrieval relevance, and the resilience of the remediation pathway to adversarial input) and qualitative measures (user satisfaction, perceived usability and troubleshooting effectiveness), comparing the results against a matched manual baseline conducted on the same scenarios.

*Assessable outcome:* measured results on a defined scenario set with human-authored ground truth, reported together with the conditions under which they were obtained; classification performance compared against a published supervised baseline for IT incident tickets [4]; retrieval relevance reported separately from end-to-end resolution outcomes, following the distinction that [11] and [12] leave unresolved; and the approval gate tested against injected instructions rather than assumed to hold [20], [21], [22].

---

## 1.8 Rich Picture of the Proposed Solution

The proposed **Auto-Ops-AI** system employs a multi-agent architecture in which five specialised AI agents collaborate through an orchestration layer to deliver end-to-end IT support automation. The architecture is layered so that each concern identified in Section 1.3.2 is handled at exactly one place: interpretation of user language in the agent layer, factual grounding in the RAG engine, action execution behind an enforced whitelist, persistence and audit in the data layer, and prediction in a separate model layer.

### Figure 1.1 — System architecture overview

```
┌───────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                           │
│   Chat UI (Text/Image) │ Dashboard │ Ticket Manager │ Admin Panel     │
└──────────────────────────────┬────────────────────────────────────────┘
                               │  REST / JSON
┌──────────────────────────────▼────────────────────────────────────────┐
│         BACKEND API (FastAPI) — Authentication (JWT + RBAC)           │
├───────────────────────────────────────────────────────────────────────┤
│                      AGENT ORCHESTRATION LAYER                        │
│                                                                       │
│   ┌────────────────────┐ ┌────────────────────┐ ┌──────────────────┐  │
│   │ LLM Conversation   │ │ Ticket Intelligence│ │ Action Executor  │  │
│   │ Agent              │ │ Agent              │ │ Agent            │  │
│   │  · classify        │ │  · create          │ │  · whitelisted   │  │
│   │  · respond         │ │  · prioritise      │ │    actions only  │  │
│   │  · escalate        │ │  · categorise      │ │  · risk tiering  │  │
│   │  · context         │ │  · resolve         │ │  · USER APPROVAL │  │
│   └────────────────────┘ └────────────────────┘ └──────────────────┘  │
│                                                                       │
│   ┌────────────────────┐ ┌────────────────────┐                       │
│   │ Image Analysis     │ │ Ticket Status      │                       │
│   │ Agent              │ │ Agent              │                       │
│   │  · OCR / vision    │ │  · lifecycle       │                       │
│   │  · categorise      │ │  · SLA tracking    │                       │
│   │  · keywords → RAG  │ │  · auto-close      │                       │
│   └────────────────────┘ └────────────────────┘                       │
├───────────────────────────────────────────────────────────────────────┤
│  RAG Engine            │  Dataset / Assignment │  PowerShell Engine   │
│  (ChromaDB vector      │  Analyzer             │  (system commands,   │
│   store + embeddings)  │  (semantic similarity)│   no shell interpr.) │
├───────────────────────────────────────────────────────────────────────┤
│  DATA LAYER: Knowledge Base (JSON) │ ChromaDB │ SQLite (tickets,      │
│              users, roles)         │          │ Audit Logs           │
├───────────────────────────────────────────────────────────────────────┤
│  ML MODELS LAYER: SLA / resolution-time predictor │ System-health     │
│                   predictor │ Category encoder                        │
└───────────────────────────────────────────────────────────────────────┘
```

**Reading the architecture.** The frontend provides four surfaces — a chat interface accepting text and images, an analytics dashboard, a ticket manager and an administrative panel — all of which reach the system through a single authenticated REST API. Authentication and role-based access control sit at the API boundary rather than inside the agents, so that no agent can be reached without an authorisation decision having already been made. Beneath the API, the orchestration layer routes a request to the agents required by that request rather than through all five in sequence. The three supporting engines are deliberately separated from the agents that invoke them: the RAG engine owns retrieval, the dataset analyzer owns similarity-based assignment, and the PowerShell engine owns command execution, which means each can be tested, replaced or constrained without touching agent logic. The data layer holds the knowledge base, the vector store, the relational store for tickets, users and roles, and the audit log; the audit log is written by the orchestration layer rather than by the agents, so that a record exists independently of whether an agent behaved as designed. The ML models layer is kept separate from the agents because its outputs are advisory signals for prioritisation and monitoring, not control decisions.

### Figure 1.2 — Key workflow: end-to-end IT support conversation

```
   User message (text and/or screenshot)
              │
              ▼
   [Image Analysis Agent] ── if an image is attached, its extracted
              │               description and keywords are merged into the
              ▼               textual message
   [LLM Conversation Agent] ── classify · understand
              │
              ├──── not technical ─────────────► casual / conversational reply
              │
              ▼ technical
   [RAG Engine] ── semantic search over the organisational knowledge base
              │
              ▼
   [LLM Conversation Agent] ── grounded multi-turn troubleshooting dialogue
              │
              ▼
   [Ticket Intelligence Agent] ── create ticket · score urgency · categorise
              │
              ▼
   [Action Executor Agent] ── propose a remediation action from the
              │                whitelist, together with its risk tier
              ▼
   ►►► USER APPROVAL REQUIRED ◄◄◄ ── nothing executes before explicit,
              │                        logged approval by the user
              ▼
   Execute → report result → write audit record
              │
              ▼
   [Ticket Status Agent] ── track · resolve and close, or escalate to a
                            human support agent
```

**Reading the workflow.** The workflow implements the closed loop that Section 1.3.2 identifies as missing from existing systems: understanding the issue, retrieving the organisation's own resolution knowledge, acting on the user's machine under consent, and closing or escalating the ticket. Three properties of this ordering are deliberate. First, image input is normalised into text before classification, so that image-originated requests follow the same, single decision path as typed requests rather than a separate and less exercised one. Second, retrieval occurs before the troubleshooting dialogue rather than after it, so that the advice offered is conditioned on organisational knowledge rather than corrected against it afterwards [7], [8]. Third, the approval gate is the final step before execution and is enforced in application code, not by instructing the model to seek permission.

**Rationale for the approval gate.** An instruction expressed inside the model's context is a string, indistinguishable in kind from an injected string arriving in user text, a pasted log or a retrieved document [20], [22]. A control expressed instead as an enumerated whitelist with parameter validation, evaluated in application code, is categorically different, because nothing the model outputs can extend the set of operations the application is capable of executing [21], [23]. This is what makes the "human-in-the-loop control" clause of the research question a testable property of the system rather than a stated intention.

### The five specialised agents and their roles

| Agent | Responsibility | Key technologies |
|---|---|---|
| **LLM Conversation Agent** | Natural language understanding; multi-turn dialogue management; message classification (technical / general / greeting); contextual response generation; escalation detection | Google Gemini LLM; prompt engineering; conversation memory window |
| **Ticket Intelligence Agent** | Intelligent ticket-creation timing; priority analysis (urgency scoring 0–10); LLM-generated title and description; category classification; resolution detection | Google Gemini LLM; hybrid rule-based and LLM logic |
| **Action Executor Agent** | Whitelisted system-action management; parameter validation; user permission workflow; PowerShell command execution; follow-up action suggestion | Enumerated action whitelist with risk tiering; parameter sanitisation; PowerShell via subprocess |
| **Image Analysis Agent** | Visual analysis of error screenshots and device photographs; text extraction; issue categorisation from images; keyword extraction for RAG search | Google Gemini Vision (multimodal LLM) |
| **Ticket Status Agent** | Ticket lifecycle management (OPEN → IN PROGRESS → RESOLVED → CLOSED); resolution and re-open detection; SLA tracking; auto-closure; abandonment detection | Rule-based state machine; SLA algorithms |

**Rationale for a heterogeneous agent design.** The five agents are deliberately not uniform in implementation: three are generative, one combines generative and rule-based logic, and the Ticket Status Agent is a deterministic state machine. The principle is single — generative where unconstrained user language must be interpreted, deterministic where accountability is required. Lifecycle state governs SLA accounting and the audit record, and an auditor asking why a ticket moved from OPEN to RESOLVED requires a reconstruction of the decision, which deterministic rules provide by re-execution and a generative justification does not.

**Rationale for multimodal input.** Users often describe faults poorly in prose but capture them accurately in a screenshot: an error dialogue, a stop code or a network status panel carries diagnostic detail that a free-text paraphrase loses. Multimodal LLM-based fault detection and diagnosis has been demonstrated in industrial fault-diagnosis settings [24], and the transfer to end-user IT support is direct. The Image Analysis Agent's output is merged into the textual message and passed through the same classification and retrieval path as ordinary text, for the reason given above.

---

## 1.9 Resource Requirements

### 1.9.1 Hardware Requirements

| Resource | Minimum specification | Recommended specification |
|---|---|---|
| Processor | Intel Core i5 (8th Gen) or equivalent | Intel Core i7 (10th Gen) or AMD Ryzen 7 |
| RAM | 8 GB DDR4 | 16 GB DDR4 |
| Storage | 256 GB SSD (50 GB free) | 512 GB SSD (100 GB free) |
| Network | Stable internet connection (5 Mbps) | Broadband connection (25+ Mbps) |
| GPU | Not required (cloud-based AI inference) | NVIDIA GPU (optional, for local model hosting) |
| Test environment | One isolated Windows virtual machine with snapshot capability | Two virtual machines |

Two entries require justification. The **network** requirement is functional rather than nominal, because every generative and embedding call is a network round trip, and link quality therefore enters directly into the latency measurements required by objective 1.7.4. The **isolated test environment** is required because remediation actions mutate system state; comparable timing across repeated trials is only possible if each trial begins from an identical restored baseline, and destructive mistakes during development must not affect a working machine.

### 1.9.2 Software Requirements

| Category | Software / tool | Version | Purpose |
|---|---|---|---|
| Programming language | Python | 3.11+ | Backend development, AI/ML |
| Runtime | Node.js | 18+ | Frontend development |
| Backend framework | FastAPI | Latest | REST API development |
| Frontend framework | React | 19 | User interface |
| Build tool | Vite | 7 | Frontend build and development server |
| LLM provider | Google Gemini API | 1.5 Pro / 2.0 Flash (version recorded with all results) | Natural language processing and vision |
| Vector database | ChromaDB | Latest | RAG knowledge retrieval |
| Relational database | SQLite | 3.x | Ticket, user and audit data |
| ORM | SQLAlchemy | Latest | Database abstraction |
| RAG tooling | LangChain (`langchain-chroma`, `langchain-google-genai`) | Latest | Knowledge base ingestion and embedding pipeline |
| Embedding model | Google `text-embedding-004` | Latest | Semantic similarity search |
| ML libraries | scikit-learn, NumPy, Pandas | Latest | Predictive models and data analysis |
| Command execution | Windows PowerShell via subprocess | — | Execution of whitelisted remediation actions |
| Containerisation | Docker + Docker Compose | Latest | Deployment and environment management |
| Authentication | JWT (PyJWT) + bcrypt | Latest | Secure user authentication |
| Version control | Git + GitHub | Latest | Source code management |
| IDE | Visual Studio Code | Latest | Development environment |
| API testing | Swagger UI (built-in) | Auto-generated | API documentation and testing |
| Operating system | Windows 10/11 (Linux supported for containerised backend deployment) | Latest | Development and deployment |

The Gemini model version is recorded with every result because a hosted model may be updated by its provider without notice; results conditioned on an unrecorded version are not reproducible, since a provider-side change would appear in the data as an unexplained change in system behaviour.

---

## 1.10 Project Scope

The table below delineates the boundaries of this research. Several exclusions remove capability the system could technically support; in each case the reason is that including it would either confound a measured comparison or add engineering surface without addressing any problem stated in Section 1.3.

| Aspect | In scope | Out of scope | Reason for the boundary |
|---|---|---|---|
| **Conversational AI** | Multi-turn, context-aware IT support dialogue using the Google Gemini LLM, with conversation memory management and escalation detection | Integration with third-party communication platforms (Slack, Microsoft Teams, WhatsApp) | Channel integration is engineering surface rather than research surface and would not alter any measured outcome |
| **Knowledge retrieval** | RAG-based knowledge base search using a ChromaDB vector store with semantic similarity matching over curated organisational IT knowledge | Real-time web crawling or external internet search for solutions | The research claim concerns grounding in *organisational* knowledge [11], [12]; open-web retrieval would introduce an uncontrolled second knowledge source |
| **Input modalities** | Text queries; image upload and analysis of screenshots and error photographs via Gemini Vision | Voice input processing, video analysis, real-time screen sharing | Multimodal fault description is supported by evidence [24] and inexpensive to implement; video and voice add cost without addressing a stated problem |
| **Ticket management** | Automated ticket creation, urgency scoring, LLM-based categorisation, and agent assignment informed by specialisation and workload | Integration with external ITSM platforms (ServiceNow, Jira Service Management, Zendesk) | Integration would make lifecycle behaviour depend on an external system's rules, preventing attribution of observed behaviour to the proposed design |
| **System remediation** | Whitelisted, risk-tiered diagnostic and remediation actions on Windows systems (process management, cleanup, network diagnostics, service management) under a mandatory user-approval workflow | Cross-platform remediation (macOS, Linux), destructive system operations, remote machine access | Destructive operations are excluded on ethical grounds; single-platform coverage is a stated limitation of the study rather than a claim about generality |
| **Multi-agent system** | Five specialised AI agents (Conversation, Ticket Intelligence, Action Executor, Image Analysis, Ticket Status) under coordinated orchestration | Self-evolving agent capabilities, agent-to-agent negotiation, dynamic agent creation | Deterministic orchestration is required if repeated trials of the same scenario are to be comparable; autonomous negotiation would make them non-comparable |
| **Security and access control** | Role-based access control across defined end-user, support-tier and administrative roles; JWT authentication; comprehensive audit logging; testing of the remediation pathway against adversarial input | Single Sign-On, OAuth2 federation, Active Directory integration, multi-factor authentication | Enterprise identity federation is a deployment concern that does not bear on the safety property under test [20]–[23] |
| **Predictive analytics** | SLA-breach risk prediction, ticket resolution-time estimation and system-health prediction | Advanced anomaly detection, real-time predictive maintenance, capacity planning | Retained as specified; feature specification follows the lifecycle-aggregation finding of [5], whereas the excluded capabilities require telemetry infrastructure outside this study |
| **User interface** | React-based dashboard with dark mode, ticket management views, analytics reports, admin panel and real-time monitoring | Native mobile applications (iOS/Android), Progressive Web App features | Interface breadth does not affect any measured outcome |
| **Deployment** | Docker containerisation and single-server deployment configuration | Kubernetes orchestration, multi-region deployment, high-availability clustering, cloud-native auto-scaling | Reproducible single-node deployment is sufficient for the evaluation and supports independent reimplementation |
| **Data** | A curated synthetic and representative enterprise IT support dataset comprising user profiles, knowledge base articles, and historical tickets with conversations | Real production data from live enterprise environments | No ethically available route exists to production support transcripts at this scale; synthetic scenarios additionally permit a defined ground truth |
| **Evaluation** | System performance metrics (resolution time, classification accuracy, prediction accuracy, RAG relevance) and usability assessment, against a matched manual baseline | Large-scale longitudinal studies, A/B testing in production environments, cross-organisational benchmarking | Beyond reach at undergraduate scale; the resulting limitation on external validity is stated rather than concealed |

Three boundaries deserve emphasis because they shape what the research can conclude. The exclusion of **external ITSM integration** keeps the ticket lifecycle entirely within the proposed system, so that observed lifecycle behaviour is attributable to the design rather than to a third-party platform's rules. The restriction of remediation to **non-destructive, whitelisted Windows actions** is what makes the safety obligations of Section 1.2 tractable within an undergraduate project: the risk surface is bounded by construction rather than by trusting the model. And the use of **synthetic data with a matched manual baseline** is what makes the evaluation interpretable, since both the ground truth and the comparison condition are defined by the study rather than inherited from an incomparable external source.

---

## 1.11 Chapter Summary

This chapter established the foundation for the research on **Auto-Ops-AI**, an intelligent multi-agent IT support system. The problem background set out the ITSM context and identified the binding constraint on support work as the cost of locating and applying knowledge the organisation already holds — a reading supported both by ITSM process research documenting knowledge-asset maintenance as a persistent challenge [1] and by field measurement showing that assistance improving knowledge access raised support productivity by 14% across 5,179 agents, with a 34% gain among the least experienced [3]. It then showed that existing academic automation treats classification and resolution-time prediction as terminal artefacts detached from diagnosis and action [4], [5]; that the enabling technologies — LLM reasoning [6], retrieval grounding [7]–[12] and agent decomposition [13], [14], [15] — are individually mature; and that the composed task nonetheless remains largely unachieved, with agents resolving only 11.4% of realistic SRE scenarios at benchmark level [16] and a production diagnosis system reaching at best 0.766 accuracy [17], [18], within a field characterised as fragmented and inconsistently evaluated [19]. It further established that any system permitted to act on user machines faces demonstrated adversarial exposure through direct and indirect prompt injection [20]–[23], which is why the proposed design places its safety controls outside the language model.

The problem statement identified the general problem of demand outgrowing constrained support capacity while resolution knowledge remains costly to apply, together with six specific shortcomings: the lack of intelligent conversation understanding, the absence of knowledge-grounded reasoning, manual and static ticket management, the absence of governed remediation capability, fragmented agent architecture, and insufficient predictive capability. The research gap was then stated in the form the evidence supports — the absence of an *openly documented and independently evaluable* integrated platform combining these capabilities — with the reason for that bounded wording made explicit.

From the gap followed a design-oriented research question and five sub-questions, a motivation grounded in observed practice and in measured evidence both of the value of AI assistance [3] and of the inadequacy of current approaches [16], [18], a research aim that fixes the evaluation comparison against a matched manual baseline, and four objectives — to identify, to analyse, to design and develop, and to evaluate — each stated with an assessable outcome. The rich picture presented the five specialised agents, the supporting RAG engine, dataset analyzer and prediction models, and the workflow that connects them, with the user-approval gate positioned as the final control before any action executes. Resource requirements, a scope table with a justification for each boundary, and the limits of what the study can conclude complete the foundation.

Chapter 2 examines the literature underlying these claims in depth, evaluating existing ITSM systems and the algorithmic, design and workflow characteristics of the technologies introduced here, in order to establish the theoretical basis on which the system in Chapter 3 is designed.

---

## References

[1] J. Serrano, J. Faustino, D. Adriano, R. Pereira, and M. Mira da Silva, "An IT service management literature review: Challenges, benefits, opportunities and implementation practices," *Information*, vol. 12, no. 3, art. 111, 2021, doi: 10.3390/info12030111.

[2] S. Ahuja, N. Kordjazi, E. Yortucboylu, V. Kapoor, M. Dundua, Y. Li, D. Ho, V. Padala, J. Whitted, and R. Steinert, "VIGIL: Towards edge-extended agentic AI for enterprise IT support," *arXiv preprint* arXiv:2603.16110, 2026.

[3] E. Brynjolfsson, D. Li, and L. R. Raymond, "Generative AI at work," National Bureau of Economic Research, Cambridge, MA, USA, NBER Working Paper 31161, Apr. 2023 (rev. Nov. 2023), doi: 10.3386/w31161.

[4] D. F. Oliveira, A. S. Nogueira, and M. A. Brito, "Performance comparison of machine learning algorithms in classifying information technologies incident tickets," *AI*, vol. 3, no. 3, pp. 601–622, 2022, doi: 10.3390/ai3030035.

[5] Mulyati, D. Stiawan, A. Rahman, M. S. Shakkah, and R. Budiarto, "Predicting incident resolution time in IT service management via lifecycle feature aggregation and machine learning," *Ingénierie des Systèmes d'Information*, vol. 31, no. 2, pp. 511–519, 2026, doi: 10.18280/isi.310219.

[6] W. X. Zhao, K. Zhou, J. Li, T. Tang, X. Wang, Y. Hou, Y. Min, B. Zhang, J. Zhang, Z. Dong, Y. Du, C. Yang, Y. Chen, Z. Chen, J. Jiang, R. Ren, Y. Li, X. Tang, Z. Liu, P. Liu, J.-Y. Nie, and J.-R. Wen, "A survey of large language models," *arXiv preprint* arXiv:2303.18223, 2023.

[7] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, "Retrieval-augmented generation for knowledge-intensive NLP tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, 2020, pp. 9459–9474.

[8] Y. Gao, Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, Y. Dai, J. Sun, M. Wang, and H. Wang, "Retrieval-augmented generation for large language models: A survey," *arXiv preprint* arXiv:2312.10997, 2024.

[9] V. Karpukhin, B. Oğuz, S. Min, P. Lewis, L. Wu, S. Edunov, D. Chen, and W. Yih, "Dense passage retrieval for open-domain question answering," in *Proc. 2020 Conf. Empirical Methods in Natural Language Processing (EMNLP)*, 2020, pp. 6769–6781, doi: 10.18653/v1/2020.emnlp-main.550.

[10] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using siamese BERT-networks," in *Proc. 2019 Conf. Empirical Methods in Natural Language Processing and 9th Int. Joint Conf. Natural Language Processing (EMNLP-IJCNLP)*, Hong Kong, China, 2019, pp. 3982–3992, doi: 10.18653/v1/D19-1410.

[11] P. Toro Isaza, M. Nidd, N. Zheutlin, J.-W. Ahn, C. A. Bhatt, Y. Deng, R. Mahindru, M. Franz, H. Florian, and S. Roukos, "Retrieval augmented generation-based incident resolution recommendation system for IT support," *arXiv preprint* arXiv:2409.13707, 2024.

[12] Z. Xu, M. J. Cruz, M. Guevara, T. Wang, M. Deshpande, X. Wang, and Z. Li, "Retrieval-augmented generation with knowledge graphs for customer service question answering," in *Proc. 47th Int. ACM SIGIR Conf. Research and Development in Information Retrieval (SIGIR '24)*, Washington, DC, USA, 2024, pp. 2905–2909, doi: 10.1145/3626772.3661370.

[13] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, "ReAct: Synergizing reasoning and acting in language models," in *Proc. Int. Conf. Learning Representations (ICLR)*, 2023.

[14] L. Wang, C. Ma, X. Feng, Z. Zhang, H. Yang, J. Zhang, Z.-Y. Chen, J. Tang, X. Chen, Y. Lin, W. X. Zhao, Z. Wei, and J.-R. Wen, "A survey on large language model based autonomous agents," *Frontiers of Computer Science*, vol. 18, no. 6, art. 186345, 2024, doi: 10.1007/s11704-024-40231-1.

[15] J. Liu, K. Wang, Y. Chen, X. Peng, Z. Chen, L. Zhang, and Y. Lou, "Large language model-based agents for software engineering: A survey," *ACM Transactions on Software Engineering and Methodology*, 2025, doi: 10.1145/3796507.

[16] S. Jha, R. Arora, Y. Watanabe, T. Yanagawa, Y. Chen, J. Clark, B. Bhavya, M. Verma, H. Kumar, H. Kitahara, N. Zheutlin, S. Takano, D. Pathak, F. George, X. Wu, B. O. Turkkan, G. Vanloo, M. Nidd, T. Dai, et al., "ITBench: Evaluating AI agents across diverse real-world IT automation tasks," in *Proc. 42nd Int. Conf. Machine Learning (ICML)*, PMLR, vol. 267, 2025.

[17] T. Ahmed, S. Ghosh, C. Bansal, T. Zimmermann, X. Zhang, and S. Rajmohan, "Recommending root-cause and mitigation steps for cloud incidents using large language models," in *Proc. IEEE/ACM 45th Int. Conf. Software Engineering (ICSE)*, Melbourne, Australia, 2023, pp. 1737–1749, doi: 10.1109/ICSE48619.2023.00149.

[18] Y. Chen, H. Xie, M. Ma, Y. Kang, X. Gao, L. Shi, Y. Cao, X. Gao, H. Fan, M. Wen, J. Zeng, S. Ghosh, X. Zhang, C. Zhang, Q. Lin, S. Rajmohan, D. Zhang, and T. Xu, "Automatic root cause analysis via large language models for cloud incidents," in *Proc. 19th European Conf. Computer Systems (EuroSys '24)*, Athens, Greece, 2024, pp. 674–688, doi: 10.1145/3627703.3629553.

[19] L. Zhang, T. Jia, M. Jia, Y. Wu, A. Liu, Y. Yang, Z. Wu, X. Hu, P. S. Yu, and Y. Li, "A survey of AIOps in the era of large language models," *ACM Computing Surveys*, 2025, doi: 10.1145/3746635.

[20] K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz, "Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection," in *Proc. 16th ACM Workshop on Artificial Intelligence and Security (AISec '23)*, Copenhagen, Denmark, 2023, pp. 79–90, doi: 10.1145/3605764.3623985.

[21] Y. Liu, G. Deng, Y. Li, K. Wang, Z. Wang, X. Wang, T. Zhang, Y. Liu, H. Wang, Y. Zheng, L. Y. Zhang, and Y. Liu, "Prompt injection attack against LLM-integrated applications," *arXiv preprint* arXiv:2306.05499, 2023.

[22] E. Debenedetti, J. Zhang, M. Balunović, L. Beurer-Kellner, M. Fischer, and F. Tramèr, "AgentDojo: A dynamic environment to evaluate prompt injection attacks and defenses for LLM agents," in *Advances in Neural Information Processing Systems (NeurIPS), Datasets and Benchmarks Track*, vol. 37, 2024.

[23] Y. Ruan, H. Dong, A. Wang, S. Pitis, Y. Zhou, J. Ba, Y. Dubois, C. J. Maddison, and T. Hashimoto, "Identifying the risks of LM agents with an LM-emulated sandbox," in *Proc. Int. Conf. Learning Representations (ICLR)*, 2024.

[24] K. M. Alsaif, A. A. Albeshri, M. A. Khemakhem, and F. E. Eassa, "Multimodal large language model-based fault detection and diagnosis in context of Industry 4.0," *Electronics*, vol. 13, no. 24, art. 4912, 2024, doi: 10.3390/electronics13244912.
