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

Tests: `cd backend && ../venv/bin/python -m pytest tests/ -q` — 518 passing.
`tests/test_api_remediation.py` drives the workflow through the HTTP API
(novelty 13.12); the rest are unit and service-level tests.
No real API key is needed: `tests/conftest.py` installs an offline placeholder
key before the app is imported (it overrides any key in `.env`), and refuses
every model call - a test that attempts one fails. A clean clone runs the suite
with no `.env`, no `data/processed` directory and no network. Live model and
retrieval evaluations (`run_retrieval_evaluation`, the chat) still need the
configured provider key.

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
* The PowerShell driver could not originally read the `startup` scope. Its
  first implementation represented an item only as enabled or disabled, which
  still allowed a no-op rollback to pass after an application re-registered
  itself. The current snapshot records live/backup existence and SHA-256
  fingerprints computed on the endpoint. A restore must reproduce the saved
  fingerprint and consume the backup. Raw startup commands do not leave the
  driver. `services` and `updates` are still unobservable on Windows, so a
  service restart cannot yet be verified there.
* Two evaluation cases reach the path: EV-31, where Teams re-registers itself
  so the disable completes and achieves nothing and the rollback restores the
  saved command in simulation; and EV-32, where nothing was changed, so there
  is nothing to put back and the case escalates. Neither fakes a failure at the
  point of interest.

Evaluation now reports 6 rollback attempts and 3 verified restorations per
condition (B and C), instead of 0 of everything.

**Historical Windows run on 22 September 2026.** Real PowerShell removed the
Run entry and the post-check detected that a stand-in launcher had put it back.
The recovery action also ran, but the old Boolean snapshot recorded only that
the item was enabled before and after it. That is not evidence that recovery
restored the saved command. Do not describe this run as verified restoration.
The fingerprint-based check added on 26 September requires a fresh Windows run
before that claim is defensible.

`backend/demo_rollback.py` drives the whole path and prints every stage. With
no arguments it runs on the host; `--device <id>` runs it on an enrolled
machine. To stage the failure on Windows, add a `DemoApp` value to the Run key
with a background job that re-adds it every 100 ms, which is what a
self-re-registering launcher does.

## Chat identity (23 September 2026)

The chat endpoints took `user_email` from the request body and required no
token. Anyone who could reach the backend could hold a conversation as another
person, list the machines registered to them, and raise remediation requests in
their name — which would have made the approval record prove nothing. The
`/chat/history`, `/chat/sessions/{email}` and `/chat/resume` routes were
readable by anyone at all.

Every chat route now requires a JWT and takes the actor from it; the body field
is kept so old callers do not break, and ignored. Conversations are readable by
the person who had them or by support staff. `frontend/src/api.js` used raw
`fetch` with no `Authorization` header, so it was changed to send the token —
`httpClient.js` was already doing this, `api.js` was the exception.

`tests/test_api_chat_auth.py` covers it, and costs no chat quota: every case is
decided before an agent runs.

Still open, and quality rather than safety: conversation memory is a process
dictionary keyed by email, not by session, so two browser tabs share one
thread, a restart loses context, and the database copy is never used to rebuild
it — the frontend resends the history instead, which also means the client can
rewrite what was said.

## What the chat may say (23 September 2026)

Reading one real conversation found three places where the system stated
something nobody had measured. All three are fixed, and all three are the same
mistake in different clothes.

* **The assistant narrated checks it had not run.** "I'm checking your disk
  space diagnostics now… your drive is indeed nearly at capacity" — while the
  risk layer had *blocked* that action for missing evidence. The system prompt
  now forbids claiming to check anything, stating a reading it was not given,
  or saying whether an action worked.
* **Retrieval searched only the last message.** "I have a meeting in 30
  minutes" returned articles on Teams audio and a frozen taskbar at 71-75% for
  a user whose disk was full — and those similarity scores become the
  evidence-quality factor, so the risk score was computed from evidence about
  the wrong problem. `retrieval_query` now searches what was first reported
  alongside the newest message. The evaluation is unaffected: the harness uses
  fixed citations, not chat retrieval.
