# Context-Aware Intelligent IT Support Systems: A Multi-Agent Framework with Predictive Issue Detection and Automated Resolution

> **ICACT 2026 submission draft — v2 (document-grounded).**
> Source: *Interim Submission 01* (P. T. N. Pathirana, 28647), Chapters 1–3.
> Transfer into `conference template/conference-template-a4.docx` (IEEE A4, two-column).
> Blocks marked **[INFORMATION NEEDED]** correspond to material your documents do not yet contain
> (Chapters 4–6 are listed there as forthcoming). Do not submit until they are filled.

---

## Author Block

**If double-blind (UNCONFIRMED — verify on CMT):** omit this block; replace self-reference with "the authors."

**Otherwise:**

```
A. P. T. Nethumini Pathirana
Faculty of Computing
NSBM Green University
Homagama, Sri Lanka
[INFORMATION NEEDED: institutional email or ORCID]
```

> **[INFORMATION NEEDED]** Supervisor / co-author names and affiliations, if to be listed.

---

## Abstract

*(276 words — within the 300-word ICACT limit)*

Enterprise IT service management is confronting a scalability deficit. Ticket volume and infrastructure
complexity continue to rise while the supply of skilled support personnel remains constrained, and a
substantial proportion of incoming requests restate problems the organisation has already documented and
solved. Existing responses address only part of this. Traditional tiered ticketing platforms function as
digital ledgers: they record and route work through largely static rules that cannot weigh issue context,
agent specialisation or real-time workload. First-generation support chatbots improve intake but rely on
intent classification that degrades during multi-turn, context-dependent diagnosis, and terminates at a
recommendation the user must still carry out.

This paper proposes Auto-Ops-AI, a context-aware multi-agent framework that addresses both limitations
within a single architecture. Five specialised agents — conversation, ticket intelligence, action
execution, image analysis and ticket status — collaborate through an orchestration layer to cover the
support lifecycle from initial message to ticket closure. Troubleshooting responses are grounded in an
organisational knowledge base through retrieval-augmented generation, constraining generated advice to
documented procedures. Remediation is performed by a dedicated execution agent restricted to a whitelist
of non-destructive operations, each requiring explicit and logged user approval. Decoupling the
conversational agent from the executing agent establishes a privilege boundary: a component that
processes untrusted user text holds no capability to act on the host.

The research adopts a pragmatist philosophy operationalised through Design Science Research, combining
abductive architectural formulation with deductive hypothesis testing, and is executed as applied system
development with experimental evaluation in a simulated enterprise environment.
**[INFORMATION NEEDED — evaluation outcomes.]** The intended contribution is an integrated framework
demonstrating that knowledge-grounded reasoning and bounded autonomous remediation can be combined
under human-in-the-loop control.

**Keywords**—multi-agent systems, retrieval-augmented generation, IT service management, large language
models, autonomous remediation

*(5 keywords — at the ICACT maximum)*

---

## I. Introduction

### A. Background

The information technology support landscape has changed substantially over the past decade. The
digitalisation of workplace operations, accelerated by the shift to remote and hybrid working, has left
organisations managing heterogeneous ecosystems that span cloud services, on-premises infrastructure,
diverse endpoint devices and complex software stacks. Industry analysis places the global IT service
management (ITSM) market on a trajectory exceeding USD 22 billion by 2028, reflecting how far
organisational function now depends on IT infrastructure [13].

Conventional IT support rests on manual ticketing workflows, static knowledge bases and tiered human
escalation (L1 → L2 → L3). A user encountering a malfunctioning VPN connection, a degraded laptop or a
recurring system crash submits a ticket, waits in a queue, and is eventually attended by support staff
who search knowledge bases and perform diagnostic steps sequentially. Reported industry figures place
average L1 resolution at 24.2 hours, with support staff spending approximately 40% of their time on
repetitive, previously resolved issues [14].

### B. Problem Statement

The general problem is a compounding inefficiency arising from three simultaneous pressures. First,
request volume and complexity continue to grow, driven by remote work, bring-your-own-device policies
and cloud migration. Second, the supply of qualified support personnel remains constrained. Third, and
most consequentially, much of the knowledge required to resolve incoming tickets already exists within
organisational records but is difficult to locate and apply efficiently. The result degrades
productivity, raises operating cost and contributes to support-team burnout. Unplanned IT downtime has
been estimated to cost large enterprises on the order of USD 1.55 trillion annually [15].

