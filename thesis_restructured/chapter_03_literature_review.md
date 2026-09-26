# Chapter 3 - Literature Review

> **Draft status:** First evidence-based structural draft. Citation numbering is provisional and corresponds to `references_working.md`.

## 3.1 Chapter Overview and Review Approach

This chapter reviews the research needed to position AutoOps AI as a context-aware IT-support framework with risk-adaptive and verifiable remediation. The review addresses two connected concerns. The first is capability: how conversational models, retrieval-augmented generation (RAG), specialized agents, and operational tools can assist with understanding and resolving IT incidents. The second is control: how an AI-proposed action can be constrained, authorized, executed, verified, and recovered without treating model output as execution authority.

The literature was examined as a structured narrative review rather than a systematic review or meta-analysis. Searches conducted on 26 September 2026 covered IT support and AIOps, LLM and multi-agent systems, RAG evaluation, AI risk management, human interaction with automation, tool-use security, runtime enforcement, preconditions and postconditions, configuration control, authorization scope, and autonomic computing. Candidate sources were verified through official proceedings or publication records from ACM, ACL Anthology, NeurIPS, PMLR, MLSys, IJCAI, NIST, the RFC Editor, Microsoft Research, IBM Research, and arXiv where a formal record was unavailable. Peer-reviewed papers, standards, and authoritative technical guidance were preferred. Generic chatbots without operational tool use, predictive-maintenance studies outside the remediation scope, vendor marketing claims, and secondary summaries were excluded from the core comparison. The complete search record and limitations are provided in `literature_search_record.md`.

The review is intentionally bounded. It supports the conclusion that the selected literature provides limited evidence of the complete integration proposed in this study. It does not establish that no comparable system exists anywhere. This distinction is important because several recent systems contain closely related controls, particularly runtime policy enforcement and contract-based tool execution.

## 3.2 Intelligent IT Support and Closed-Loop Remediation

IT support involves identifying an incident, gathering diagnostic information, selecting a corrective procedure, changing system state where appropriate, confirming restoration, documenting the case, and escalating unresolved conditions. The quality of the process depends not only on identifying a likely cause, but also on the accessibility of organizational knowledge and the ability to determine whether a selected change is appropriate for the current environment.

AutoTSG demonstrates the practical value and limitations of operational troubleshooting knowledge [1]. Its study examined more than 4,000 troubleshooting guides linked to thousands of incidents and reported that guides were widely used but could be fragmented, incomplete, difficult to validate, and costly to maintain. AutoTSG combined machine learning and program synthesis to convert natural-language troubleshooting material into executable workflows. This establishes that operational documentation can be transformed into structured action. It does not, however, establish a contextual mechanism for selecting different authorization levels or verifying that an executed procedure resolved the user-visible problem.

RCAgent extends operational assistance from static guide execution to active evidence gathering [5]. It uses a tool-augmented LLM agent for cloud root-cause analysis and employs specialized analytical tools, observation management, and self-consistency to operate over large diagnostic data. Its industrial evaluation supports the use of agents for iterative investigation. Nevertheless, root-cause quality and action validity are not equivalent to remediation governance. A credible diagnosis does not alone determine the potential impact, reversibility, affected scope, or required approver for the proposed change.

AIOpsLab provides a complementary evaluation perspective [14]. It deploys cloud applications, injects faults, generates workloads, exposes telemetry, and allows agents to interact with a changing operational environment. This addresses a limitation of static question-answer benchmarks: an operational agent should be evaluated through stateful interaction and observable outcomes. AIOpsLab is therefore relevant to AutoOps AI's use of repeatable scenarios and injected failures. Its cloud-scale focus and general evaluation interface do not themselves provide the domain-specific graded authorization and recovery policy required for end-user remediation.

