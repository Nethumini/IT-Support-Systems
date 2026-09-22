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

Tests: `cd backend && ../venv/bin/python -m pytest tests/ -q` — 315 passing.
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
| `services/execution/` | Drivers: `simulated`, `posix`, `hybrid`, `powershell`, `agent` |
| `services/execution/agent.py` | Runs an action on an enrolled machine and waits for the answer |
| `services/remediation_service.py` | Orchestrates propose → assess → approve → pre-check → execute → post-check → recover |
| `services/knowledge_service.py` | Solved problems become drafts; only a reviewer makes them searchable |
| `models/remediation.py` | Persistence plus the single-use approval token |
| `models/device.py`, `models/device_job.py` | Enrolled machines and the work queue for their agents |
| `api/endpoints/devices.py`, `agent_work.py` | Device administration; the two routes an agent uses |
| `agent/autoops_agent.py` | The program that runs on a user's machine |
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

## Endpoint agents (added 21-22 September 2026)

A remediation can now run on the machine that has the problem, not only on the
host running the backend.

* An administrator registers a machine at **Endpoint Devices**, which returns a
  device id and a secret shown **once**.
* The agent runs there: `python agent/autoops_agent.py` with
  `AUTOOPS_BACKEND_URL`, `AUTOOPS_DEVICE_ID`, `AUTOOPS_DEVICE_SECRET`. Full
  instructions in `agent/README.md`.
* The agent **asks** for work; the server never calls out to it. It receives an
  action id, never a command, and resolves it against the same catalogue the
  backend uses.
* The chat finds a user's machine by matching `owner_email` to the signed-in
  user. No agent means actions are refused, not silently run on the server.
  More than one machine means the user is asked which.

**Risk, approval, pre-check, post-check, rollback and audit did not change to
make this work.** That is the driver boundary doing its job, and it is worth
saying at a viva.

Proven on real Windows (`DESKTOP-2MDI0I9`) on 22 September 2026: chat on the
Windows browser, backend on the Mac, PowerShell executed on Windows, verified,
and the result explained back in the conversation.

### Two traps this cost a day to find

* **The Gemini SDK is synchronous.** Called from an `async` endpoint it holds
  the event loop and the whole server stops answering - including the agents'
  polls, so the machine about to run the remediation goes unreachable too.
  Every model call now goes through `run_in_threadpool` or `asyncio.to_thread`,
  and `tests/test_server_stays_responsive.py` guards it.
* **The browser gave up after 10 seconds.** A model call takes longer, and the
  server waits up to 60 seconds for a device. `remediationService` now sets
  120s on `execute` and `explain`; everything else keeps the 10s default.

## Recovery (22 September 2026)

Rollback used to be a claim rather than a path. The one contract that had a
rollback named `enable_startup_item`, which was in no catalogue and no driver,
so every attempt raised and the request escalated saying no rollback was
defined — which was not what had happened.

What changed:

* `disable_startup_item` now saves the startup command it removes (to an
  AutoOps registry key on Windows, to `startup_backup` in the simulator), and
  `enable_startup_item` restores it. Deleting the value outright, as before,
  made the advertised rollback impossible on a real machine.
* `_recover` post-checks the rollback against observed state and records
  `verified` beside the driver's `success`. Restored means verified, not
  reported. Anything else escalates and says why.
* The PowerShell driver could not read the `startup` scope at all, so on a
  real machine every startup remediation post-checked as inconclusive and no
  rollback could ever be verified there. It now reads the Run key and the
  AutoOps backup key, listing a disabled item as `False` rather than letting
  it vanish — a missing key means "cannot tell", which is a different answer
  from "turned off". `services` and `updates` are still unobservable on
  Windows, so a service restart cannot yet be verified there.
* Two evaluation cases reach the path: EV-31, where Teams re-registers itself
  so the disable completes and achieves nothing and the rollback restores the
  machine; and EV-32, where nothing was changed, so there is nothing to put
  back and the case escalates. Neither fakes a failure at the point of
  interest.

Evaluation now reports 6 rollback attempts and 3 verified restorations per
condition (B and C), instead of 0 of everything.

**Proven on real Windows on 22 September 2026.** A failed remediation was
rolled back on `DESKTOP-2MDI0I9` through the endpoint agent: real PowerShell
removed the Run entry, a stand-in launcher put it back the way Teams does, the
post-check read the actual registry and reported `verified_failure`, and the
rollback restored the entry and was itself verified against registry state.
Risk, approval, pre-check, post-check and audit were unchanged from the
simulated run — the driver boundary again.

`backend/demo_rollback.py` drives the whole path and prints every stage. With
no arguments it runs on the host; `--device <id>` runs it on an enrolled
machine. To stage the failure on Windows, add a `DemoApp` value to the Run key
with a background job that re-adds it every 100 ms, which is what a
self-re-registering launcher does.

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
- **A rollback is verified like any other action.** Recovery runs at the point
  where the machine is already in a state nobody asked for, so its exit code
  is the last thing that should be trusted. An unverified rollback escalates.
- **A rollback that is registered must exist.** Its action id needs a
  catalogue entry, a contract of its own and a driver that can run it.
  `tests/test_verification.py` checks all three.

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