Within the ITSM domain specifically, several shortcomings persist that current solutions do not
adequately address:

- **Limited conversational understanding.** Deployed support chatbots depend on keyword matching or
  intent classification and cannot sustain multi-turn, context-aware diagnostic dialogue. They fail to
  distinguish technical from non-technical queries, miss urgency signals, and cannot adapt their line of
  questioning in response to user feedback.
- **Absence of knowledge-grounded reasoning.** Responses are generated without conditioning on
  organisation-specific knowledge, producing generic suggestions that do not exploit documented
  solutions from past incidents.
- **Manual and static ticket management.** Creation, classification, prioritisation and assignment
  remain largely manual. Where automation exists, it is rule-based routing that disregards agent
  specialisation, workload balance and issue context.
- **No autonomous remediation.** Current systems are information-retrieval tools. They can describe a
  remedy but cannot apply it, even for safe and well-defined operations such as clearing temporary
  files or flushing a DNS cache.
- **Fragmented architecture.** Solutions lack a cohesive multi-agent design in which specialised agents
  handle distinct aspects of the workflow, yielding monolithic and inflexible systems.
- **Insufficient predictive capability.** Systems are reactive, responding only after issues are
  reported, without models for SLA breach risk or system health.

### C. Research Question and Objectives

The research is directed by a single primary question:

> *How can a multi-agent AI system leveraging large language models (LLMs) and retrieval-augmented
> generation (RAG) be designed and implemented to autonomously handle end-to-end IT support operations —
> including conversation management, knowledge-grounded troubleshooting, automated ticket lifecycle
> management, safe system remediation and predictive analytics — while maintaining security,
> auditability and human-in-the-loop control?*

This decomposes into five sub-questions concerning, respectively: LLM-driven classification and
multi-turn response; RAG-based grounding of troubleshooting advice in organisational knowledge; agent
orchestration across conversation, ticket intelligence, execution, image analysis and status tracking;
safe execution of remediation under user consent, risk assessment and audit logging; and integration of
machine-learning models for SLA and system-health prediction.

Four objectives structure the investigation: to **identify** the limitations of existing IT support
systems and establish requirements; to **analyse** the architectural patterns of LLMs, RAG and
multi-agent systems for suitability in ITSM; to **design and develop** the proposed five-agent framework;
and to **evaluate** it against quantitative and qualitative measures.

### D. Contributions

1. An integrated multi-agent architecture for ITSM combining conversational intelligence,
   retrieval-grounded troubleshooting, ticket lifecycle automation, multimodal error analysis and
   predictive analytics within one framework.
2. A privilege-separated remediation design in which the agent processing untrusted user input is
   structurally distinct from the agent permitted to execute, with execution confined to a whitelist of
   non-destructive operations under mandatory logged user approval.
3. A Design Science Research treatment of the problem, in which the artefact is evaluated against the
   ITSM bottlenecks it is designed to remediate.

Section II reviews related work and establishes the research gap. Section III describes the research
methodology. Section IV presents the proposed framework. Section V specifies the evaluation design.
Sections VI and VII discuss and conclude.

---

## II. Related Work

### A. Domain Overview

The operational reality of ITSM remains constrained by inefficiencies that infrastructure investment
alone does not resolve. The reported concentration of support effort on repetitive issues [14],
alongside the scale of downtime cost [15], indicates that the binding constraint is not a technological
deficit in infrastructure but a **scalability deficit in human-driven support**. The volume of routine
work absorbs skilled practitioners, which motivates a shift from manual, reactive support toward
intelligent and proactive automation.

### B. Existing Systems and Frameworks

Enterprise responses to this constraint fall into two established categories.

**Traditional ticketing and routing systems.** In platforms of this class, creation, classification and
routing remain largely manual or governed by static rules. Where NLP-based routing has been introduced,
it does not dynamically account for real-time agent workload, nuanced issue context or specialised
expertise [16]. Such systems act as digital ledgers rather than active problem solvers: a static routing
rule cannot distinguish the urgency of an executive's locked account from a routine software request. A
purely reactive ticketing layer therefore constitutes a bottleneck that dynamic, LLM-driven ticket
intelligence must replace.