Closed-loop system management predates LLM agents. Autonomic-computing architectures organize self-management around monitoring, analysis, planning, execution, and shared knowledge, and connect these functions to self-configuration, self-healing, self-optimization, and self-protection [20]. This provides a useful conceptual foundation for AutoOps AI. A remediation loop should observe state, analyse evidence, plan a change, execute through a defined interface, and feed the observed result back into the process. AutoOps AI adds two controls that are not automatically implied by a general autonomic loop: risk-dependent human authority before a state-changing action and explicit verification of both the remediation and any attempted rollback.

Security-focused configuration management also treats system changes as controlled activities rather than isolated commands. NIST SP 800-128 links configuration control, monitoring, security impact, authorization, documentation, and organizational risk [22]. Although the guidance is not written for LLM agents, it supports the principle that a system-changing remediation should have an identified target, an authorized change, a retained record, and observable post-change state. Together, the troubleshooting, AIOps, autonomic-computing, and configuration-management literature establishes the domain requirement for an auditable feedback loop rather than a one-way chatbot-to-command pipeline.

## 3.3 Multi-Agent and Tool-Using Systems

ReAct combines reasoning and acting by allowing a language model to alternate between an internal plan, a tool action, and an observation returned by the environment [2]. This interaction pattern suits troubleshooting because an initial hypothesis can prompt a diagnostic observation, which can then alter the next action. However, ReAct primarily improves task solving; it does not ensure that the same model is qualified to authorize the action it proposes. A plausible reasoning trace is not a security boundary.

AutoGen shows how applications can be composed from agents that communicate with one another and can incorporate tools and human participants [3]. Such composition supports role specialization: one component may conduct a conversation, another may process a ticket, and another may execute a registered operation. The broader survey by Guo *et al.* identifies profiling, communication, environment interaction, planning, and capability acquisition as recurring multi-agent concerns [4]. It also highlights continuing challenges involving coordination, reliability, evaluation, and the difficulty of showing that multiple agents improve the system rather than merely increasing its complexity.

This literature supports using specialized capabilities in AutoOps AI, but it also limits the claim that a multi-agent architecture is itself novel or necessarily safer. Multiple agents can share the same unsupported assumption, propagate incorrect context, or provide an appearance of independent agreement when they rely on the same underlying model. Consequently, agent outputs are treated as proposals and evidence, not as permission. The implementation's deterministic remediation services and action contracts must retain authority even when the wider interaction is described using an agent-oriented architecture.

The distinction between conceptual and implemented agents is also methodologically important. An architecture diagram may describe conversation, retrieval, diagnosis, execution, image analysis, and status management as roles. The final thesis must separately identify which roles exist as concrete agent classes and which are implemented as services or endpoint orchestration. The literature justifies functional decomposition, but it does not justify describing every service as an autonomous agent.

## 3.4 Retrieval-Augmented Generation and Evidence Quality

RAG combines parametric generation with retrieved non-parametric knowledge [15]. The approach is relevant to organizational support because troubleshooting procedures, policies, and previously approved resolutions can change more quickly than a foundation model is retrained. Retrieval can also provide provenance for a recommendation by identifying which article or procedure influenced it.

Retrieval does not guarantee that the returned material is relevant, authoritative, current, applicable to the target, or faithfully used by the generated response. RAGAS separates dimensions such as context relevance, answer relevance, and faithfulness, demonstrating that a RAG pipeline requires evaluation at more than one stage [6]. For AutoOps AI, this creates a necessary distinction between retrieval quality and action safety. A semantically similar article may be useful evidence, but it cannot grant permission to execute a state-changing operation. Conversely, a weak match should reduce confidence in unattended remediation.

The literature implies three evaluation levels. First, retrieval evaluation should determine whether labelled relevant material appears in the ranked results, using measures such as Hit@1, Hit@3, and mean reciprocal rank. Second, grounding evaluation should determine whether the answer or proposal is supported by the retrieved material. Third, operational evaluation should determine whether the resulting action is permissible and whether it achieves the required state. RAG and RAGAS principally address the first two levels; AutoOps AI uses retrieval as an input to the third.

