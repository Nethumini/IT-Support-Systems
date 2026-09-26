# Chapter 1 - Introduction

> **Draft status:** First restructured draft. Citation tokens and confirmation notes are intentionally retained until the reference library and approved proposal are checked.

## 1.1 Chapter Overview

This chapter introduces the problem addressed by the research and explains why safer automation is needed in intelligent IT-support systems. It outlines the development of AI-assisted support, the difficulty of allowing language-model-based systems to perform actions on user devices, and the need to connect recommendations with explicit authorization and outcome verification. The chapter then defines the research problem and gap, presents the research questions, explains the significance and scope of the study, and gives a concise overview of the proposed AutoOps AI framework.

## 1.2 Background

Organizations depend on endpoint devices, applications, networks, and shared digital services to support everyday work. When these components fail, users commonly depend on IT-support teams to diagnose the incident, find an appropriate solution, apply the corrective action, and confirm that normal operation has been restored. Many incidents are repetitive, but their resolution can still require several exchanges between users and support personnel. This creates delays for users and consumes support capacity that could otherwise be directed towards unusual or high-impact incidents [1].

Artificial intelligence has increasingly been applied to knowledge retrieval, troubleshooting, root-cause analysis, and operational workflow automation [1], [5], [14]. Large language models can interpret informal descriptions and generate diagnostic or resolution suggestions, while retrieval-augmented generation can supply organization-specific material rather than relying entirely on information encoded in a model's parameters [15]. Multi-agent approaches can further divide a support task into specialized functions such as conversation management, ticket processing, evidence retrieval, visual-error analysis, and action execution [2]-[4].

Generating a plausible recommendation, however, is different from safely changing a computer system. A model-generated action may be unsupported by the available evidence, inappropriate for the target environment, disruptive to other resources, irreversible, or outside the user's authority. An action can also finish without producing the required outcome. For example, a command returning a successful exit status establishes that the command ran, but does not by itself establish that the reported problem was resolved. Systems that connect language models to tools therefore require controls over what may be executed, by whom, against which target, and under what conditions [7]-[9], [16], [17], [19]. They also require observations of the resulting state rather than accepting a model's assertion that the action succeeded [12], [18].

AutoOps AI was developed as a context-aware IT-support artefact that combines conversational assistance, ticket-management functions, knowledge retrieval, support-agent services, and controlled remediation. Its central research contribution is a risk-adaptive and verifiable remediation workflow. The language-model layer may help interpret a request and propose a supported action, but a deterministic control path calculates the applicable risk, selects the required authority, validates the proposed operation, executes it through a restricted driver, and verifies the observed outcome. Failed or inconclusive outcomes lead to verified rollback where a defined inverse is available, or to escalation where safe recovery cannot be established.

## 1.3 Problem Statement

Existing AI-assisted support tools can make diagnostic information easier to access and can recommend troubleshooting steps. Nevertheless, a recommendation-only system leaves the user or technician responsible for interpreting and applying each step, while a system that gives a language model unrestricted execution authority introduces unacceptable operational and security risks. The research problem is therefore not simply how to generate an IT-support answer. It is how to permit useful remediation while ensuring that execution authority is proportionate to contextual risk and that claimed resolution is supported by observed system state.

Three connected difficulties motivate this problem. First, remediation risk is contextual. The same action can have different consequences depending on the target, available evidence, diagnostic confidence, reversibility, and resources potentially affected. Second, human approval is meaningful only when it is scoped to the proposed action, parameters, and target and is checked before execution. Third, action completion cannot be equated with problem resolution; the system must test explicit postconditions and respond safely when the required state is not achieved.

Accordingly, this study addresses the absence of an evaluated control workflow in the project context that connects evidence-grounded recommendations to explainable risk classification, graded authorization, deterministic safety checks, restricted execution, post-action verification, and controlled recovery. The intended solution must retain the usefulness of AI-assisted support without allowing model-generated text to become unrestricted system commands.

## 1.4 Research Gap

