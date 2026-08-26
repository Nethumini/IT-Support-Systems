# CHAPTER – 01 [ INTRODUCTION ]

**Research title:** Context Aware Intelligent IT Support Systems: A Multi Agent Framework with Predictive Issue Detection and Automated Resolution

**Author:** P. T. N. Pathirana (28647) · NSBM Green University Town

> **Note on sources and style.** This revision preserves the research problem, research direction, objectives, proposed system and scope of Interim Submission 01. All in-text citations are IEEE numeric and refer only to the research papers supplied with this revision; the reference list at the end contains only sources actually cited in this chapter. Section 1.13 records exactly what was retained, improved, justified or corrected relative to Interim 01.

---

## 1.1 Chapter Overview

This chapter presents the introduction to the research titled **"Context Aware Intelligent IT Support Systems: A Multi Agent Framework with Predictive Issue Detection and Automated Resolution."** It commences with a discussion of the problem background that contextualizes the challenges faced by modern enterprise IT support operations, and narrows through a structured problem statement that delineates both the general organizational implications and the domain-specific shortcomings that motivate this research. A formally stated research question encapsulates the core inquiry, followed by articulations of research motivation, aim, and objectives. A rich picture of the proposed solution illustrates the envisioned multi-agent architecture and its operational workflows. The chapter concludes with resource requirements, a delineation of project scope, a statement of the significance of the research, and a chapter summary.

The chapter is deliberately organized as a single line of argument. Section 1.2 establishes the IT Service Management (ITSM) context and the evidence that the binding constraint in support work is the cost of accessing and applying existing knowledge; it then examines what current automation approaches achieve, where they stop, what technological developments make the remaining work tractable, and why — despite those developments — the composed task is not yet solved. Section 1.3 converts that evidence into a general problem, six specific problems, and a precisely bounded research gap. Sections 1.4 to 1.7 state the research question, motivation, aim and objectives that follow from the gap. Sections 1.8 to 1.12 present the proposed solution, the resources it requires, the boundary of the investigation, its significance, and a summary.

---

## 1.2 Problem Background

### 1.2.1 The IT Service Management Context

IT Service Management is the body of practice through which organizations deliver, support and improve IT services, structured around defined processes — incident management, request fulfilment, problem management and change management — and instrumented by ticketing systems and service level agreements. A systematic review of 47 studies characterizes ITSM adoption as delivering real benefits in service quality, process standardization and customer satisfaction, while simultaneously documenting persistent implementation challenges, notably the organizational cost of maintaining process discipline and the difficulty of establishing and sustaining the knowledge assets on which the processes depend [1].

That last challenge locates the problem this research addresses. ITSM frameworks presuppose documented, current and findable resolution knowledge, and the reviewed literature records that maintaining it in practice is among the persistent difficulties rather than a solved administrative matter [1].

The operational environment has made this harder rather than easier. Enterprise IT estates are heterogeneous by construction — cloud services, on-premises infrastructure, diverse endpoint devices and layered software stacks — and recent work on enterprise IT support characterizes the resulting difficulty precisely: heterogeneous devices, evolving policies and long-tail failure modes that are difficult to resolve centrally, with failures often emerging from subtle local interactions rather than clear global faults [2]. Support is delivered through tiered human escalation models (L1 → L2 → L3) mediated by ticketing systems. A user encountering a technical issue — a malfunctioning VPN connection, a slow laptop, a recurring Blue Screen of Death — must submit a ticket, wait in a queue, and interact with support personnel who may need to search knowledge bases, consult documentation and perform diagnostic steps sequentially. This arrangement controls cost, because generalists filter work before it reaches specialists, but it imposes two structural penalties: queuing delay at each tier, and repeated context-gathering at each handoff, since the information a user supplied at L1 is rarely sufficient for L2 and must be re-elicited.

A substantial proportion of this workload is repetitive. Password and access problems, VPN and network connectivity faults, endpoint performance degradation, and peripheral or driver failures recur continuously, and the resolutions to much of this work already exist within the organization's own records. The problem is therefore not primarily one of missing knowledge but of the cost of locating, interpreting and applying existing knowledge on every recurrence.

**This reading is supported by direct measurement rather than assumption.** In the largest field study of generative AI in a support setting conducted to date, Brynjolfsson, Li and Raymond observed the staggered rollout of a generative-AI conversational assistant to **5,172 customer support agents** and measured an increase in productivity, defined as issues resolved per hour, of approximately **15% on average** [3]. Three features of that result matter for this research.

First, the effect was strongly heterogeneous: less experienced and lower-skilled workers improved in both speed and quality, while the most skilled agents gained little in speed [3]. The authors attribute this to the diffusion of *tacit knowledge* — the working practice of high performers becoming accessible to everyone else. The improvement is therefore an improvement in **knowledge access**, not in generative fluency, which confirms from the opposite direction the constraint that ITSM research identifies from the process side [1].

Second, the largest gains occurred for problems of moderate rarity — those where the individual agent lacked personal experience but adequate precedent existed in the system [3]. This is precisely the profile of the recurrent-but-not-trivial incident that dominates enterprise support queues.

Third, and most importantly, the assistant that produced these gains **recommended; it did not act**. The measured 15% represents the value of better advice delivered to a human who must still perform the work. Whether that residual work can itself be automated, and under what conditions it would be safe to do so, is the question this research investigates.

### 1.2.2 Current Automation Approaches and Where They Stop

The academic response to the repetitiveness of support work has, for the most part, taken the form of supervised classification applied to the ticket record.

Oliveira, Nogueira and Brito compare six supervised algorithms for classifying IT incident tickets using text mining and natural language processing, across Portuguese, Spanish and English ticket datasets. A linear support vector classifier achieved **93.12% accuracy** on their Portuguese corpus, ahead of stochastic gradient descent (90.01%), logistic regression (88.65%) and multinomial naïve Bayes (85.03%), with k-nearest neighbours and random forest performing worst [4]. Two of their secondary findings matter more than the headline figure: oversampling materially improved results, and the smaller Spanish and English datasets, to which oversampling was not applied, performed appreciably worse [4]. Automated ticket categorization is therefore substantially achievable, but its accuracy is contingent on corpus size and on explicit treatment of class imbalance rather than being an intrinsic property of the method.

Related work extends supervised learning from categorization to timing. Mulyati et al. show that predicting incident resolution time improves substantially when features are aggregated across the incident lifecycle rather than taken at ticket-open time alone: their lifecycle-aggregated model attains **R² = 0.8318** with a mean absolute error of 60.67 hours, against **R² = 0.5412** for the non-aggregated configuration, with process-derived features such as system modification count, assignment group and reassignment frequency proving far more predictive than the attributes available when the ticket was first raised [5].

**The structural limitation shared by this body of work is that the model is a terminal artefact.** A ticket is classified, or a duration is predicted, and the process ends. The classifier does not participate in diagnosis, does not consult resolution knowledge, and does not act. Reported accuracies, however high, are consequently not evidence that support automation is solved; they measure a sub-task that sits upstream of the work a support engineer actually performs. A second implication follows from [5] specifically: if lifecycle-aggregated features are required for good resolution-time prediction, then a predictor detached from the conversational process that generates the lifecycle has structurally limited access to its own strongest signal.

### 1.2.3 The Technological Opportunity

Three developments make the end-to-end problem newly tractable. Each is accompanied by a documented limitation that constrains how it can responsibly be used, and it is the pairing of capability with limitation that shapes the design proposed in this research.

**Large Language Models.** Contemporary LLMs demonstrate multi-step reasoning and sustained instruction-following, capabilities that emerge above certain parameter scales and are further shaped by adaptation tuning [6]. The property that matters for IT support is *conditional adaptation*: selecting the next diagnostic step from the reported outcome of the previous one. A fixed decision tree cannot do this beyond the branches its author anticipated; a model that reasons over accumulated dialogue state can. The corresponding weakness is equally well documented — fluent generation of confident but factually incorrect content, together with knowledge staleness and untraceable reasoning [6].