This distinction also affects knowledge learning. A system that writes its own unverified solution into the retrievable corpus can create a feedback loop in which an unsupported answer later appears to have organizational evidence. Reviewer approval before a learned article becomes searchable is therefore a meaningful boundary. The literature supports grounding and faithfulness assessment, while the present study adds a domain workflow in which admission to the knowledge base and remediation authority remain human- and policy-controlled.

## 3.5 Risk-Adaptive Automation and Human Oversight

The NIST AI Risk Management Framework organizes AI risk activities around governing, mapping, measuring, and managing risks throughout the system lifecycle [10]. Its Generative AI Profile emphasizes risks that are created or intensified by generative systems, including confabulation, information-security concerns, human-AI configuration, and the need for context-sensitive testing and documentation [11]. These sources do not prescribe AutoOps AI's five-factor formula, but they support transparent, contextual, and continuously evaluated controls instead of relying on a single model confidence score.

Human-factors research further shows that automation is not an all-or-nothing design choice. Parasuraman, Sheridan, and Wickens describe different types and levels of automation across information acquisition, analysis, decision selection, and action implementation [21]. Automation changes the operator's work and can introduce new coordination demands. This supports graded autonomy: gathering read-only evidence, proposing an action, authorizing it, and implementing it need not have the same automation level.

Human approval alone is not a sufficient safety claim. An approver requires relevant information and a meaningful ability to reject or correct the system. Amershi *et al.* recommend making system capabilities clear, presenting contextually relevant information, supporting correction, and enabling recovery when an AI system is wrong [13]. Applied to remediation, an approval request should identify the proposed action, target, parameters, supporting evidence, expected effect, possible impact, and recovery availability. A generic confirmation detached from the actual operation provides weaker control.

The selected literature supports the five conceptual factors used by AutoOps AI, but it does not independently validate their implemented weights or thresholds. Potential impact and affected scope relate to contextual risk mapping [10], [11]. Diagnosis confidence reflects the strength of the inferred cause and supporting observations [2], [5]. Evidence quality relates to retrieval relevance and faithful grounding [6], [15]. Reversibility relates to correction, recovery, and controlled change [13], [22]. These relationships justify the constructs, while Chapter 4 must state how the prototype actually operationalizes them and Chapter 6 must acknowledge that author-selected scales and weights require external calibration.

The practical implication is proportional intervention. A bounded, reversible, strongly supported user-local operation may receive more autonomy than a privileged, weakly supported, irreversible, or shared-resource change. Medium-risk cases require explicit approval, whereas unacceptable cases must be blocked or escalated. This design preserves human authority where uncertainty or consequence is higher without requiring the same intervention for every read-only observation or bounded action.

## 3.6 Runtime Enforcement, Tool Security, and Authorization

Tool access changes an LLM from an advisory component into a system capable of producing external effects. ToolEmu provides a scalable method for identifying such risks using an LM-emulated sandbox [7]. Its evaluation showed that model agents can produce risky outcomes across diverse high-stakes tools. The framework is valuable for scenario generation and pre-deployment testing, but a model-based emulator and evaluator cannot be the only runtime safeguard for a real endpoint.

AgentDojo focuses on prompt injection against agents that process untrusted data and use tools [8]. Its stateful benchmark combines benign user tasks with adversarial instructions embedded in tool-accessible content. The findings demonstrate that security cannot be reduced to whether the initial user prompt appears safe. Retrieved articles, web pages, messages, and tool outputs can also influence an agent. For AutoOps AI, retrieved text must therefore be treated as evidence rather than executable authority, and tool permissions must be enforced outside the model.