Prior research provides important elements of intelligent remediation. Retrieval-augmented generation grounds model responses in external knowledge [6], [15]; reasoning-and-action and multi-agent frameworks allow models to coordinate tools [2]-[4]; guardrail and policy approaches restrict unsafe actions [9], [12], [16]-[19]; and autonomic-computing and configuration-management research provides established concepts for monitoring, execution, controlled change, and recovery [20], [22].

These individual mechanisms do not automatically form a safe remediation process. Retrieval relevance does not itself decide whether an action may execute. Human approval does not demonstrate that the approved operation achieved its intended result. A successful tool response does not verify the resulting device state. Similarly, rollback cannot be treated as successful merely because an inverse command was issued; restoration must also be checked.

The research therefore focuses on the limited evidence, within the reviewed literature, of IT-support frameworks that integrate all of the following within one evaluated workflow:

1. evidence-grounded recommendation of a supported remediation action;
2. deterministic and explainable risk assessment using contextual signals;
3. risk-dependent selection of automatic execution, human approval, or expert escalation;
4. approval scoped to the proposed action, parameters, and target;
5. deterministic pre-action validation and controlled execution;
6. post-action verification using observed state; and
7. verified rollback or escalation with an auditable decision history.

This is an **integration and evaluation gap**. The study does not claim to have invented retrieval, multi-agent coordination, risk scoring, approval workflows, verification, rollback, or audit logging individually. The claimed contribution is the design, implementation, and evaluation of their coordinated use for risk-adaptive IT-support remediation. The strength of this gap statement must be confirmed through the structured comparison in Chapter 3 rather than through an unsupported claim that no related framework exists.

## 1.5 Research Questions

The study is guided by the following questions:

**RQ1:** How can evidence-grounded IT-support recommendations be integrated with deterministic, risk-adaptive authorization and controlled remediation?

**RQ2:** To what extent does the implemented risk-adaptive policy prevent scenarios labelled unsafe for autonomous execution while avoiding unnecessary approval requirements compared with the selected baselines?

**RQ3:** How reliably does the framework verify remediation outcomes and invoke rollback or escalation when execution does not produce the required state?

**RQ4:** How effectively does the knowledge-retrieval component return relevant approved support evidence for representative IT-support queries?

> [CONFIRM: Ensure these questions remain consistent with the approved proposal and the final wording of Chapter 2 before supervisor submission.]

## 1.6 Research Motivation and Significance

The study is motivated by the tension between the usefulness of AI-assisted troubleshooting and the risk of allowing probabilistic model output to control operational systems. A support assistant that can only provide text may reduce information-search time but cannot complete the remediation loop. Conversely, an assistant that executes arbitrary generated commands may cause disruption, exceed a user's authority, or report success without observing the resulting state. A practical design must therefore provide useful automation while making authority, safety checks, execution boundaries, and outcome evidence explicit.

The research has three forms of significance.

### 1.6.1 Research significance

The study contributes an applied framework that treats evidence, authority, execution, and outcome verification as connected stages. Its principal research value is the integration of these controls and the evaluation of their interaction. In particular, the framework examines two propositions: weak supporting evidence should reduce the autonomy granted to a proposed action, and command completion should not be treated as verified resolution.

### 1.6.2 Practical significance

For IT-support users and practitioners, the framework provides a way to automate selected operations without granting unrestricted command authority to a language model. Low-risk supported actions can proceed through a controlled route, actions requiring consent can be held for approval, and high-risk or unsupported actions can be blocked or escalated. The resulting decision and execution records can help support personnel understand what was proposed, why it was permitted or refused, what was observed, and whether recovery was attempted.

### 1.6.3 Methodological significance

The framework separates the probabilistic interpretation and recommendation layer from the deterministic control and verification layer. This separation allows risk rules, approval states, action contracts, execution drivers, and recovery behaviour to be tested without depending on variable language-model output. A repeatable simulator can be used for controlled policy and failure-path evaluation, while endpoint execution can examine whether the same control design operates against an actual device. This combination supports reproducibility while acknowledging that simulator results alone do not establish production effectiveness.