**First-generation IT chatbots.** Deployed conversational agents in ITSM rely predominantly on intent
classification. They perform adequately at deflecting basic queries such as password-reset requests, but
fail during multi-turn, context-dependent troubleshooting, frequently looping through generic scripts.
Two limitations are decisive: they cannot execute actions, and they cannot ground their reasoning in
dynamic organisational context. Conversational interfaces must therefore evolve from rigid decision trees
into reasoning components that maintain context, adapt to feedback, and hand off to execution modules
rather than returning documentation links.

### C. Technological Analysis

**Algorithmic.** Large language models exhibit strong zero-shot reasoning and multi-step logical
capability [3], but are prone to hallucination — the generation of plausible yet factually incorrect
output. Retrieval-augmented generation addresses this by mapping queries into a vector space, retrieving
semantically matching passages from a trusted corpus, and conditioning generation on that retrieved
evidence [1], [2]. Dense retrieval methods provide the underlying similarity techniques [11], [12].
Supervised models have been applied to service-management prediction tasks such as resolution-time
estimation.

For IT support the algorithmic conclusion is stronger than it is in general question answering.
Unconstrained LLMs are unsuitable where an incorrect remediation step can damage a user system.
Retrieval grounding is therefore not an enhancement but a precondition: constraining generation to an
organisationally approved context bounds generative variance and is what makes the advice actionable.

**Design.** System design has moved from monolithic models toward multi-agent systems, in which
specialised autonomous agents interact to decompose complex problems [4], [7], [8]. In an ITSM setting
this decomposition carries a security rationale beyond capability. If one model both converses with users
and emits system commands, it is exposed to prompt injection — adversarial content within pasted logs or
error text becomes an instruction [9], [10]. Because IT support consumes untrusted input by construction,
decoupling the conversation agent from the action executor introduces a necessary layer of
privilege-based security: an executor bound by whitelists and approval protocols can refuse a dangerous
command irrespective of what the conversational component produced.

**Workflow.** Current ITSM workflows are fragmented. A user talks to a bot, the bot creates a ticket, a
human reads it, a human executes a fix, and a human closes it. Few systems permit AI-initiated
remediation on end-user machines, chiefly on risk grounds [5], [6]. The resulting deficiency is the
**action gap**: systems can explain *how* to fix an issue but cannot fix it. A complete workflow closes
the loop — understand the issue, retrieve the documented solution, request user permission, execute the
approved operation, and close or escalate the ticket. Anything short of this is partial automation.

### D. Research Gap

These strands have largely been studied in isolation. LLM research addresses natural-language capability
[3]; RAG research addresses factual grounding [1], [2]; multi-agent research addresses decomposition and
scalability [4], [7], [8]; and LLM security research prescribes least privilege and human confirmation
as principles [9], [10] without instantiating them in a domain system.

> **The gap:** there is no unified framework that integrates LLM-driven conversation, RAG-backed
> knowledge retrieval, multimodal image analysis, predictive monitoring and — most critically — secure
> agentic remediation into a single cohesive IT support platform.

Existing frameworks are either safe but incapable, as with traditional chatbots, or capable but unsafe,
as with unbounded LLMs. Auto-Ops-AI addresses the gap by synthesising these technologies under a
multi-agent architecture in which generative capability is tethered by retrieval grounding and policed
by a specialised execution agent, extending intelligence across the workflow from initial user message
to autonomous closure.

---

## III. Research Methodology

### A. Paradigm

The research adopts a **pragmatist** philosophy. Pragmatism is concerned with action, practical
consequence and what works to resolve real problems; truth is assessed by the practical efficacy of the
solution rather than by correspondence to an observed phenomenon alone. Since the problem under
investigation is an operational crisis of efficiency and scalability in ITSM, the research does not
merely observe the phenomenon but intervenes in it.

This philosophy is operationalised through **Design Science Research (DSR)**, which is directed at the
construction and evaluation of a novel IT artefact — here, the multi-agent architecture integrating
LLMs, retrieval grounding and execution agents. Analysis is accordingly focused on whether the designed
system effectively and safely remediates the identified bottlenecks relative to existing frameworks.

### B. Approach and Strategy

A mixed **abductive–deductive** approach is used. Abductive reasoning is applied first: observing the
action gap in existing systems, the most plausible architectural response is inferred to be a multi-agent
system decoupled into conversational and execution layers. Deductive reasoning follows: from the
literature, testable propositions are derived — that retrieval grounding reduces hallucination, and that
multi-agent decoupling permits safe autonomous execution — which are then empirically examined.