GuardAgent and ShieldAgent both separate the protected agent from a guard component [16], [17]. GuardAgent translates safety requests into checking plans and executable guardrail code, while ShieldAgent constructs policy structures and evaluates action trajectories against them. Their empirical results support independent policy checking, but the systems primarily produce guard decisions for general healthcare or web-agent benchmarks. They do not directly define domain-specific low-, medium-, and high-risk remediation routes or prove restoration after a failed endpoint action.

AgentSpec introduces a domain-specific language containing triggers, predicates, and enforcement mechanisms for runtime agent constraints [9]. Its evaluation across code, embodied, and autonomous-driving tasks demonstrates the practical value of explicit enforcement checkpoints. ToolSafe similarly evaluates each proposed invocation before execution and uses feedback to redirect a ReAct-style agent [19]. These studies support intercepting actions at the tool boundary. AutoOps AI adopts a stricter implementation principle for its curated operations: a denied or unknown action is technically prevented by the executor rather than relying on the language model to follow natural-language feedback.

Classical security principles strengthen this boundary. The principle of least privilege requires a subject or program to operate with only the authority necessary for its task [23]. Attribute-based access control evaluates subject, object, requested operation, and environmental attributes against policy [25]. OAuth's scope concept illustrates that an authorization grant should be limited and that clients should request only the minimum required scope [24]. AutoOps AI does not implement OAuth for remediation approval, but these principles justify action-specific, target-specific, time-limited, and single-use execution authorization instead of a reusable generic approval.

These sources also reveal a limitation. Runtime guards can enforce only the policies and state that they can observe. A correct action identifier with misleading parameters, stale device state, or an incorrectly defined contract may still produce harm. Runtime enforcement must therefore be combined with reliable identity, parameter validation, target binding, preconditions, postconditions, adversarial testing, and audit evidence.

## 3.7 Verifiable Execution, Recovery, and Auditability

ToolGate directly addresses the gap between tool invocation and trusted state [18]. It represents tools using Hoare-style precondition and postcondition contracts. A precondition determines whether invocation is allowed in the current state, while a postcondition determines whether the result can be accepted into the trusted symbolic state. This is closely aligned with the distinction in AutoOps AI between an action being executed and the reported incident being verified as resolved.

The relevance of ToolGate is substantial but should not be overstated. Its contribution concerns logical state evolution in general tool-augmented reasoning. It does not provide the complete end-user IT-support process of knowledge retrieval, contextual risk scoring, user or expert approval, endpoint execution, ticket handling, and verified rollback. It does, however, demonstrate that explicit contracts are a stronger foundation than interpreting a command return value as proof of success.

Doshi *et al.* argue for deriving enforceable tool-use specifications from system-level hazard analysis and propose multiple enforcement levels, including deterministic blocking, required actions, capability limits, and selective confirmation [12]. This work provides a close conceptual precedent for risk-adaptive authority. Its contribution is a general process and emerging architecture rather than a completed IT-support remediation evaluation. AutoOps AI operationalizes a narrower version through an allow-listed catalogue, policy thresholds, approval states, preconditions, postconditions, and recovery rules.

Recovery must follow the same evidence principle as remediation. Issuing an inverse operation does not establish restoration. The previous state must be captured where required, the rollback must be invoked through a registered action, and its result must be checked against observable state. NIST configuration-management guidance supports controlled, documented, and monitored changes [22], while the autonomic-computing literature supplies the feedback-loop model [20]. The reviewed agent literature discusses safety interception and verified state, but verified rollback outcomes are rarely a central evaluation measure.

Auditability connects all stages. A useful record must identify the request, retrieved evidence, proposed action, risk inputs, policy result, approver where applicable, target, precondition observations, execution result, postcondition observations, recovery attempt, and final state. Persistent logs improve traceability but are not automatically tamper-evident. The present prototype can claim ordered persistent decision records; stronger integrity guarantees require cryptographic signing, append-only storage, or independently protected logging and remain outside the implemented scope.

## 3.8 Comparison of Existing Approaches