## 1.7 Scope

### 1.7.1 Included in the study

The study includes:

- a web-based AI-assisted IT-support prototype named AutoOps AI;
- conversational support and ticket-related services;
- semantic retrieval over a curated and reviewer-approved support knowledge base;
- proposal of actions from a restricted remediation catalogue;
- explainable risk classification using impact, diagnosis/classification confidence, evidence quality, reversibility, and affected-resource factors;
- low-, medium-, and high-risk control paths;
- scoped approval and single-use execution authorization;
- action-specific preconditions and postconditions;
- controlled execution through simulator, host, PowerShell, and enrolled-endpoint driver boundaries as applicable;
- rollback where a defined inverse exists, otherwise escalation;
- persistent audit records and reviewer-controlled admission of learned knowledge;
- simulator-based comparative evaluation, fault injection, repeatability checks, retrieval testing, end-to-end cases, and limited real-Windows-endpoint evidence.

### 1.7.2 Excluded from the study

The study does not claim to provide:

- unrestricted shell or arbitrary command execution generated by a language model;
- autonomous execution of critical, destructive, irreversible, or unsupported operations;
- production-scale validation across multiple organizations or large device fleets;
- universal correctness of the selected risk weights, thresholds, or scenario labels;
- cryptographically tamper-evident audit storage;
- hardware-backed attestation of endpoint-reported state;
- complete support for every operating system, application, or IT incident;
- evidence of user acceptance or usability from human participants unless a separately approved study is completed; or
- proof that the framework is superior to all existing IT-support approaches.

The evaluation is intended to establish implementation correctness, specification conformance, retrieval behaviour, safety-path behaviour, recovery handling, and limited endpoint feasibility within the stated test conditions. Its limitations are reported explicitly in Chapter 6.

## 1.8 Overview of the Proposed Solution

AutoOps AI organizes remediation as a controlled sequence rather than allowing a language model to execute generated instructions directly.

1. The system receives the authenticated user's problem description and available context.
2. Relevant approved support knowledge is retrieved and used to support the proposed response or action.
3. The system maps an eligible recommendation to a predefined action and validated parameters.
4. A deterministic engine calculates a risk score from configured contextual factors and applies safety overrides.
5. The resulting risk class determines whether execution may proceed without an approval token, must wait for authorized approval, or must be blocked and escalated.
6. Before execution, the framework revalidates the action, parameters, target, authority, and action-specific preconditions.
7. An execution driver invokes the registered operation rather than executing unrestricted model-generated code.
8. The framework observes the relevant system state and evaluates the action's postconditions.
9. A verified successful outcome can complete the request. Failure or an inconclusive result initiates a defined and post-checked rollback where available; otherwise, the request is escalated.
10. The proposal, assessment, approval, checks, execution, observations, recovery, and final state are recorded for auditability.

The architecture uses specialized conversational, ticket, image-analysis, execution, and status capabilities, supported by backend services for retrieval, risk assessment, verification, remediation orchestration, device jobs, and knowledge review. The multi-agent and retrieval components assist the remediation workflow, while deterministic control services retain execution authority.

> [FIGURE PLACEHOLDER: A single high-level workflow showing evidence retrieval -> proposed action -> risk assessment -> graded authorization -> precheck -> controlled execution -> postcheck -> verified completion or rollback/escalation -> audit. Detailed architecture belongs in Chapter 4.]

## 1.9 Chapter Summary

This chapter established the need for an IT-support framework that goes beyond generating plausible recommendations while avoiding unrestricted AI-controlled execution. The identified problem concerns the connection between evidence, contextual risk, authorization, controlled action, and verified outcome. The research addresses this problem through an integrated risk-adaptive and verifiable remediation workflow. Its contribution is the coordinated framework and its evaluation, rather than the invention of the individual component techniques. The next chapter states the overall aim and the specific objectives used to guide the design, implementation, and evaluation of the study.