**Retrieval Augmented Generation.** RAG conditions generation on documents retrieved from a trusted corpus, pairing the model's parametric knowledge with an explicit non-parametric memory that can be inspected and updated without retraining [7]. The approach has since matured into a substantial design space of retrieval, ranking and integration strategies, organized by Gao et al. into naïve, advanced and modular paradigms and motivated explicitly by hallucination, knowledge staleness and untraceable reasoning [8]. Its retrieval component rests on dense representation learning: dual-encoder passage retrieval trained from limited question–passage supervision substantially outperforms sparse lexical baselines on top-k retrieval accuracy [9], and siamese sentence-embedding networks make large-scale semantic similarity computationally tractable by permitting passages to be encoded independently and compared by cosine distance [10]. This matters concretely in IT support, where a user writes "my internet keeps dropping" and the relevant article is titled "Wireless adapter power management configuration" — a match that lexical search cannot make.

Applied to this domain specifically, Toro Isaza et al. construct an incident-resolution recommendation system combining RAG-based answer generation with an encoder-only classifier and a generative query-formulation stage, designed explicitly around two enterprise constraints: incomplete domain coverage of the knowledge base, and restricted model size where organizations decline larger proprietary models on cost and privacy grounds [11]. Xu et al., working on a production customer-service ticket corpus, demonstrate that conventional RAG treats past tickets as flat text and thereby discards intra-issue structure and inter-issue relations, and that preserving that structure improves both retrieval and downstream answer quality [12].

**Multi-Agent Systems.** Rather than a single model performing every function, the agentic paradigm decomposes a task across specialized components that reason, act, observe the outcome and iterate. The ReAct formulation established that interleaving reasoning traces with actions allows a model to induce, track and revise plans while interfacing with external sources, with observation feedback closing the loop [13]. Wang et al. survey LLM-based autonomous agents and formalize their construction around profiling, memory, planning and action [14], while Liu et al. survey 124 studies applying LLM-based agents across software engineering activities, documenting both the breadth of adoption and the reliability, evaluation and cost challenges that remain open [15]. For the present research the decomposition matters for governance as much as for capability: it creates explicit, nameable boundaries at which policy can be enforced and at which each component can be tested independently.

### 1.2.4 Why the Problem Remains Unsolved

Despite these advancements, a significant gap persists between the theoretical capabilities of AI-driven automation and their practical application in enterprise IT support environments. The evidence for this statement is measured rather than asserted.

The clearest measurement comes from ITBench, a benchmark of 102 real-world IT automation scenarios spanning site reliability engineering, compliance and security operations, and financial operations. Agents built on state-of-the-art models resolve **11.4% of SRE scenarios**, **25.2% of compliance and security-operations scenarios** and **25.8% of financial-operations scenarios**, with anomaly-detection tasks reaching an F1 of only 0.35 [16]. These are not marginal shortfalls to be closed by a larger model; they indicate that *composing* capable components into a system that reliably completes realistic IT work is itself an unsolved problem.

Domain-specific studies converge on the same picture closer to the support desk. Ahmed et al. evaluate large language models for recommending root causes and mitigation steps for cloud incidents at industrial scale and find meaningful assistance but performance short of autonomous reliability [17]. Chen et al.'s RCACopilot — a production on-call system that matches an incident to a handler and aggregates critical runtime diagnostic information *before* invoking the model — reports root-cause categorization accuracy of **up to 0.766** over a year of real production incidents [18]. A system correct roughly three times in four is a valuable assistant and an unacceptable autonomous actor, and the distance between those two roles is where this research is situated. The architectural lesson from [18] is directly applicable and is adopted in the proposed design: the model performs better when invoked over *assembled context* than over a raw problem description, which is the same principle that motivates retrieval grounding.

Field-level synthesis reaches the same conclusion from the opposite direction. Zhang et al.'s survey of AIOps in the era of large language models analyzes 183 articles published between January 2020 and December 2024 and documents rapid expansion of LLM application across failure-management tasks alongside fragmented architectures, uneven data practices and inconsistent evaluation methodology [19]. The field is producing systems faster than it is producing comparable evidence about them.

**A recent development sharpens the research opportunity rather than removing it.** VIGIL, an edge-extended agentic system for enterprise IT support, deploys desktop-resident agents that perform situated diagnosis, retrieval over enterprise knowledge and **policy-governed remediation on user devices with explicit consent** and end-to-end observability. A ten-week pilot on 100 resource-constrained endpoints reports a **39% reduction in interaction rounds**, at least **fourfold faster diagnosis**, and **self-service resolution in 82% of matched cases**, together with favourable usability, trust and cognitive-workload results across four validated instruments [2].

This result is important to the present research in two ways, and both are accepted here rather than minimized. It confirms that consent-gated, knowledge-grounded remediation on user devices is a viable and valuable design direction, so the design premise of this research is supported by evidence rather than assumed. It equally confirms that the direction remains **under-characterized**: the reported gains are attributed to the system as a whole, and no decomposition establishes which architectural components produce the effect. The paper's own observation that users rated the system *higher* when no historical knowledge-base match was available [2] illustrates the point directly — the relationship between retrieval and perceived value is evidently not straightforward and cannot be inferred from an aggregate outcome. Furthermore, no adversarial evaluation of the governance layer is published, so the conditions under which consent-gated remediation holds against deliberate manipulation remain uncharacterized.

### 1.2.5 The Safety Dimension of an Acting System

Any support system that executes commands on user machines consumes untrusted input by construction — user prose, pasted logs, error text, uploaded screenshots — and is therefore exposed to prompt injection. This exposure is not speculative, and it bears directly on the "safe system remediation" component of the proposed research.

Greshake et al. established that adversarial instructions need not originate with the user at all: content *retrieved* by an LLM-integrated application can itself carry the attack. This **indirect** injection vector applies to any system that performs retrieval over a corpus it does not fully control, and the authors demonstrate compromise of real deployed applications [20]. Liu et al. establish the empirical breadth of the exposure: applying a black-box injection technique to **36 real-world LLM-integrated applications, 31 were found vulnerable**, with ten vendors subsequently confirming the findings [21].

Where a model is permitted to call tools, the exposure changes character from an information risk to an execution risk. AgentDojo, an evaluation environment populated with **97 realistic tool-using tasks and 629 security test cases**, finds that existing attacks break some security properties while existing defences close some but not all, and observes that language models lack a formal mechanism for distinguishing instructions from data [22]. ToolEmu makes the complementary methodological point that identifying such risks by hand does not scale: using an LM-emulated sandbox over 36 high-stakes toolkits and 144 test cases, its authors find that **68.8% of the failures it surfaces are judged by human evaluators to be valid real-world agent failures**, and that even the safest agent evaluated fails 23.9% of the time [23].

Read together, these four results support a design conclusion that this research adopts explicitly, and which justifies the human-in-the-loop control already stated in the research question: **safety controls that depend on the model's compliance are not safety controls**, because the model is the component under attack. A defence expressed as a system-prompt instruction is a string in the model's context, indistinguishable in kind from an injected string [22]. A defence expressed as an enumerated action whitelist enforced in application code is categorically different, because no manipulation of the model expands the set of operations the application is capable of executing. This is why the proposed Action Executor Agent is bounded by a whitelist, parameter validation and mandatory user approval enforced outside the model, rather than by instructing the model to behave safely.

---

## 1.3 Problem Statement

### 1.3.1 General Problem

Enterprise IT support operations face an escalating challenge of efficiency, scalability and user satisfaction. The problem is twofold and structural.

First, the volume and complexity of IT support requests continue to grow, driven by the proliferation of remote and hybrid work, bring-your-own-device policies, cloud migration and increasingly sophisticated software ecosystems, producing precisely the heterogeneous, long-tail environment that recent work identifies as difficult to resolve centrally [2]. Support capacity, meanwhile, is bounded by the number of trained engineers an organization can employ and retain. The two quantities do not scale together, and the gap between them is absorbed as queuing delay, deferred resolution and displaced staff productivity.

Second, the repetitive and knowledge-intensive nature of IT troubleshooting means that a significant proportion of support tickets involve previously encountered issues whose solutions already exist within organizational knowledge bases but are costly to locate, interpret and apply on each recurrence [1]. That this is the binding constraint is supported by direct measurement: when support agents were given an assistant that made the working practice of high performers accessible, throughput rose approximately 15%, and the effect concentrated among the least experienced agents — the distributional signature expected if the limiting factor is access to knowledge the organization already holds [3].

