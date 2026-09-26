# Literature Search Record

## Purpose

This record documents how the working literature set for Chapter 3 was assembled. It supports a structured narrative review; it is not presented as a systematic literature review or meta-analysis.

## Search date and coverage

- Search performed: 26 September 2026
- Main publication period: 2019-2026
- Earlier foundational work retained where necessary: information-protection principles, levels of automation, autonomic computing, authorization scope, and configuration management
- Language: English
- Domains: IT support and AIOps, LLM agents, multi-agent systems, retrieval-augmented generation, AI risk management, human-AI interaction, runtime enforcement, tool security, access control, verification, rollback, and configuration control

## Discovery and verification sources

Candidate studies were located through keyword searches and then verified against primary or authoritative publication records from:

- ACM Digital Library and official ACM/ICSE conference records
- ACL Anthology
- NeurIPS proceedings
- Proceedings of Machine Learning Research
- MLSys proceedings
- IJCAI proceedings
- Microsoft Research and IBM Research publication records
- NIST publication records
- RFC Editor
- arXiv, primarily for discovery or when a formal publication page was unavailable

Search-result summaries, personal blogs, vendor marketing pages, Wikipedia, Reddit, and ResearchGate were not used as evidence in the chapter. They could assist discovery, but a primary publication record was required before a source was retained.

## Search concepts

The searches used combinations of the following terms:

- `IT support`, `incident troubleshooting`, `AIOps`, `root cause analysis`, `autonomous cloud`, `remediation agent`
- `large language model agent`, `multi-agent`, `ReAct`, `tool-augmented agent`
- `retrieval augmented generation`, `RAG evaluation`, `faithfulness`, `retrieval relevance`
- `agent safety`, `tool invocation safety`, `prompt injection`, `runtime enforcement`, `guard agent`
- `precondition`, `postcondition`, `verified tool execution`, `rollback`, `state verification`
- `risk adaptive automation`, `levels of automation`, `human approval`, `human AI interaction`
- `least privilege`, `scoped authorization`, `attribute based access control`, `configuration change control`
- `autonomic computing`, `MAPE-K`, `self-healing`

Representative exact searches included:

- `AutoTSG Learning and Synthesis for Incident Troubleshooting official paper`
- `RCAgent Cloud Root Cause Analysis autonomous agents official ACM paper`
- `AIOpsLab holistic framework evaluate AI agents autonomous clouds official paper`
- `RAGAS Automated Evaluation Retrieval Augmented Generation ACL`
- `AgentDojo prompt injection attacks defenses official paper`
- `AgentSpec customizable runtime enforcement safe reliable LLM agents official ICSE`
- `ToolGate Contract-Grounded and Verified Tool Execution official paper`
- `Towards Verifiably Safe Tool Use for LLM Agents ICSE official paper`
- `NIST AI Risk Management Framework official`
- `autonomic computing MAPE-K architecture IBM paper`
- `types and levels of human interaction with automation IEEE`
- `NIST security focused configuration management change control`

## Inclusion criteria

A source was included when it satisfied at least one of the following conditions and directly informed the research design or gap:

1. It studied IT incident troubleshooting, AIOps, root-cause analysis, or operational-agent evaluation.
2. It introduced or evaluated an agent architecture relevant to reasoning, tool use, or multi-agent coordination.
3. It introduced or evaluated retrieval grounding or RAG quality measures.
4. It provided empirical evidence about unsafe tool use, prompt injection, policy enforcement, or guardrails.
5. It specified preconditions, postconditions, runtime verification, recovery, or system-state control.
6. It provided authoritative guidance for AI risk management, authorization, least privilege, human oversight, or configuration change control.

Preference was given to peer-reviewed papers, standards, official government guidance, and official proceedings. Recent 2026 work was included where it was already formally published or accepted and directly relevant to verifiable agent tool use.

## Exclusion criteria

Sources were excluded from the core comparison when they were:

- marketing claims without a research method or evaluation;
- generic chatbot studies without operational tool use;
- predictive-maintenance studies unrelated to remediation after a reported incident;
- papers focused only on model content safety with no relationship to agent actions or tools;
- duplicates, superseded drafts, or secondary summaries where a primary record was available;
- inaccessible claims whose reported metrics could not be checked against an abstract, paper, standard, or official publication record.

## Selection limitations

The search was structured but not exhaustive. It did not use a preregistered protocol, formal database-export deduplication, forward/backward citation counts, or dual-reviewer screening. The literature set can therefore support a carefully bounded statement that the reviewed work provides limited evidence of the complete integration, but it cannot prove that no similar framework exists anywhere. This limitation must be retained in Chapters 3 and 6.

## Working source set

Twenty-five primary or authoritative sources are currently retained. Their provisional IEEE entries and links are recorded in `references_working.md`. Citation numbering remains provisional until all thesis chapters are consolidated.