The strategy is **applied system development (prototyping) with experimental evaluation**. Rather than
theoretical analysis or observational case study, the framework is engineered and then subjected to
synthetic IT support scenarios — network failures, software crashes, access requests — in a controlled,
simulated enterprise environment, measuring resolution efficiency and safety against baseline metrics.

### C. Data Collection

A mixed-methods strategy gathers primary and secondary data.

*Primary.* **System performance logs** provide quantitative measures captured automatically during
experimental testing: ticket resolution time, classification accuracy, retrieval relevance and system
latency. **User feedback surveys** using Likert-scale instruments collect qualitative measures of
satisfaction, perceived usability and conversational naturalness from test users.

*Secondary.* **Literature and industry reports** supply baseline metrics for conventional L1 resolution
as a comparative benchmark. A **synthetic IT support dataset** comprising user profiles, historical
tickets and standard operating procedures populates the knowledge base.

> **⚠ CORRECTION REQUIRED.** The interim report specifies a synthetic dataset of 200 users. The dataset
> presently available comprises 5 user profiles, 5 tickets and 6 knowledge-base articles. State the
> actual figure in the paper, or generate the full dataset before submission. A corpus of this size will
> not support a credible retrieval evaluation and a reviewer will identify this.

### D. Execution Workflow

> **TABLE I** — DSR execution workflow.

| Phase | Aspect | Execution |
|---|---|---|
| 1 | Problem identification | Analysed the ITSM scalability crisis through literature review; established that manual L1/L2 support cannot scale with ticket growth and that rule-based chatbots lack the reasoning to resolve complex issues or act |
| 2 | Relevance justification | Quantified the problem through downtime cost and resolution-time benchmarks; established relevance to operating cost, employee productivity and support-staff burnout |
| 3 | Comparative analysis and gap | Compared monolithic LLM applications against multi-agent systems; identified the absence of an integrated, safe platform bridging the action gap |
| 4 | Objective definition | Finalised four objectives: identify challenges, analyse MAS/RAG capability, design and develop the framework, evaluate against baselines |
| 5 | Design and development | Architected the five-agent orchestration layer; managed relational and knowledge-base data across appropriate stores |
| 6 | Evaluation and communication | Experimental evaluation of resolution time, retrieval accuracy and prediction; communicated through this paper and prototype demonstration |

### E. Project Management and Ethics

Development follows **Agile Scrum**. The justification is that multi-agent AI development is subject to
rapid technological change — including revisions to model APIs and retrieval methods — which sequential
methodologies such as Waterfall accommodate poorly. Iterative sprints permit individual agents to be
developed and tested incrementally before integration into the orchestration layer.

Three ethical commitments govern a system capable of executing operations on user machines:

1. **Safety and non-maleficence.** The execution agent is restricted to a whitelist of non-destructive
   operations; destructive commands are programmatically blocked.
2. **Consent and transparency.** Users are informed that they are interacting with an AI system, and no
   remediation executes without explicit, logged approval.
3. **Data privacy.** Simulated ticket data and synthetic user profiles are anonymised, and role-based
   access control restricts audit-log visibility to authorised personnel.

---

## IV. Proposed System

### A. Architecture

Auto-Ops-AI is organised as a layered architecture. A web presentation layer provides chat, dashboard,
ticket management and administration interfaces. A REST API layer enforces authentication and role-based
access control. An **agent orchestration layer** coordinates the five specialised agents. A supporting
services layer provides retrieval, prioritisation, assignment and prediction, over a data layer holding
relational records, the vectorised knowledge base and audit logs.

> **FIGURE 1** — Layered system architecture. Adapt from the interim report (p. 9); **add an explicit
> privilege boundary** around the action executor, which the current diagram does not show.

### B. The Five Agents

> **TABLE II** — Agent responsibilities and privilege separation.

| Agent | Responsibility | Handles untrusted input | May execute on host |
|---|---|---|---|
| Conversation | Natural-language understanding, multi-turn dialogue, message classification, escalation detection | **Yes** | **No** |
| Ticket Intelligence | Creation timing, urgency scoring, title and description generation, categorisation, resolution detection | Yes | No |
| Image Analysis | Interpretation of error screenshots and device photographs, text extraction, keyword extraction for retrieval | **Yes** | No |
| Ticket Status | Lifecycle transitions, SLA tracking, re-open and abandonment detection, auto-closure | No | No |
| Action Executor | Whitelist management, parameter validation, approval workflow, execution, follow-up suggestion | **No** | **Yes** |

