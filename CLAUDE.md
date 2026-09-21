# AutoOps AI — working notes

Undergraduate final-year research project (NSBM Green University). The thesis
draft is `Final Thesis draft - 28647.pdf`; the novelty brief is `novelty.md`.

**The thesis is the contract.** It states specific formulas, test cases and
measures that a viva panel has read. Before changing anything in the risk,
verification or RAG path, check what chapters 5 and 6 promise. Where code and
thesis disagree, say so and let the author choose which to change — do not
quietly pick one.

## The research contribution

Risk-adaptive and verifiable remediation. An LLM may *propose* a fix; it never
decides whether the fix may run, and never decides whether it worked.

Two claims are being defended:

1. **Weak evidence costs autonomy.** A poor knowledge-base match raises the
   risk score, which can push a normally-automatic action into needing
   approval.
2. **Completion is not resolution.** A command exiting zero proves only that it
   ran. Post-action verification reads actual system state.

## Setup (macOS)

System Python is 3.14; the pinned dependencies need 3.12.

```bash
uv venv venv --python 3.12
uv pip install --python venv/bin/python -r requirements.txt
cd backend && ../venv/bin/python init_db.py
```

Run: `./run.sh` and `./run-frontend.sh` (bash ports of the repo's PowerShell
scripts). Login `admin@acme.com` / `admin123`.

Tests: `cd backend && ../venv/bin/python -m pytest tests/ -q` — 237 passing.
No API key needed.

Evaluation: `cd backend && ../venv/bin/python -m evaluation.run_evaluation` —
prints the results table, writes CSV and JSON to `evaluation/results/`. Calls
no chat model, so it costs no quota and repeats identically.

## Architecture of the contribution

Each layer is separately testable; that is deliberate.

| Module | Does |
| --- | --- |
| `services/risk_engine.py` | Five-factor weighted scoring, thresholds, overrides. Pure Python, no DB, no LLM |
| `services/risk_signals.py` | Turns retrieval scores and classifier confidence into the five factors |
| `services/verification.py` | Per-action contracts: preconditions, postconditions, rollback |
| `services/execution/` | Drivers: `simulated`, `posix`, `hybrid`, `powershell` |
| `services/remediation_service.py` | Orchestrates propose → assess → approve → pre-check → execute → post-check → recover |
| `services/knowledge_service.py` | Solved problems become drafts; only a reviewer makes them searchable |
| `models/remediation.py` | Persistence plus the single-use approval token |
| `evaluation/` | Labelled scenarios, harness, metrics |

### The risk formula is fixed by the thesis (5.3.3)

```
S = 0.30*I + 0.20*C + 0.20*E + 0.15*R + 0.15*A      each factor 1-3
```

Confidence and evidence quality are stored positively (3 = best) and inverted
only inside the calculation: `C = 4 - confidence_rating`. Do not replace this
with a simpler scheme.

Override rules beat the score and can only raise it: missing required evidence,
privileged security action, irreversible change to a shared resource, no
rollback on a critical resource, and the action catalogue's own risk as a floor.

Bump `RiskPolicy.version` whenever a weight or threshold changes — every
assessment records the version that produced it.

## Rules that must not be broken

- **No LLM scores its own proposal.** Every risk number comes from a similarity
  score, a classifier confidence, or a static property of the action.
- **A driver takes an action id, never a command string.** The allow-list is
  meaningless otherwise.
- **`inconclusive` is never reported as resolved.** If the system cannot tell,
  it says so.
- **A knowledge draft is never retrievable.** Only approved articles are
  searchable, or the system grounds answers on its own unreviewed guesses.
- **Approval is bound to the exact action and parameters.** Changing either
  invalidates the token and forces reassessment.
- **Read-only diagnostics require no evidence.** Requiring it would be circular
  — reading state is how evidence gets gathered.
- **Fail closed.** If risk assessment fails, an action is marked not executable,
  never executable by default.

## Environment

`backend/.env`:

- `EXECUTION_DRIVER` — `hybrid` for daily work (real read-only diagnostics of
  the host, simulated changes), `simulated` for evaluation and fault injection,
  `powershell` only on Windows.
- `GEMINI_MODEL` — the free tier allows **20 requests per day per model**, so
  roughly 7-10 chat messages. Quota is per model: switching model gives a fresh
  allowance. Do not rehearse a demo on the day of the viva.
- `EMBEDDING_MODEL` — `models/gemini-embedding-001`. `text-embedding-004` no
  longer exists on this API.

## Known limitations

- **Developed on macOS; the action catalogue is PowerShell.** The simulated and
  hybrid drivers exist because of this. Since 21 September 2026 the catalogue
  has also been run for real on Windows through the endpoint agent, so thesis
  6.2's "isolated Windows test environment" is now defensible for the
  demonstration. The **evaluation** still runs on macOS with the simulated
  driver, because repeatable fault injection needs it — keep the two claims
  separate when writing up.
- **Diagnostics can now target another machine.** `services/execution/agent.py`
  plus the agent in `agent/` run an action on an enrolled device and report the
  state they observed. Risk, approval and verification did not change to make
  this work, which is the driver boundary doing its job. Without a device id a
  remediation still runs on the host, as before.
- **A device reports its own state, and verification believes it.** A
  compromised agent could claim a fix that did not happen. Closing that needs
  attested measurement and is outside this project; what the system does keep is
  an audit record tied to one revocable device credential.
- **Evaluation labels were author-assigned.** Risk-classification accuracy of
  1.0 therefore shows the code matches its own specification, not that it
  matches expert judgement. Thesis 6.3 requires independent labelling; until
  that happens, report it as a consistency check.
- **`/api/v1/actions/*` is legacy but no longer unauthenticated.** Every
  endpoint requires a JWT and takes the actor from it; a `user_email` sent by
  the client is ignored. It still runs actions without scoring them first or
  verifying the outcome, so `/api/v1/remediation/*` remains the verified path.
  The frontend no longer calls the legacy route for approve or execute.
- **Only 30 knowledge-base articles**, all Windows-oriented, in
  `backend/data/raw/ticketing_system_data_new.json`.

## Thesis corrections still outstanding

Full list with exact replacement wording: `THESIS_CORRECTIONS.md`
(live editable copy: https://claude.ai/code/artifact/RrDXPcHo75FSFpjgdAaMrh)

The substantial one: chapters 5 and 6 describe **ChromaDB** as the retrieval
store in five places, and LangChain as the retrieval framework. Neither is used
— retrieval is in-memory over the JSON knowledge base. Everything else is a
sentence: the embedding model name, "50+ safe operations" (actually 25),
"isolated Windows test environment", and the scikit-learn contradiction.

## Style

Match the surrounding code. Explain *why* in comments, not *what*. The author
is a non-native English speaker working under time pressure — in chat, lead
with the answer in plain words, give one next step, and keep it short.