* **An unknown outcome was explained as a known one.** The device never
  answered, the system said so correctly, and the explanation then said the
  temporary files were "still cluttered". The explain prompt forbade claiming
  the problem was *fixed* but not claiming it *persisted*.

Also: an action is no longer offered for a machine whose agent has been silent
for more than 90 seconds. It used to be offered, attempted, and then spend the
executor's full 60-second wait to arrive at "the outcome is unknown".

A second reading, 24 September 2026, found the same mistake in a new place. A
cleanup was refused three times because the machine had 20 GB free, and each
time the assistant replied that the user's storage was full and offered another
way to clean it. The cause: `explanation_prompt` never read `pre_check`, so a
blocked action reached the model as "Outcome: failed" and nothing else, and it
filled the gap with the reported problem. The refusal reason is now in the
prompt, with a rule that the checks decide what is a problem and the
explanation puts their finding into words rather than overruling it. The chat
prompt gained the matching rule: a refusal ends that line of enquiry, and
severity is not the model's to add.

**Resolved.** `_require_disk_actually_low` now fires below 20 GB free **or**
below 10% free. Absolute space is what a cleanup recovers, so it is still the
first test; the proportional arm exists because a large disk can hold 20 GB
free at 95% used, which leaves Windows short of room for updates and paging.
The machine that prompted it had 20.06 GB free and 94.7% used, and read as
fine to the old rule. Evaluation numbers are unchanged: the simulated machine
has 4.2 GB free, so the first arm fires as before.

## Is the action appropriate? (24 September 2026)

The disk refusal above was only possible because the disk cleanups had an
appropriateness precondition. Nothing else did. The network actions — the ones
that interrupt a connection or cost the user a restart — had none at all, so a
report of slow internet could have produced a Winsock reset and a reboot on a
machine whose network was fine. Six of twenty-six actions asked whether the
problem existed, and they were all about disk.

Now:

| Action | Runs only when |
| --- | --- |
| `flush_dns` | the resolver cache actually holds entries |
| `release_renew_ip`, `reset_network_adapter` | the machine has no connection |
| `reset_winsock` | the stack reports as degraded |

The Windows driver had to learn to see this. `connected` meant "this machine
has network interfaces", which is true of a laptop in a drawer; it now means an
interface that is up and holds a routable IPv4 address, so a 169.254 address —
what Windows assigns when DHCP got no answer — reads as not connected. DNS
cache size comes from `Get-DnsClientCache`.

**`reset_winsock` will not run on real Windows.** Stack integrity is not
readable cheaply, the field is therefore absent, and an unreadable
precondition refuses. That is fail-closed working as intended on the most
destructive action in the catalogue: an expert can still act outside the
system. Say it at a viva before someone finds it.

Evaluation numbers are unchanged, but one scenario had to be corrected to keep
them so: EV-15 reports "nothing connects to the network" and was running on a
machine that was online, which nobody could see until an appropriateness check
refused it. Scenarios can now declare `machine_state`, and EV-15 sets
`network_connected=False`. A scenario whose story and machine disagree is a
scenario that proves nothing.

`tests/test_chat_grounding.py` holds all of it, and calls no model.

## When the machine cannot be reached (24 September 2026)

A user whose machine is off, off the network or faulty can still open the chat
from their phone — it is a web app, not something installed on the broken
machine. What they could not get was a person. The chat said "I can still
advise you" and stopped there: no ticket, nobody told, no record.

There are two moments where this is established, and only the first was
handled at first. Testing on real hardware on 24 September 2026 found the
second: the agent was stopped *after* the action had been offered, so the
freshness check could not help — it had been answering a second earlier. The
action was sent, the executor waited its full minute, and the user was
correctly told the outcome was unknown. And it ended there.

Both now escalate, through `services/escalation_service.py`:

* **before acting** — the agent has not asked for work recently, so nothing is
  offered; and
