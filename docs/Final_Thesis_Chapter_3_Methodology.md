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