The asymmetry in the final two columns is the framework's principal design property. Every agent that
processes untrusted natural language is denied execution capability, and the sole agent holding that
capability does not accept free-form text. An instruction injected through pasted log content or an
uploaded screenshot therefore has no architectural path to the host.

### C. Knowledge-Grounded Troubleshooting

The user's problem description is embedded and compared by cosine similarity against embeddings of
knowledge-base articles. Articles exceeding a relevance threshold are ranked by a weighted combination
of semantic similarity and historical usage, so that procedures with an established resolution record
are preferred:

> **Equation (1):**
> score(*a*, *q*) = *w*₁ · cos(**e**_*q*, **e**_*a*) + *w*₂ · usage(*a*)

where **e**_*q* and **e**_*a* denote query and article embeddings and usage(*a*) is a normalised count
of tickets previously resolved by article *a*. The highest-ranked articles are supplied to the
conversation agent as grounding context, constraining generated advice to documented organisational
procedure.

### D. Ticket Intelligence

Priority is determined by a transparent additive scoring function over user tier, declared urgency,
urgency-bearing keywords in the description, category criticality, and the requester's support history
including unresolved prior tickets. The resulting score maps to a priority level by fixed thresholds.
Because each factor's contribution is returned alongside the score, a support manager can inspect why a
ticket was prioritised and contest any individual factor. This trades predictive ceiling for
auditability, which is the appropriate trade where prioritisation decisions are subject to review.

> **TABLE III** — Priority scoring factors and weights. **[INFORMATION NEEDED — transcribe exact weights
> and thresholds from the implementation.]**

### E. Bounded Autonomous Remediation

Remediation is the security-critical path and is designed as a closed system. Each permitted operation
is a static whitelist entry carrying an identifier, description, category, risk tier, a fixed command
template and a parameter specification with enumerated permissible values.

Execution proceeds in four stages: the user's intent is matched to a whitelist entry, so that the system
selects among pre-authorised operations rather than composing a command; supplied parameters are
validated against the specification and rejected if outside the permitted set; the operation, its risk
tier and its concrete effect are presented for explicit user approval; and on approval the operation
executes, with invocation, parameters, approving user and outcome written to the audit log.

> **FIGURE 2** — Remediation pipeline showing the approval gate and rejection paths.

Three properties follow structurally rather than behaviourally. The action space is **closed**: an
operation absent from the whitelist is unreachable, not merely discouraged. Parameter interpolation is
**bounded** by enumerated values. And **no state change occurs without a logged human decision**. None
of these depends on the language model behaving correctly, which is what makes the design defensible
under adversarial input.

### F. Predictive Components

Two supervised models supplement the rule-based logic: a classifier over host telemetry returning a
system-health state with an associated risk probability, and a regression model estimating resolution
time from ticket attributes. Both are advisory, informing prioritisation and escalation; neither gates
execution.

> **[INFORMATION NEEDED]** Training data provenance, dataset size, split protocol and validated accuracy
> for both models. The interim report describes SLA prediction as a Random Forest; the implemented
> component is a linear regression over resolution hours, while the Random Forest applies to host health.
> **Correct this before submission, or describe both as advisory components rather than evaluated
> contributions.**

### G. Scope

The framework addresses multi-turn context-aware support dialogue, retrieval over an organisational
knowledge base, text and image input, automated ticket creation and prioritisation, whitelisted
remediation on Windows endpoints, five-role access control with audit logging, SLA and system-health
prediction, and containerised single-server deployment.

Explicitly out of scope: integration with third-party communication platforms and external ITSM
suites; real-time web search; voice and video input; cross-platform and remote-machine remediation;
self-evolving or dynamically created agents; single sign-on and directory federation; native mobile
applications; orchestrated multi-region deployment; and evaluation against real production data from
live enterprise environments.

---

## V. Evaluation Design

> **[INFORMATION NEEDED — no evaluation outcomes exist in the provided documents.]**
> The interim report lists implementation, evaluation and conclusions as forthcoming chapters. The
> protocol below follows the measures its Objective 4 and Section 3.4 specify, and is the minimum
> required to support the contributions claimed in Section I.

Evaluation is conducted in a controlled simulated enterprise environment across five measures.

**E1 — Classification accuracy.** A labelled corpus of user messages spanning technical and non-technical
intents across system categories. Report accuracy, per-class precision and recall, and a confusion
matrix.