* **during acting** — the machine never answered inside the executor's wait.
  `DeviceUnreachableError` makes that distinguishable from every other refusal,
  and the request records `execution_result.device_unreachable`.

Raising a ticket does not change the verdict: the outcome stays *unknown*, not
*failed*. What changes is that somebody now holds it.

An unreachable machine raises a ticket and assigns it:

* `device_offline` → HIGH priority, hardware, "Machine not responding — needs
  someone to look at it".
* `no_agent` → MEDIUM priority, software, a setup job.
* `choose_device` raises nothing. That is a question the user answers in their
  next message, not an escalation.

Escalation lives in its own service rather than in `remediation_service.py`:
whether a job reaches a human is operational, not part of the verified core,
and nothing there may change what risk, approval or verification decided.

`TicketService.create_ticket` does **not** assign — assignment is a separate
step reached when the assistant cannot resolve something itself, which is
exactly this. `assign_ticket` runs through `run_in_threadpool` because it calls
the model, and it falls back to rule-based assignment when that fails. Note the
two paths disagree on the key: the chooser returns `agent_email`, the fallback
returns `assigned_to`, so both are read.

A conversation that already has a ticket keeps it — the same problem does not
become two jobs.

When a user has more than one machine, the chat now says which are answering
and lists the silent ones first. Someone reporting a broken machine is usually
reporting the quiet one, and chatting from the one that still works.

## A ticket knows which machine (24 September 2026)

Tickets had no device field at all, so a technician opening one could not tell
which computer to go to — including the tickets raised automatically for
machines that had stopped answering, which said "not responding" in the text
and never named the machine.

`tickets.device_id` is now optional and filled from three places: the manual
form (a dropdown of the reporter's own machines, marking the silent ones), the
chat (the machine the conversation resolved), and the unreachable-device
escalation (the machine that went quiet). Optional on purpose — a password
reset or a VPN question is about no machine, and a required field would put
noise in every ticket to capture the few that need it.

When a machine *is* named it must be real and belong to the ticket's owner, or
the field tells a technician something untrue about where to go. Two related
fixes came with it: only support staff may raise a ticket in someone else's
name (it was taken from the request body), and the create endpoint no longer
turns its own refusals into 500s — `except HTTPException: raise` sits above the
catch-all.

Migration: `("tickets", "device_id", "VARCHAR")` in `migrations.py`, applied on
start. NULL means "not about one machine", which is true of every ticket raised
before the column existed.

## Rules that must not be broken

- **No LLM scores its own proposal.** Every risk number comes from a similarity
  score, a classifier confidence, or a static property of the action.
- **A driver takes an action id, never a command string.** The allow-list is
  meaningless otherwise.
- **The actor comes from the token, never from the request.** Any endpoint that
  acts for a person takes their address from the JWT. A body field named
  `user_email` is ignored where one still exists.
- **`inconclusive` is never reported as resolved.** If the system cannot tell,
  it says so — and it does not report it as unresolved either. An action nobody
  could observe proves nothing in either direction.
- **The assistant never claims to have measured anything.** It cannot see the
  machine. A reading may be repeated only if the system reported it into the
  conversation.
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
- **`restart_explorer` can never be reported as resolved.** It has no
  postcondition, because restarting the shell leaves nothing observable that
  separates a fix from a no-op, so every run ends `inconclusive` and
  escalates. Fail-closed and defensible, but say it before a panel finds it.
- **`updates` state is unreadable on Windows.** Pending updates need the
  Windows Update COM API, not a psutil reading, so an action in that scope
  post-checks as inconclusive on a real machine. `services` was the same until
  23 September 2026 and now reads through `psutil.win_service_iter`, which
  makes `restart_service` verifiable on real hardware. **Unmeasured:** whether
  service states drift on their own inside the second a read-only diagnostic
  takes. If `list_services` starts failing its no-change check on Windows,
  that is why, and the fix belongs beside the disk allowance — measured, as
  that one was.
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