Automation attempts to date address this only partially, and they fall short at opposite ends of the same axis. Systems restricted to information retrieval are safe but shallow: they terminate at a recommendation the user must still carry out, leaving the residual manual effort untouched. Systems that extend into action-taking are useful but are not accompanied, in the published literature, by governance evidence sufficient to justify confident deployment. The measured resolution rates on realistic IT tasks — 11.4% of SRE scenarios for agents built on state-of-the-art models [16] — indicate that the deficiency is **architectural rather than merely a matter of model capability**, since the same models perform considerably better on isolated reasoning tasks than on composed operational ones.

This combination of rising demand, constrained supply and untapped organizational knowledge produces a compounding inefficiency that degrades productivity, increases operational cost, and burdens IT support teams with repetitive workloads.

### 1.3.2 Specific Problems

Within the ITSM domain, six specific shortcomings persist that current solutions fail to adequately address.

**Lack of Intelligent Conversation Understanding.** Existing IT support chatbots largely employ keyword matching or intent-classification models that cannot sustain multi-turn, context-aware troubleshooting dialogue. They fail to reliably distinguish technical from non-technical queries, miss urgency signals, and cannot adapt their troubleshooting approach based on conversational feedback. The capability actually required is conditional reasoning over accumulated dialogue state — selecting the next diagnostic action from the reported outcome of the previous one [6], [13] — which is a different capability from intent lookup against a fixed taxonomy.

**Absence of Knowledge Grounded Reasoning.** Conventional chatbot systems generate responses without grounding them in organization-specific knowledge, producing guidance that is plausible in general but inappropriate for the specific organization: referencing tools it does not use, procedures it does not follow, or configurations it does not have. Retrieval grounding is the established mitigation [7], [8], and domain-specific implementations demonstrate its value for IT incident resolution under realistic enterprise constraints [11], [12]. However, the literature predominantly evaluates *retrieval and answer quality*; the contribution of grounding to *end-to-end resolution outcomes* within a complete support pipeline is rarely isolated and measured [11], [12].

**Manual and Static Ticket Management.** Ticket creation, classification, prioritization and assignment remain predominantly manual or governed by static rules that do not account for agent specialization, workload balance, or the nuanced context of the reported issue. Supervised approaches to ticket classification [4] and resolution-time prediction [5] have been studied, but as standalone models detached from the conversational process that generates the ticket. In the resolution-time case the detachment carries a measurable cost, since features available at ticket-open time are demonstrably the weakest configuration [5].

**No Autonomous Remediation Capability.** Current IT support systems function predominantly as information retrieval tools: they can suggest solutions but cannot execute diagnostic or remediation actions on the user's system, even for safe, well-defined operations such as clearing temporary files, flushing DNS caches or restarting Windows services. Closing this gap requires executing commands on user systems, which introduces genuine security exposure through direct and indirect prompt injection [20], [21], [22]. Where the gap has been closed in practice, it has been closed under policy governance and explicit consent [2], which confirms both the viability of the approach and the necessity of the governance.

**Fragmented Agent Architecture.** Existing solutions lack a cohesive multi-agent architecture in which specialized agents collaboratively handle distinct aspects of the support workflow — conversation management, ticket intelligence, action execution, image analysis and status tracking — resulting in monolithic, inflexible systems. Agent decomposition patterns are well established in the general literature [13], [14], [15], but their benefit has not been empirically isolated within an ITSM setting, and integrated systems in this domain report aggregate outcomes rather than per-component contributions [2].

**Insufficient Predictive and Proactive Capabilities.** Most IT support systems are purely reactive, responding only after issues are reported. They lack predictive components for resolution-time and SLA-risk estimation and for system-health monitoring. Predictive modelling of incident resolution time is demonstrably feasible, but the literature shows it is sensitive to feature specification, with lifecycle-aggregated features substantially outperforming those available at ticket creation [5] — a finding that a system integrating prediction with the conversational process is better positioned to exploit than a standalone predictor.

### 1.3.3 Research Gap

Despite the rapid advancement of LLMs, RAG architectures and multi-agent systems, these paradigms have largely been developed and evaluated in isolation from one another. Ticket classification and resolution-time prediction are studied as terminal artefacts [4], [5]; retrieval grounding is evaluated on retrieval and answer quality rather than resolution outcomes [11], [12]; LLM incident diagnosis stops at recommendation and reaches at best 0.766 accuracy in production [17], [18]; agent decomposition is well theorized but not empirically isolated in this domain [13], [14], [15]; and the safety obligations of an acting system are documented as principles without being instantiated and tested inside a domain support system [20]–[23]. Field-level surveys characterize the resulting picture as fragmented and inconsistently evaluated [19], and benchmark evidence confirms that the composed task remains largely unachieved [16].

> **Statement of the research gap.** There exists no *openly documented and independently evaluable* integrated IT support platform that combines LLM-driven conversational intelligence with RAG-based knowledge retrieval, autonomous but human-gated system remediation, intelligent multi-agent ticket management, visual analysis of error screenshots, and predictive analytics within a unified, secure and auditable framework. This research aims to bridge this gap.

**Justification for the wording of this gap.** Interim Submission 01 stated that *no* comprehensive integrated IT support platform of this kind exists. That claim cannot be sustained: VIGIL reports an industrial pilot of an integrated system combining situated diagnosis, retrieval over enterprise knowledge and consent-governed remediation on user devices [2], and commercial ITSM platforms combine conversational AI with ticket automation. The gap is therefore restated in the narrower and defensible form above. The restatement does not change the research direction, the proposed system or the objectives; it changes only what is claimed to be absent. What the literature genuinely lacks is an integrated architecture that is *published at a level permitting inspection, reimplementation and independent evaluation*, and whose components can therefore be assessed individually rather than only as an aggregate — which is exactly what [2] does not provide and what [19] identifies as a field-level deficiency. Making a smaller claim that the evidence supports is academically stronger than making a larger one that a reviewer can refute with a single citation.

---

## 1.4 Research Question

**Primary Research Question**

> *"How can a multi-agent AI system leveraging Large Language Models (LLMs) and Retrieval Augmented Generation (RAG) be designed and implemented to autonomously handle end-to-end IT support operations — including intelligent conversation management, knowledge-grounded troubleshooting, automated ticket lifecycle management, safe system remediation, and predictive analytics — while maintaining security, auditability, and human-in-the-loop control?"*

The question is design-oriented, which is appropriate to a Design Science Research study whose primary output is an artefact together with knowledge about it. Its empirical component is supplied by the fourth objective (§1.7.4), which requires the constructed system to be evaluated rather than merely demonstrated. The clause "while maintaining security, auditability, and human-in-the-loop control" is not a qualification but a substantive constraint, and §1.2.5 establishes why: an acting system faces demonstrated adversarial exposure [20]–[23], so a design that satisfies the first part of the question without the second would not answer it.

**Sub-Questions**

| # | Sub-question | Grounding in the reviewed evidence |
|---|---|---|
| **1** | How can LLM-powered conversational agents effectively classify, understand and respond to diverse IT support queries through natural, multi-turn dialogue? | Conditional multi-step reasoning is a documented LLM capability [6], [13]; classical supervised classification of IT tickets provides a published comparison point [4] |
| **2** | How can Retrieval Augmented Generation be employed to ground AI-generated troubleshooting advice in organization-specific knowledge bases, thereby improving accuracy and reducing hallucination? | RAG pairs parametric knowledge with an inspectable non-parametric memory [7], [8]; domain implementations exist for IT support [11], [12] but are evaluated on retrieval quality rather than resolution outcome |
| **3** | How can a multi-agent architecture be designed to orchestrate specialized agents for conversation management, ticket intelligence, action execution, image analysis and status tracking within a cohesive IT support workflow? | Agent construction and reasoning–action interleaving are established [13], [14], [15], but the benefit of decomposition is not empirically isolated in ITSM [2], [19] |
| **4** | How can autonomous system remediation actions be safely executed with appropriate user consent, risk assessment and comprehensive audit logging? | Direct and indirect prompt injection against tool-using applications is demonstrated and practical [20], [21], [22], [23]; consent-governed remediation is shown to be viable in a production pilot [2] |
| **5** | How can machine learning models be integrated to predict SLA/resolution-time risk and system health, enabling proactive IT support operations? | Resolution-time prediction is feasible but strongly sensitive to feature specification [5]; ticket-level supervised modelling is mature [4] |