Table 3.1 compares the reviewed systems against the capabilities needed by the present study. A filled circle indicates that the capability is central and evaluated, a half circle indicates partial or indirect treatment, and a dash indicates that it is not a central evaluated contribution of the cited work. The table describes the reported scope of each study; a dash does not mean that the system could never be extended to provide that capability.

**Table 3.1. Comparison of related approaches against the proposed integration**

| Approach | Operational evidence/grounding | Runtime execution control | Graded human authority | Post-action state verification | Verified recovery | IT-support/AIOps evaluation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoTSG [1] | ● | ◐ | — | ◐ | — | ● |
| ReAct [2] | ◐ | — | — | — | — | — |
| AutoGen [3] | ◐ | ◐ | ◐ | — | — | — |
| RCAgent [5] | ● | ◐ | — | — | — | ● |
| RAG and RAGAS [6], [15] | ● | — | — | — | — | — |
| ToolEmu [7] | ◐ | — | — | — | — | — |
| AgentDojo [8] | ◐ | ◐ | — | — | — | — |
| AIOpsLab [14] | ● | ◐ | — | ◐ | ◐ | ● |
| GuardAgent [16] | ◐ | ● | — | — | — | — |
| ShieldAgent [17] | ◐ | ● | — | ◐ | — | — |
| AgentSpec [9] | ◐ | ● | — | ◐ | — | — |
| ToolSafe [19] | ◐ | ● | — | — | — | — |
| ToolGate [18] | ● | ● | — | ● | — | — |
| Verifiably safe tool-use process [12] | ◐ | ● | ● | ● | — | — |
| Proposed AutoOps AI evaluation target | ● | ● | ● | ● | ● | ● |

The comparison shows that the strongest overlap comes from recent safe-tool-use and contract-execution work. Therefore, the thesis must not claim novelty for preconditions, postconditions, policy interception, or selective confirmation individually. The differentiating research target is their domain-specific connection to retrieved IT-support evidence, a transparent risk class, scoped approval, endpoint action contracts, verified recovery, ticket state, and a comparative evaluation.

Table 3.2 translates the literature into concrete design implications.

**Table 3.2. Literature-to-design traceability**

| Literature finding | Design implication for AutoOps AI |
| --- | --- |
| Operational knowledge is useful but can be incomplete or difficult to execute consistently [1]. | Use a curated article set and map only supported recommendations to registered actions. |
| Agents benefit from iterative observations and specialized roles [2]-[5]. | Permit agent-assisted interpretation and diagnosis, but keep execution authority in separate deterministic services. |
| RAG needs retrieval and faithfulness evaluation [6], [15]. | Evaluate ranked retrieval separately and carry evidence strength into the risk decision without treating retrieval as authorization. |
| Operational agents require stateful scenarios and fault injection [7], [14]. | Use repeatable scenarios, observable states, and controlled fault injection, while retaining real-endpoint evidence. |
| Untrusted content can redirect tool-using agents [8]. | Treat retrieved/tool text as untrusted evidence and validate every executable action outside the LLM. |
| AI risks must be governed and evaluated in context [10], [11]. | Use explicit factor definitions, versioned policy, overrides, retained traces, and stated limitations. |
| Automation can be allocated at different levels [21]. | Route actions according to risk instead of requiring either universal automation or universal approval. |
| Human-AI interaction should support understanding, correction, and recovery [13]. | Present evidence, effect, scope, risk, and rollback information to an approver. |
| Least privilege and scoped authorization restrict the consequences of misuse [23]-[25]. | Restrict execution to an allow-listed action, validated parameters, an identified target, expiry, and single use. |
| Runtime constraints should be explicit and externally enforced [9], [12], [16], [17], [19]. | Apply deterministic policy and action checks that the proposing model cannot bypass. |
| Preconditions and postconditions support trusted state evolution [18]. | Verify state before execution and accept resolution only after observing the required postcondition. |
| Controlled changes require monitoring and records [20], [22]. | Record the complete transition and verify rollback or escalate when safe restoration cannot be demonstrated. |