**E2 — Retrieval relevance.** Problem descriptions with known correct knowledge-base articles. Report
Precision@k, Recall@k and mean reciprocal rank at the operating threshold, with a threshold sweep to
justify the chosen cut-off.

**E3 — Prioritisation agreement.** An experienced practitioner independently assigns priority to a
ticket sample; report agreement with the scoring function using Cohen's κ, and analyse disagreements.

**E4 — Safety containment.** An adversarial suite attempting to induce destructive execution: direct
requests, indirect injection through pasted log content and uploaded screenshots, out-of-enumeration
parameter values, and template-escape attempts. Report containment rate and classify each failure by the
control that caught it. *This experiment tests the framework's central claim and no comparable system
reports it; it carries the highest value per hour invested.*

**E5 — End-to-end resolution.** Scripted scenarios executed end to end, reporting the proportion resolved
without human escalation and median time to resolution. **Compare against a within-system baseline** —
the same scenarios with the execution agent disabled — rather than against externally cited industry
figures, which is not a controlled comparison and will not survive review.

Qualitative evaluation follows Section III-C: Likert-scale instruments measuring satisfaction, perceived
usability and conversational naturalness.

**Reporting requirements.** State the model version and access date, since results are not reproducible
against a changing hosted API. Run each condition multiple times and report variance. Document all
hyperparameters.

---

## VI. Results

> **[INFORMATION NEEDED — no results exist in the provided documents.]**
>
> Required: Table IV (classification), Table V (retrieval), Table VI (safety containment — the headline
> result), Figure 3 (confusion matrix), Figure 4 (threshold sweep), Figure 5 (resolution time with and
> without the execution agent).
>
> The figures appearing in the project release notes (85% SLA prediction, 90% categorisation, 95%
> assignment, 60% API reduction) are **not supported by any artefact in the provided materials** and must
> not be reported as results unless regenerated and recorded under the protocol above.

---

## VII. Discussion

> **[Complete after results. Structure below.]**

**Interpretation.** State what the containment rate implies for the architectural claim. If containment
is high, attribute it to whitelist closure rather than model alignment — that is the transferable
finding.

**Threats to validity.**
- *Construct validity.* Scenarios drawn from the same knowledge base used for retrieval risk
  circularity; acknowledge explicitly.
- *External validity.* A synthetic dataset and small knowledge base do not represent enterprise scale.
  State the bound plainly; a reviewer will otherwise state it for you.
- *Reproducibility.* Results depend on a hosted model whose behaviour may change without notice.
- *Evaluator bias.* If labels and priority judgements derive from a single annotator, disclose it.

**Trade-offs.** The closed whitelist bounds risk but also bounds coverage: any issue whose remedy is not
pre-registered cannot be automated, and extension is manual. This is deliberate and defensible — argue
it rather than conceal it. Likewise, rule-based prioritisation sacrifices predictive ceiling for
auditability.

---

## VIII. Conclusion and Future Work

This paper presented Auto-Ops-AI, a context-aware multi-agent framework for enterprise IT support
addressing the scalability deficit in ITSM. The framework integrates five specialised agents covering
conversation, ticket intelligence, execution, image analysis and status management, grounds
troubleshooting in organisational knowledge through retrieval-augmented generation, and confines
remediation to a whitelist of non-destructive operations under mandatory logged user approval.
Decoupling the conversational agent from the execution agent establishes a privilege boundary that
bounds risk structurally rather than behaviourally. The work is positioned within Design Science
Research, treating the architecture as an artefact evaluated against the bottlenecks it is designed to
remediate.

The transferable proposition is that in agentic systems operating on untrusted input, safety is more
reliably obtained by restricting what the model is able to express than by constraining what it is
inclined to say.

> **[Complete once results exist: one sentence stating the strongest empirical outcome, particularly the
> adversarial containment rate.]**

**Future work.** Expanding the knowledge base and re-evaluating retrieval at realistic scale; extending
remediation beyond Windows endpoints; evaluating with practising support staff in an operational
setting; integration with established ITSM platforms; and formal verification of the parameter-validation
layer, which is the load-bearing control in the safety argument.

---

## References

> IEEE numbered style, matching the conference template. Entries [1]–[12] were individually verified as
> existing. Entries [13]–[16] are industry and practitioner sources carried from the interim report and
> **require primary-source verification before submission** (see the notes following).