---

## 1.5 Research Motivation

**Personal experience with IT support inefficiencies.** Through firsthand observation in organizational IT environments, it was apparent that support teams spend a disproportionate amount of time on repetitive issues — password resets, VPN connectivity problems, software configuration errors — that appear amenable to intelligent automation. This observation prompted the investigation into how contemporary AI technologies could change the IT support paradigm.

**Demonstrated, measured impact of AI assistance in support work.** The motivation for this research does not rest on the observation alone. A field study across 5,172 support agents measured an approximately 15% increase in issues resolved per hour when a generative assistant was introduced, with gains concentrated among less experienced workers and attributed to the diffusion of tacit knowledge [3]. This establishes that improving knowledge access in support work has real and quantified value, and it does so from a system that only advised. The question this research pursues is what architecture delivers that value most effectively and how far it can be extended from advice into action.

**Evidence that the problem is not already solved.** The 11.4% SRE resolution rate reported for agents built on state-of-the-art models [16], and the ceiling of 0.766 root-cause categorization accuracy reached by a production system over a year of real incidents [18], together show that applying current models to IT operations does not by itself produce competent automation. Architectural research is therefore warranted rather than redundant.

**The promise of RAG for domain-specific knowledge.** The ability of retrieval augmentation to combine the generative capability of LLMs with grounding in curated organizational knowledge addresses the hallucination risk that makes unconstrained generation inadmissible in a domain where an incorrect instruction may be executed on a working machine [7], [8]. Domain-specific implementations for IT support demonstrate that this is practical under real enterprise constraints of knowledge coverage and model size [11], [12].

**The multi-agent systems paradigm.** The growing body of research on LLM-based agents [13], [14], [15] motivates the exploration of a collaborative architecture in which specialized agents, each responsible for a distinct aspect of the support workflow, orchestrate an end-to-end support process. Decomposition additionally creates explicit boundaries at which governance can be enforced and at which each component can be tested independently — a property that a monolithic implementation cannot offer.

**Bridging the theory–practice gap.** While academic research on LLMs, RAG and multi-agent systems is abundant, openly documented implementations that integrate these technologies into a coherent IT support platform remain scarce, and the closest published system reports aggregate outcomes without decomposing them [2]. Field-level surveys identify this fragmentation and inconsistent evaluation as a systemic problem [19]. This research is motivated by the opportunity to produce an openly documented, inspectable architecture at a scale appropriate to an undergraduate thesis.

---

## 1.6 Research Aim

> The aim of this research is to design, develop and evaluate an intelligent, multi-agent IT support system (**Auto-Ops-AI**) that leverages Large Language Models (LLMs) and Retrieval Augmented Generation (RAG) to automate end-to-end IT support operations — encompassing conversational issue understanding, knowledge-grounded troubleshooting, intelligent ticket lifecycle management, human-approved system remediation, visual error analysis and predictive analytics — within a secure, auditable and human-in-the-loop framework, and to demonstrate its effect on resolution time, support efficiency and user satisfaction **relative to a matched manual baseline evaluated under the same conditions**.

**Justification for the final clause.** Interim Submission 01 expressed this aim as demonstrating improvement "compared to conventional IT support approaches," with §3.4 proposing that published industry figures for L1 resolution time serve as the comparative benchmark. That comparison is not defensible: the population, the ticket mix, the organizational context and the measurement definition all differ from those of the evaluation, and no adjustment available at this scale would make them commensurable. A favourable comparison against such a figure would therefore be evidence of nothing. The aim is accordingly restated so that the comparison is internal — the same scenarios, the same scoring criteria, the same timing protocol, with system assistance as the manipulated variable. This preserves the intent of the original aim, which is to establish that the system improves on manual support, while making the resulting claim one the study can actually substantiate.

---

## 1.7 Research Objectives

### 1.7.1 To Identify

To identify the key challenges, limitations and inefficiencies in existing IT support systems and chatbot-based support tools through a comprehensive literature review, thereby establishing the requirements for an intelligent, multi-agent AI-driven IT support platform.

*Verifiable outcome:* a comparative analysis of existing approaches — supervised ITSM machine learning [4], [5], LLM-based incident diagnosis [17], [18], retrieval-augmented support [11], [12], and integrated agentic IT support [2] — stating for each what was done, what was found, what limits the finding, and what remains unresolved.

### 1.7.2 To Analyze

To analyze the capabilities and architectural patterns of Large Language Models, Retrieval Augmented Generation and multi-agent systems in the context of IT service management, evaluating their suitability for conversational troubleshooting, knowledge-grounded response generation, intelligent ticket management and human-approved remediation, together with their documented failure modes.

*Verifiable outcome:* a technological analysis at the algorithmic [6], [7], [8], [9], [10], design [13], [14], [15], [20]–[23] and workflow levels, each strand terminating in an explicitly justified design decision for the proposed system.

### 1.7.3 To Design and Develop

To design and develop a comprehensive multi-agent IT support system (**Auto-Ops-AI**) comprising five specialized AI agents:

- **LLM Conversation Agent** — natural language understanding, contextual dialogue management and intelligent response generation;
- **Ticket Intelligence Agent** — automated ticket creation, priority analysis, metadata generation and resolution detection;
- **Action Executor Agent** — safe, permission-based execution of diagnostic and remediation actions on user systems;
- **Image Analysis Agent** — visual analysis of error screenshots, device photographs and technical images using multimodal AI;
- **Ticket Status Agent** — ticket lifecycle transitions, SLA tracking, escalation detection and auto-closure;

integrated with RAG-based knowledge retrieval over a vector store, role-based access control (RBAC), and a modern React-based frontend dashboard.

*Verifiable outcome:* an operational system in which each of the five agents is implemented as a discrete, independently exercisable module invoked within the request pipeline, with remediation constrained by an enumerated action whitelist and a mandatory user-approval gate enforced in application code rather than by model instruction [20]–[23].

### 1.7.4 To Evaluate

To evaluate the developed system's performance through quantitative metrics (ticket resolution time, classification accuracy, resolution-time/SLA prediction accuracy, RAG retrieval relevance) and qualitative measures (user satisfaction, system usability, troubleshooting effectiveness), comparing results against a matched manual baseline conducted on the same scenarios, in order to validate the system's efficacy and identify areas for improvement.

*Verifiable outcome:* measured results on a defined scenario set with human-authored ground truth, reported alongside the conditions under which they were obtained. Classification performance is compared against a published supervised baseline for IT incident tickets [4]; retrieval relevance is reported separately from end-to-end resolution outcomes, following the distinction that [11] and [12] leave unresolved; and the safety of the remediation pathway is tested rather than assumed, given the demonstrated practicality of direct and indirect injection against tool-using applications [20], [21], [22].

---

## 1.8 Rich Picture of the Proposed Solution

The proposed **Auto-Ops-AI** system employs a multi-agent architecture in which five specialized AI agents collaborate through an orchestration layer to deliver end-to-end IT support automation.

### 1.8.1 System Architecture Overview

