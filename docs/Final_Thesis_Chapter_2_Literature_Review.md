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