## 3.9 Synthesized Research Gap and Implications

Five connected gaps emerge from the reviewed literature.

**Integration gap.** IT troubleshooting, RAG, multi-agent coordination, risk governance, runtime guardrails, contract verification, and change control are usually studied as separate problems. The reviewed work provides limited evidence of an end-user IT-support artefact that evaluates them as one closed remediation loop.

**Graded-authority gap.** Several safety approaches enforce allow/deny decisions or provide general human confirmation. Practical support requires a more explicit distinction among bounded automatic candidates, user-approved changes, expert-controlled actions, and prohibited operations. The selected authority must be tied to contextual risk rather than only the presence of a tool call.

**Evidence-to-authority gap.** RAG research evaluates retrieval and answer grounding, whereas agent-safety work evaluates actions and policies. The reviewed studies provide limited examination of retrieval strength as one input to the amount of execution autonomy permitted for an IT remediation.

**Outcome-and-recovery gap.** ToolGate establishes strong precondition/postcondition concepts, and configuration-management literature emphasizes monitored changes. However, the reviewed agent systems rarely make verified rollback or escalation outcome a central end-user remediation measure. A command, tool response, or issued inverse action must not be accepted as proof of resolution or restoration without observed state.

**Domain-evaluation gap.** AIOpsLab, RCAgent, and AutoTSG provide operational evidence, but their main settings are cloud incidents, guide automation, or root-cause analysis. AgentDojo, ToolEmu, GuardAgent, ShieldAgent, AgentSpec, ToolSafe, and ToolGate provide broader security or tool-use evaluations. The reviewed set does not evaluate the full combination using common endpoint-support cases with risk labels, approval routing, postconditions, recovery traces, retrieval results, and limited real-device execution.

These gaps motivate AutoOps AI as an integration contribution. The proposed framework connects approved support evidence to an action proposal, converts configured contextual factors into a deterministic risk class, selects the applicable authority, checks a registered contract, executes through a restricted driver, observes the result, and either completes, rolls back, or escalates while retaining an audit record. The research contribution must be evaluated at this integrated-workflow level. Demonstrating only accurate risk labels or a working chatbot would not be sufficient.

The review also constrains the evaluation claims. Author-labelled scenarios can show whether the implementation conforms to its specification, but they do not independently validate the policy. Simulator tests can provide repeatability and controlled failures, but they do not demonstrate production effectiveness. Retrieval similarity can support ranking, but it does not by itself establish authority, currency, applicability, or faithfulness. These limitations shape the methodology in Chapter 4 and must remain visible in the final discussion.

## 3.10 Chapter Summary

This chapter examined the capability and control literature relevant to risk-adaptive IT remediation. AutoTSG, RCAgent, and AIOpsLab establish the value of structured operational knowledge, tool-assisted diagnosis, stateful evaluation, and fault injection. ReAct, AutoGen, and multi-agent research support iterative reasoning and specialized roles but do not provide execution authority. RAG and RAGAS support external grounding and separate retrieval from faithfulness. NIST risk guidance, levels-of-automation research, human-AI guidelines, least-privilege principles, and configuration management provide foundations for contextual risk and meaningful human control. AgentDojo, ToolEmu, GuardAgent, ShieldAgent, AgentSpec, ToolSafe, and recent verifiable tool-use work demonstrate the importance of independent security enforcement. ToolGate provides the closest technical basis for explicit preconditions and postconditions.

The resulting gap is not the absence of these mechanisms individually. It is the limited evidence, within the reviewed set, of their integration and evaluation as a domain-specific loop that links IT-support evidence to graded authority, controlled endpoint execution, observed outcomes, and verified recovery. Chapter 4 therefore explains how this synthesis was converted into the requirements, architecture, implementation procedure, and evaluation plan for AutoOps AI.