```
┌───────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                           │
│   Chat UI (Text/Img)  │  Dashboard  │  Ticket Manager  │  Admin Panel │
└──────────────────────────────┬────────────────────────────────────────┘
                               │  REST / JSON
┌──────────────────────────────▼────────────────────────────────────────┐
│           BACKEND API (FastAPI) — Authentication (JWT + RBAC)         │
├───────────────────────────────────────────────────────────────────────┤
│                      AGENT ORCHESTRATION LAYER                        │
│                                                                       │
│   ┌────────────────────┐ ┌────────────────────┐ ┌──────────────────┐  │
│   │ LLM Conversation   │ │ Ticket Intelligence│ │ Action Executor  │  │
│   │ Agent              │ │ Agent              │ │ Agent            │  │
│   │  · classify        │ │  · create          │ │  · whitelisted   │  │
│   │  · respond         │ │  · prioritize      │ │    actions only  │  │
│   │  · escalate        │ │  · categorize      │ │  · risk tiering  │  │
│   │  · context         │ │  · resolve         │ │  · USER APPROVAL │  │
│   └────────────────────┘ └────────────────────┘ └──────────────────┘  │
│                                                                       │
│   ┌────────────────────┐ ┌────────────────────┐                       │
│   │ Image Analysis     │ │ Ticket Status      │                       │
│   │ Agent              │ │ Agent              │                       │
│   │  · OCR / vision    │ │  · lifecycle       │                       │
│   │  · categorize      │ │  · SLA track       │                       │
│   │  · keywords → RAG  │ │  · auto-close      │                       │
│   └────────────────────┘ └────────────────────┘                       │
├───────────────────────────────────────────────────────────────────────┤
│  RAG Engine          │  Assignment / Dataset  │  PowerShell Engine    │
│  (vector store +     │  Analyzer              │  (subprocess, no      │
│   embeddings)        │  (semantic similarity) │   shell interpreter)  │
├───────────────────────────────────────────────────────────────────────┤
│  DATA LAYER: Knowledge Base (JSON) │ Vector Store │ SQLite (tickets,  │
│              users, roles)         │              │ Audit Logs        │
├───────────────────────────────────────────────────────────────────────┤
│  ML MODELS LAYER: Resolution-time / SLA-risk model │ System Health    │
│                   model │ Category Encoder                            │
└───────────────────────────────────────────────────────────────────────┘
```

### 1.8.2 Key Workflow: End-to-End IT Support Conversation

```
   User Message (text and/or screenshot)
              │
              ▼
   [Image Analysis Agent]  ── if an image is attached, its description is
              │                merged into the textual message so that image-
              ▼                originated requests follow the same path as text
   [LLM Conversation Agent] ── classify · understand
              │
              ├──── not technical ─────────────► casual/conversational response
              │
              ▼ technical
   [RAG Engine] ── semantic search over the organizational knowledge base
              │
              ▼
   [LLM Conversation Agent] ── grounded multi-turn troubleshooting dialogue
              │
              ▼
   [Ticket Intelligence Agent] ── create ticket · score urgency · categorize
              │
              ▼
   [Action Executor Agent] ── propose remediation from the whitelist,
              │                with its risk tier
              ▼
   ⛔ USER APPROVAL REQUIRED ⛔  ── nothing executes before explicit,
              │                     logged approval by the requesting user
              ▼
   Execute → report result → audit log
              │
              ▼
   [Ticket Status Agent] ── track · close or escalate to a human agent
```

**Rationale for the approval gate.** The gate is positioned as the last step before execution and is enforced in application code rather than by prompting the model, for the reason established in §1.2.5: an instruction expressed in the model's context can be overridden by an injected instruction in the same context [22], whereas the set of operations the application will execute cannot be extended by anything the model outputs [20], [21]. This is what makes "human-in-the-loop control" in the research question a testable property rather than a stated intention.

### 1.8.3 The Five Specialized Agents and Their Roles

| Agent | Responsibility | Key Technologies |
|---|---|---|
| **LLM Conversation Agent** | Natural language understanding; multi-turn dialogue management; message classification (technical / general / greeting); contextual response generation; escalation detection | Hosted LLM (Google Gemini); prompt engineering; conversation memory window |
| **Ticket Intelligence Agent** | Intelligent ticket creation timing; priority analysis (urgency scoring 0–10); LLM-powered title and description generation; category classification; resolution detection | Hosted LLM; hybrid rule-based and LLM logic |
| **Action Executor Agent** | Whitelisted system action management; parameter validation; user permission workflow; PowerShell command execution; follow-up action suggestion | Enumerated action whitelist with risk tiering; parameter sanitization; PowerShell via subprocess without shell interpretation |
| **Image Analysis Agent** | Visual analysis of error screenshots and device photographs; text extraction; issue categorization from images; keyword extraction for RAG search | Multimodal LLM (Gemini Vision) |
| **Ticket Status Agent** | Ticket lifecycle management (OPEN → IN PROGRESS → RESOLVED → CLOSED); resolution detection; re-open detection; SLA tracking; auto-closure; abandonment detection | Rule-based state machine; SLA algorithms |

**Rationale for a heterogeneous agent design.** The five agents are deliberately not uniform in implementation: three are generative, one is a hybrid of generative and rule-based logic, and the Ticket Status Agent is a deterministic state machine. This follows a single principle — generative where interpretation of unconstrained user language is required, deterministic where accountability is required. Lifecycle state governs SLA accounting and audit records, and an auditor asking why a ticket moved from OPEN to RESOLVED requires a reconstruction of the reasoning, which deterministic rules can provide by re-execution and a generative justification cannot.

**Rationale for multimodal input.** Users describe faults poorly in prose but capture them accurately in screenshots: an error dialogue, a stop code or a network status panel carries diagnostic information that free-text paraphrase loses. Multimodal LLM-based fault detection and diagnosis has been demonstrated in industrial fault-diagnosis settings [24], and the transfer to end-user IT support is direct. The Image Analysis Agent's output is merged into the textual message and passed through the same classification and retrieval path as ordinary text, so that no separate, less-validated decision path exists for image-originated requests.

---

## 1.9 Resource Requirements

### 1.9.1 Hardware Requirements

| Resource | Minimum Specification | Recommended Specification |
|---|---|---|
| Processor | Intel Core i5 (8th Gen) or equivalent | Intel Core i7 (10th Gen) or AMD Ryzen 7 |
| RAM | 8 GB DDR4 | 16 GB DDR4 |
| Storage | 256 GB SSD (50 GB free) | 512 GB SSD (100 GB free) |
| Network | Stable internet connection (5 Mbps) | Broadband connection (25+ Mbps) |
| GPU | Not required (cloud-based AI inference) | NVIDIA GPU (optional, for local model hosting) |
| Test environment | One isolated Windows virtual machine with snapshot capability | Two virtual machines |

*Justification for the network requirement:* every generative and embedding call is a network round trip, so link quality directly affects the latency measurements required by objective 1.7.4. *Justification for the test environment:* remediation actions mutate system state, so evaluation trials require restoration to a uniform baseline between runs if resolution-time measurements are to be comparable.

### 1.9.2 Software Requirements

| Category | Software / Tool | Version | Purpose |
|---|---|---|---|
| Programming language | Python | 3.11+ | Backend development, AI/ML |
| Runtime | Node.js | 18+ | Frontend development |
| Backend framework | FastAPI | Latest | REST API development |
| Frontend framework | React | 19 | User interface |
| Build tool | Vite | 7 | Frontend build and dev server |
| LLM provider | Google Gemini API | Version recorded with all results | Natural language processing, vision |
| Vector database | ChromaDB | Latest | RAG knowledge retrieval |
| Relational database | SQLite | 3.x | Ticket, user and audit data |
| ORM | SQLAlchemy | Latest | Database abstraction |
| Embedding model | Google `text-embedding-004` | Latest | Semantic similarity search |
| ML libraries | scikit-learn, NumPy, Pandas | Latest | Predictive models, data analysis |
| Command execution | Windows PowerShell via subprocess (no shell interpretation) | — | Remediation action execution |
| Containerization | Docker + Docker Compose | Latest | Deployment and environment management |
| Authentication | JWT (PyJWT) + bcrypt | Latest | Secure user authentication |
| Version control | Git + GitHub | Latest | Source code management |
| IDE | Visual Studio Code | Latest | Development environment |
| API testing | Swagger UI (built-in) | Auto-generated | API documentation and testing |
| Operating system | Windows 10/11 | Latest | Development and deployment |

*Justification for recording the model version:* results conditioned on an unrecorded hosted-model version are not reproducible, since a silent provider-side update would appear in the data as an unexplained change in system behaviour.

---

## 1.10 Project Scope

The following table delineates the boundaries of this research by distinguishing capabilities that are within scope from those that are outside it. Several exclusions remove capability the system could technically support; in each case the justification is that including it would either confound a measured comparison or add engineering surface without addressing a stated problem.