[1] P. Lewis *et al.*, "Retrieval-augmented generation for knowledge-intensive NLP tasks," in *Proc. Adv.
Neural Inf. Process. Syst. (NeurIPS)*, 2020, pp. 9459–9474.

[2] Y. Gao *et al.*, "Retrieval-augmented generation for large language models: A survey," *arXiv
preprint arXiv:2312.10997*, 2023.

[3] W. X. Zhao *et al.*, "A survey of large language models," *arXiv preprint arXiv:2303.18223*, 2023.

[4] L. Wang *et al.*, "A survey on large language model based autonomous agents," *Frontiers of Computer
Science*, vol. 18, no. 6, p. 186345, 2024.

[5] T. Schick *et al.*, "Toolformer: Language models can teach themselves to use tools," in *Proc. Adv.
Neural Inf. Process. Syst. (NeurIPS)*, 2023.

[6] S. Yao *et al.*, "ReAct: Synergizing reasoning and acting in language models," in *Proc. Int. Conf.
Learn. Represent. (ICLR)*, 2023.

[7] Q. Wu *et al.*, "AutoGen: Enabling next-gen LLM applications via multi-agent conversation," *arXiv
preprint arXiv:2308.08155*, 2023.

[8] S. Hong *et al.*, "MetaGPT: Meta programming for a multi-agent collaborative framework," in *Proc.
Int. Conf. Learn. Represent. (ICLR)*, 2024.

[9] K. Greshake *et al.*, "Not what you've signed up for: Compromising real-world LLM-integrated
applications with indirect prompt injection," in *Proc. 16th ACM Workshop on Artificial Intelligence and
Security (AISec)*, 2023, pp. 79–90.

[10] OWASP Foundation, "OWASP Top 10 for Large Language Model Applications," 2023. [Online]. Available:
https://owasp.org/www-project-top-10-for-large-language-model-applications/

[11] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using Siamese BERT-networks," in
*Proc. Conf. Empirical Methods Natural Language Processing (EMNLP)*, 2019, pp. 3982–3992.

[12] V. Karpukhin *et al.*, "Dense passage retrieval for open-domain question answering," in *Proc. Conf.
Empirical Methods Natural Language Processing (EMNLP)*, 2020, pp. 6769–6781.

[13] Statista, "IT service management (ITSM) — global market revenue 2020–2028," Statista Research, 2025.
**[VERIFY]**

[14] HDI, "Technical support practices and salary report 2024," HDI Research, 2024. **[VERIFY]**

[15] International Data Corporation, "The business value of IT service automation," IDC, 2024.
**[VERIFY]**

[16] V. Patel and S. K. Singh, "Intelligent ticket routing in ITSM using NLP and machine learning," in
*Proc. IEEE Int. Conf. Service Operations and Logistics*, 2023, pp. 112–119. **[VERIFY]**

### Citation notes

**Removed — verified not to exist.** The following interim-report citations were searched and could not
be located in any indexed database. Each shows the signature of machine-generated references: a plausible
title in a real journal with an invented article number. They must not be reinstated.

| Interim report citation | Status |
|---|---|
| Ahmad *et al.*, "A Systematic Review of AI Chatbots in ITSM," *J. Syst. Softw.*, 198, 111602, 2023 | Not found |
| Xu *et al.*, "Conversational AI for IT Support," *Inf. Syst. Frontiers*, 25(3), 2023 | Not found |
| Kumar & Mehta, "Predictive Analytics for ITSM," *Expert Syst. Appl.*, 238, 122034, 2024 | Not found |
| Li *et al.*, "Multi-Agent Systems for Enterprise AI: A Survey," *ACM Comput. Surv.*, 56(4), 2024 | Not found |

The arguments these citations supported in the interim report — the weakness of intent-classification
chatbots, the security case for multi-agent decomposition, the risk barrier to autonomous remediation —
have been retained and re-attached to verified literature [4]–[10]. **The argument does not depend on the
removed sources.**

**Requiring verification.** References [13]–[16] and the associated statistics (USD 22 billion market,
24.2-hour L1 resolution, 40% repetitive workload, USD 1.55 trillion downtime cost) are carried from the
interim report but could not be confirmed against primary documents. Obtain each report and cite it
precisely with page reference, or remove the claim. Two further interim-report citations — Gartner (2024)
and Freshworks (2024), together with CompTIA (dated "2924", evidently a typographical error) and U.S.
Bureau of Labor Statistics (2024) — have been dropped, as the Introduction has been reconstructed so that
its argument does not rely on them.
