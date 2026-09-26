# Chapter 2 - Objectives

> **Draft status:** First restructured draft. Confirm the aim and objectives against the approved proposal and supervisor feedback before treating them as final.

## 2.1 General Objective

The general objective of this research is to design, implement, and evaluate a context-aware, risk-adaptive, and verifiable remediation framework for safer AI-assisted IT support.

## 2.2 Specific Objectives

The specific objectives are:

1. **To investigate** existing intelligent IT-support, multi-agent, retrieval, authorization, verification, and recovery approaches and identify the gap addressed by their integration within a controlled remediation workflow.

2. **To design** an explainable remediation architecture that uses contextual risk to select an appropriate level of execution authority and restricts remediation to supported, validated actions.

3. **To implement** the proposed framework with evidence retrieval, deterministic risk assessment, scoped approval, pre-action checks, controlled execution, post-action verification, rollback or escalation, and auditable decision records.

4. **To evaluate** the implemented framework using labelled remediation scenarios, comparative authorization policies, retrieval-quality tests, injected failure conditions, repeatability analysis, end-to-end workflow cases, and limited execution against a real endpoint.

## 2.3 Relationship Between Objectives and Evidence

Table 2.1 defines how achievement of each objective will be demonstrated. It prevents an implemented feature from being treated as an achieved research objective without corresponding evidence.

**Table 2.1. Objective-to-evidence mapping**

| Objective | Principal method | Evidence required to claim achievement |
| --- | --- | --- |
| O1 - Investigate | Structured literature search and comparative synthesis | Search description, comparison matrix, identified gap, and design implications |
| O2 - Design | Requirements analysis and architecture/design specification | Architecture, risk model, authorization states, action contracts, data/workflow design, and design rationale |
| O3 - Implement | Iterative artefact development and automated verification | Final implementation version, functional test output, selected traces, and interface/endpoint evidence |
| O4 - Evaluate | Scenario comparison, retrieval evaluation, fault injection, repeatability analysis, end-to-end cases, and endpoint execution | Final metrics with denominators, retrieval error analysis, recovery results, raw evidence, and threats-to-validity analysis |

The first objective establishes the research context and gap. The second converts the findings into a design. The third produces the research artefact. The fourth determines what can reasonably be concluded from the implemented artefact under the stated evaluation conditions.

## 2.4 Chapter Summary

This chapter defined one general objective and four specific objectives covering investigation, design, implementation, and evaluation. The objectives are intentionally measurable and are linked to evidence that must appear in the later chapters. Chapter 3 reviews the literature required to establish the conceptual basis, compare related approaches, and justify the integration gap addressed by the framework.