| Aspect | In Scope | Out of Scope | Justification for the boundary |
|---|---|---|---|
| **Conversational AI** | Multi-turn, context-aware IT support dialogue using a hosted LLM, with conversation memory management and intelligent escalation detection | Integration with third-party communication platforms (Slack, Microsoft Teams, WhatsApp) | Channel integration is engineering surface, not research surface; it would not alter any measured outcome |
| **Knowledge retrieval** | RAG-based knowledge base search using a vector store with semantic similarity matching over curated organizational IT knowledge | Real-time web crawling or external internet search | The research claim concerns grounding in *organizational* knowledge [11], [12]; open-web retrieval would introduce an uncontrolled second knowledge source |
| **Input modalities** | Text queries; image upload and analysis (screenshots, error photographs) via a multimodal LLM | Voice input processing, video analysis, real-time screen sharing | Multimodal fault description is demonstrated in the literature [24] and inexpensive to support; video adds cost without addressing a stated problem |
| **Ticket management** | Automated ticket creation, intelligent prioritization (urgency scoring), LLM-powered categorization, smart agent assignment based on specialization and workload | Integration with external ITSM platforms (ServiceNow, Jira Service Management, Zendesk) | Integration would make lifecycle behaviour depend on an external system's rules, preventing attribution of observed behaviour to the proposed design |
| **System remediation** | Whitelisted, risk-tiered diagnostic and remediation actions on Windows systems (process management, cleanup, network diagnostics, service management) under a mandatory user-approval workflow | Cross-platform remediation (macOS, Linux), destructive system operations, remote machine access | Destructive operations are excluded on ethical grounds; single-platform scope is a stated limitation of the study |
| **Multi-agent system** | Five specialized AI agents (Conversation, Ticket Intelligence, Action Executor, Image Analysis, Ticket Status) under coordinated orchestration | Self-evolving agent capabilities, agent-to-agent negotiation, dynamic agent creation | Deterministic orchestration is required if repeated trials of the same scenario are to be comparable; autonomous negotiation would make them non-comparable |
| **Security and access control** | Role-based access control across five roles, JWT authentication, comprehensive audit logging, and testing of the remediation pathway against adversarial input | Single Sign-On, OAuth2 federation, Active Directory integration, MFA | Enterprise identity federation is a deployment concern that does not bear on the safety property being tested [20]–[23] |
| **Predictive analytics** | Resolution-time and SLA-risk estimation; system-health prediction | Advanced anomaly detection, real-time predictive maintenance, capacity planning | Retained as specified in Interim 01; feature specification follows the lifecycle-aggregation finding of [5] |
| **User interface** | React-based dashboard with dark mode, ticket management views, analytics reports, admin panel, real-time monitoring | Native mobile applications (iOS/Android), Progressive Web App features | Interface breadth does not affect any measured outcome |
| **Deployment** | Docker containerization, single-server deployment configuration | Kubernetes orchestration, multi-region deployment, high-availability clustering, cloud-native auto-scaling | Reproducible single-node deployment is sufficient for the evaluation and supports independent reimplementation |
| **Data** | Curated synthetic/representative enterprise IT support dataset comprising user profiles, knowledge base articles, and historical tickets with conversations | Real production data from live enterprise environments | No ethically available route exists to production support transcripts at this scale; synthetic scenarios additionally permit a defined ground truth that real transcripts would not |
| **Evaluation** | System performance metrics (resolution time, accuracy, RAG relevance) and usability assessment, against a matched manual baseline | Large-scale longitudinal studies, A/B testing in production, cross-organizational benchmarking | Out of reach at undergraduate scale; the resulting external-validity limitation is stated rather than concealed |

---

## 1.11 Significance of the Research

**Academic significance.** The reviewed literature supplies the components of this problem in isolation — ticket classification [4], resolution-time prediction [5], retrieval grounding [7]–[12], agent construction [13], [14], [15] — or an integrated outcome reported in aggregate without decomposition [2], within a field that surveys characterize as fragmented and inconsistently evaluated [19]. Infrastructure-tier benchmarks such as [16] measure agent performance on operations tasks but do not cover the conversational support tier at which most end-user support interactions occur. An openly documented integrated architecture for that tier, with its evaluation methodology stated, addresses a documented deficiency rather than an assumed one.

**Practical significance.** Organizations that cannot procure enterprise ITSM AI platforms currently have no documented reference design to build against, because commercial platforms are not inspectable and industrial pilots report outcomes rather than architectures [2]. The governance arrangement specified in §1.8.2 — enumerated action whitelist, parameter validation, risk tiering, and mandatory user approval enforced outside the model — is transferable to any system that permits a language model to act, independently of the IT support domain.

**Methodological significance.** Two decisions in the evaluation design address validity threats that recur in this literature. Retrieval relevance is reported separately from end-to-end resolution outcomes, rather than the first being treated as a proxy for the second, which is the distinction that [11] and [12] leave unresolved. And the human comparison uses a matched internal baseline on the same scenarios rather than an externally published average, which removes population and measurement-definition differences as confounds (§1.6).

**Limitation of the contribution, stated explicitly.** This research does not claim to introduce a previously non-existent category of system, and does not claim to outperform commercial platforms or the industrial pilot reported in [2]. Its claim is narrower and defensible: to produce an openly documented, inspectable and independently evaluable integrated architecture for AI-driven IT support, at a scale that permits reimplementation.

---

## 1.12 Chapter Summary

This introductory chapter has established the foundational context for the research on **Auto-Ops-AI**, an intelligent multi-agent IT support system. The problem background established the ITSM context and identified the binding constraint as the cost of accessing and applying knowledge the organization already holds — a reading supported both by ITSM process research documenting knowledge-asset maintenance as a persistent challenge [1] and by field measurement showing that assistance improving knowledge access raised support productivity by approximately 15% across 5,172 agents, with gains concentrated among the least experienced [3]. It then established that existing academic automation treats classification and prediction as terminal artefacts detached from diagnosis and action [4], [5]; that the enabling technologies — LLM reasoning [6], retrieval grounding [7]–[12] and agent decomposition [13], [14], [15] — are individually mature; and that the composed task nonetheless remains largely unachieved, resolving only 11.4% of realistic SRE scenarios at benchmark level [16] and reaching at best 0.766 root-cause accuracy in production [18], within a field characterized as fragmented and inconsistently evaluated [19]. It further established that any system permitted to act on user machines faces demonstrated adversarial exposure through direct and indirect prompt injection [20]–[23], which is why the proposed design places its safety controls outside the language model.

The problem statement identified the general organizational problem of demand outgrowing constrained support capacity while resolution knowledge remains costly to apply, together with six domain-specific shortcomings: the lack of intelligent conversation understanding, the absence of knowledge-grounded reasoning, manual and static ticket management, the absence of remediation capability, fragmented agent architecture, and insufficient predictive capability. The research gap was stated in the form the evidence supports — the absence of an *openly documented and independently evaluable* integrated platform combining these capabilities — with the reasons for narrowing the original formulation set out explicitly in §1.3.3.

The research question was formulated to address how a multi-agent AI system leveraging LLMs and RAG can be designed and implemented to handle end-to-end IT support operations while maintaining security, auditability and human-in-the-loop control, supported by five sub-questions each grounded in the reviewed evidence. The research motivation drew on direct observation, measured evidence of impact [3], measured evidence that the problem is unsolved [16], [18], the promise of retrieval grounding [7], [8], [11], [12], the multi-agent paradigm [13], [14], [15], and the need to bridge the theory–practice gap [2], [19]. Four objectives — to identify, analyze, design and develop, and evaluate — structure the investigative pathway, each stated with a verifiable outcome.

A rich picture illustrated the proposed multi-agent architecture comprising the five specialized agents, supported by a RAG engine, dataset analyzer, ML prediction models and a React-based frontend, with the human approval gate positioned as the final control before any action executes. Resource requirements, a scope delineation with a justification for each boundary, and a statement of the significance and limits of the contribution complete the foundation.

The subsequent chapters present the literature review (Chapter 2), the methodology (Chapter 3), implementation details (Chapter 4), evaluation and results (Chapter 5), and conclusions with future work (Chapter 6).

---

## 1.13 Record of Changes Relative to Interim Submission 01

This section is provided for supervisory review and is not intended for inclusion in the final thesis body.

### 1.13.1 Retained without change

| Element | Status |
|---|---|
| Research title | Retained verbatim |
| Chapter structure §1.1–§1.10 and §1.12 (Chapter Summary) | Retained; §1.11 Significance added (see 1.13.4) |
| Primary research question and all five sub-questions | Retained; sub-question 5 reworded only to match the corrected predictive scope (see 1.13.3) |
| Four research objectives (identify / analyze / design and develop / evaluate) | Retained verbatim in substance |
| The five specialized agents and their responsibilities | Retained verbatim |
| System architecture, workflow, and the user-approval step | Retained |
| Six specific problems in §1.3.2 | Retained, all six, with the same headings |
| Project scope table (all rows and in/out classifications) | Retained |
| Hardware requirements table | Retained |
| Research motivation items | Retained (one re-based, see 1.13.3) |

### 1.13.2 Improved and justified

| Element | What was improved |
|---|---|
| §1.2 Problem Background | Reorganized into five subsections producing an explicit progression: ITSM context → current approaches and where they stop → technological opportunity → why the problem remains unsolved → the safety dimension. No content was removed except unverifiable statistics (see 1.13.3) |
| Every specific problem in §1.3.2 | Each is now supported by a paper that genuinely evidences it, with the mechanism stated rather than asserted |
| §1.2.3 | The LLM / RAG / MAS discussion now states, for each technology, both the capability and its documented limitation, so that the design decisions in §1.8 follow from the analysis rather than preceding it |
| §1.8 | Rationales added for the approval gate, the heterogeneous agent design, and multimodal input, each tied to the evidence in §1.2 |
| §1.7 objectives | Each objective now carries a verifiable outcome, so that completion can be assessed rather than asserted |
| §1.9 | Justifications added for the network and test-environment requirements and for recording the model version |
| §1.10 | A justification column was added to the scope table, so that each exclusion is reasoned rather than merely listed |
| §1.2.5 (new) | The security and human-in-the-loop clause of the research question is now evidenced, rather than appearing only as a stated intention |

### 1.13.3 Corrected, with justification

| # | Interim 01 statement | Correction and reason |
|---|---|---|
| 1 | Market-size figures (ITSM market USD 14.5 bn → 22 bn), the 24.2-hour L1 resolution time and "40% of time on repetitive issues", the USD 1.55 trillion downtime cost, the 67%/52% employee survey figures, the 6% growth and 43% unfilled-position figures, and the "75% of ITSM interactions AI-augmented by 2027" projection | **Removed.** These come from vendor, analyst and industry-survey sources whose methodology is not published and which cannot be independently verified. The underlying arguments they supported — demand outgrowing capacity, repetitive workload, the value of AI assistance — are retained and re-based on peer-reviewed measurement [1], [2], [3], [16] |
| 2 | Citations to Ahmad et al. (2023), Xu et al. (2023) "Conversational AI for IT Support", Patel & Singh (2023), Kumar & Mehta (2024), and Li et al. (2024) "Multi-Agent Systems for Enterprise AI" | **Removed.** These could not be located in any bibliographic database. Each claim they supported has been re-grounded on a verified paper from your supplied set: conversational limitations → [6], [13]; ticket routing and management → [4], [5]; autonomous remediation → [2], [20]–[23]; multi-agent architecture → [13], [14], [15]; predictive analytics → [5] |
| 3 | Research gap: "there exists **no** comprehensive, integrated IT support platform that combines…" | **Narrowed** to the absence of an *openly documented and independently evaluable* such platform. VIGIL reports exactly such an integrated system in an industrial pilot [2], so the original claim is refutable by a single citation. The research direction, proposed system and objectives are unchanged; only the claim of absence is corrected. Justified in full at §1.3.3 |
| 4 | Research aim: "…compared to conventional IT support approaches", with §3.4 of Interim 01 proposing published L1 resolution times as the benchmark | **Restated** as comparison against a matched manual baseline on the same scenarios. Populations, ticket mixes and measurement definitions differ between the published figure and this evaluation, so the original comparison could not support the conclusion it was intended to support. The intent of the aim is preserved. Justified at §1.6 |
| 5 | Action Executor Agent: "50+ safe operations"; scope table: "50+ whitelisted actions" | **Replaced** with an unquantified description of the enumerated whitelist. Source verification recorded in Revision 3 of Interim 01 established 25 active action definitions; the higher figure appears to have counted commented-out and duplicated entries. A count is best stated in the implementation chapter where it can be evidenced |
| 6 | Software requirements: "AI Orchestration — LangChain" | **Removed.** Source verification recorded in Revision 3 established that LangChain is not in the runtime request path. Listing a dependency that is not used is a factual error in a requirements table |
| 7 | Software requirements: React 18 | **Updated** to React 19 / Vite 7, matching the verified implementation |
| 8 | RBAC: "5 roles: Admin, Manager, Support L2, Support L1, Staff" | **Generalized** to "five roles". The verified role constants differ from the names listed; naming them incorrectly in Chapter 1 would conflict with the implementation chapter |
| 9 | Data scope: "200 users, knowledge base articles, historical tickets" | **Generalized** to a curated synthetic dataset without the specific figure, which was not realized in the constructed corpus |
| 10 | Predictive analytics: "SLA breach risk prediction (**Random Forest**)" | **Generalized** to resolution-time and SLA-risk estimation without naming the algorithm, since the algorithm is an implementation choice belonging to Chapter 4 and the trained artefact differs from the one named |
| 11 | §1.7.3: "RAG based knowledge retrieval (ChromaDB)" | **Generalized** to "RAG-based knowledge retrieval over a vector store". The objective states design intent; naming a specific product in an objective ties the objective to an implementation detail |
| 12 | Citation style: author–date in text, IEEE-numbered reference list | **Unified** to IEEE numeric throughout, matching the numbered reference list already used in Interim 01 |

### 1.13.4 Added

| Element | Justification |
|---|---|
| §1.2.5 The Safety Dimension of an Acting System | The research question already commits to "security, auditability, and human-in-the-loop control" and specific problem 4 already concerns remediation. Interim 01 asserted these without evidence. This subsection evidences them from the supplied papers [20]–[23]. It introduces no new research direction |
| §1.11 Significance of the Research | Requested as part of the required progression. Its content is drawn entirely from material already present in Interim 01 — principally the "bridging the theory–practice gap" motivation — plus the openness argument already implicit in the research gap |
| Verifiable outcomes under each objective; justification column in the scope table; rationale paragraphs in §1.8 | Presentational strengthening only; no scope, objective or system element was changed |

### 1.13.5 Papers supplied but not cited in Chapter 1

Three of the supplied papers are not cited here because they support material belonging to later chapters, and citing them in Chapter 1 would not be genuine support: **RAGAs** (evaluation methodology for RAG pipelines — belongs to the evaluation design), and the **AIOps preprint version** of [19] (superseded by the peer-reviewed version cited). Introducing them here purely to raise the citation count would breach the requirement that every citation genuinely supports the statement it is attached to.

---

## References

Cited in Chapter 1 only. All entries were verified against the publisher record; the local file supplied with this research is identified for each.

[1] J. Serrano, J. Faustino, D. Adriano, R. Pereira, and M. M. da Silva, "An IT service management literature review: Challenges, benefits, opportunities and implementation practices," *Information*, vol. 12, no. 3, art. 111, 2021, doi: 10.3390/info12030111.
*Supplied file:* `An IT Service Management Literature Review.pdf`

[2] S. Ahuja, N. Kordjazi, E. Yortucboylu, V. Kapoor, M. Dundua, Y. Li, D. Ho, V. Padala, J. Whitted, and R. Steinert, "VIGIL: Towards edge-extended agentic AI for enterprise IT support," *arXiv preprint* arXiv:2603.16110, 2026.
*Supplied file:* `VIGIL Towards Edge-Extended Agentic AI for Enterprise IT Support.pdf`

[3] E. Brynjolfsson, D. Li, and L. R. Raymond, "Generative AI at work," *The Quarterly Journal of Economics*, vol. 140, no. 2, pp. 889–942, 2025, doi: 10.1093/qje/qjae044.
*Supplied file:* `Generative AI at work.pdf`

[4] D. F. Oliveira, A. S. Nogueira, and M. A. Brito, "Performance comparison of machine learning algorithms in classifying information technologies incident tickets," *AI*, vol. 3, no. 3, pp. 601–622, 2022, doi: 10.3390/ai3030035.
*Supplied file:* `Performance Comparison of Machine Learning Algorithms in Classifying Information Technologies Incident Tickets.pdf`

[5] Mulyati, D. Stiawan, A. Rahman, M. S. Shakkah, and R. Budiarto, "Predicting incident resolution time in IT service management via lifecycle feature aggregation and machine learning," *Ingénierie des Systèmes d'Information*, vol. 31, no. 2, pp. 511–519, 2026, doi: 10.18280/isi.310219.
*Supplied file:* `Predicting Incident Resolution Time in IT Service Management via Lifecycle Feature Aggregation and Machine Learning.pdf`

[6] W. X. Zhao, K. Zhou, J. Li, T. Tang, X. Wang, Y. Hou, et al., "A survey of large language models," *Frontiers of Computer Science*, vol. 20, no. 12, art. 2012627, 2026, doi: 10.1007/s11704-026-60308-3.
*Supplied file:* `A Survey of Large Language Models.pdf` (arXiv:2303.18223 author version of the same work)

[7] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, "Retrieval-augmented generation for knowledge-intensive NLP tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, 2020, pp. 9459–9474.
*Supplied file:* `Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.pdf`

[8] Y. Gao, Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, Y. Dai, J. Sun, M. Wang, and H. Wang, "Retrieval-augmented generation for large language models: A survey," *arXiv preprint* arXiv:2312.10997, 2024.
*Supplied file:* `Retrieval-Augmented Generation for Large Language Models A Survey.pdf`

[9] V. Karpukhin, B. Oğuz, S. Min, P. Lewis, L. Wu, S. Edunov, D. Chen, and W. Yih, "Dense passage retrieval for open-domain question answering," in *Proc. 2020 Conf. Empirical Methods in Natural Language Processing (EMNLP)*, 2020, pp. 6769–6781, doi: 10.18653/v1/2020.emnlp-main.550.
*Supplied file:* `Dense Passage Retrieval for Open-Domain Question Answering.pdf`

[10] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using siamese BERT-networks," in *Proc. 2019 Conf. Empirical Methods in Natural Language Processing and 9th Int. Joint Conf. Natural Language Processing (EMNLP-IJCNLP)*, Hong Kong, China, 2019, pp. 3982–3992, doi: 10.18653/v1/D19-1410.
*Supplied file:* `Sentence-BERT Sentence Embeddings using Siamese BERT-Networks.pdf`

[11] P. Toro Isaza, M. Nidd, N. Zheutlin, J.-W. Ahn, C. A. Bhatt, Y. Deng, R. Mahindru, M. Franz, H. Florian, and S. Roukos, "Retrieval augmented generation-based incident resolution recommendation system for IT support," *arXiv preprint* arXiv:2409.13707, 2024.
*Supplied file:* `Retrieval Augmented Generation-Based Incident Resolution Recommendation System for IT Support.pdf`

[12] Z. Xu, M. J. Cruz, M. Guevara, T. Wang, M. Deshpande, X. Wang, and Z. Li, "Retrieval-augmented generation with knowledge graphs for customer service question answering," in *Proc. 47th Int. ACM SIGIR Conf. Research and Development in Information Retrieval (SIGIR '24)*, Washington, DC, USA, 2024, pp. 2905–2909, doi: 10.1145/3626772.3661370.
*Supplied file:* `Retrieval-Augmented Generation with Knowledge Graphs for Customer Service Question Answering.pdf`

[13] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, "ReAct: Synergizing reasoning and acting in language models," in *Proc. Int. Conf. Learning Representations (ICLR)*, 2023.
*Supplied file:* `Synergizing Reasoning and Acting in Language Models.pdf`

[14] L. Wang, C. Ma, X. Feng, Z. Zhang, H. Yang, J. Zhang, Z.-Y. Chen, J. Tang, X. Chen, Y. Lin, W. X. Zhao, Z. Wei, and J.-R. Wen, "A survey on large language model based autonomous agents," *Frontiers of Computer Science*, vol. 18, no. 6, art. 186345, 2024, doi: 10.1007/s11704-024-40231-1.
*Supplied file:* `A Survey on Large Language Model Based Autonomous Agents.pdf`

[15] J. Liu, K. Wang, Y. Chen, X. Peng, Z. Chen, L. Zhang, and Y. Lou, "Large language model-based agents for software engineering: A survey," *ACM Transactions on Software Engineering and Methodology*, 2025, doi: 10.1145/3796507.
*Supplied file:* `Large Language Model-Based Agents for Software Engineering A Survey.pdf`

[16] S. Jha, R. R. Arora, Y. Watanabe, T. Yanagawa, Y. Chen, J. Clark, et al., "ITBench: Evaluating AI agents across diverse real-world IT automation tasks," in *Proc. 42nd Int. Conf. Machine Learning (ICML)*, PMLR, vol. 267, 2025, pp. 27134–27197.
*Supplied file:* `ITBench Evaluating AI Agents across Diverse Real-World IT Automation Tasks.pdf`

[17] T. Ahmed, S. Ghosh, C. Bansal, T. Zimmermann, X. Zhang, and S. Rajmohan, "Recommending root-cause and mitigation steps for cloud incidents using large language models," in *Proc. IEEE/ACM 45th Int. Conf. Software Engineering (ICSE)*, Melbourne, Australia, 2023, pp. 1737–1749, doi: 10.1109/ICSE48619.2023.00149.
*Supplied file:* `Recommending Root-Cause and Mitigation Steps for Cloud Incidents using Large Language Models.pdf`

[18] Y. Chen, H. Xie, M. Ma, Y. Kang, X. Gao, L. Shi, Y. Cao, X. Gao, H. Fan, M. Wen, J. Zeng, S. Ghosh, X. Zhang, C. Zhang, Q. Lin, S. Rajmohan, D. Zhang, and T. Xu, "Automatic root cause analysis via large language models for cloud incidents," in *Proc. 19th European Conf. Computer Systems (EuroSys '24)*, Athens, Greece, 2024, pp. 674–688, doi: 10.1145/3627703.3629553.
*Supplied file:* `rcacopilot_paper.pdf`

[19] L. Zhang, T. Jia, M. Jia, Y. Wu, A. Liu, Y. Yang, Z. Wu, X. Hu, P. S. Yu, and Y. Li, "A survey of AIOps in the era of large language models," *ACM Computing Surveys*, 2025, doi: 10.1145/3746635.
*Supplied file:* `A Survey of AIOps in the Era of Large Language Models.pdf`

[20] K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz, "Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection," in *Proc. 16th ACM Workshop on Artificial Intelligence and Security (AISec '23)*, Copenhagen, Denmark, 2023, pp. 79–90, doi: 10.1145/3605764.3623985.
*Supplied file:* `Not What You've Signed Up For Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection.pdf`

[21] Y. Liu, G. Deng, Y. Li, K. Wang, Z. Wang, X. Wang, T. Zhang, Y. Liu, H. Wang, Y. Zheng, L. Y. Zhang, and Y. Liu, "Prompt injection attack against LLM-integrated applications," *arXiv preprint* arXiv:2306.05499, 2023.
*Supplied file:* `Prompt Injection Attack against LLM-Integrated Applications.pdf`

[22] E. Debenedetti, J. Zhang, M. Balunović, L. Beurer-Kellner, M. Fischer, and F. Tramèr, "AgentDojo: A dynamic environment to evaluate prompt injection attacks and defenses for LLM agents," in *Advances in Neural Information Processing Systems (NeurIPS) Datasets and Benchmarks Track*, vol. 37, 2024.
*Supplied file:* `AgentDojo- A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents.pdf`

[23] Y. Ruan, H. Dong, A. Wang, S. Pitis, Y. Zhou, J. Ba, Y. Dubois, C. J. Maddison, and T. Hashimoto, "Identifying the risks of LM agents with an LM-emulated sandbox," in *Proc. Int. Conf. Learning Representations (ICLR)*, 2024.
*Supplied file:* `Identifying the Risks of LM Agents with an LM-Emulated Sandbox.pdf`

[24] K. M. Alsaif, A. A. Albeshri, M. A. Khemakhem, and F. E. Eassa, "Multimodal large language model-based fault detection and diagnosis in context of Industry 4.0," *Electronics*, vol. 13, no. 24, art. 4912, 2024, doi: 10.3390/electronics13244912.
*Supplied file:* `Multimodal Large Language Model-Based Fault Detection and Diagnosis in Context of Industry 4.0.pdf`
