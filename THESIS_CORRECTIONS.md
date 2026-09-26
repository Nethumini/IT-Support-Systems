# Thesis corrections needed

> **Planning note (26 September 2026):** This file is a detailed correction
> register and was originally verified against an older commit. Use
> `THESIS_RESTRUCTURING_PLAN.md` for the approved six-chapter plan and
> `THESIS_COMPLETION_CHECKLIST.md` to decide whether the thesis is complete.
> Re-verify all implementation counts and evaluation values against the final
> frozen commit before inserting them into the thesis.

Every place the thesis says something the code no longer does, with the current
wording and a suggested replacement. One item is substantial; the rest are
minutes each.

Live version (editable, with checkboxes):
<https://claude.ai/code/artifact/RrDXPcHo75FSFpjgdAaMrh>

Thesis file: `Final Thesis draft - 28647.pdf`
Verified against commit `86eba07`, 20 September 2026.

---

## 1. ChromaDB — the one that needs a decision

The thesis describes ChromaDB as the retrieval store on **pages 41, 42, 46, 47
and 51**, and LangChain as the retrieval framework in Table 5.2 and 5.5.2.

**The application uses neither.** Verified at commit `86eba07`:

- Nothing in `backend/app/` imports `chromadb` or `langchain`. The only mention
  of LangChain is a comment in `app/main.py:15`.
- `ingestion_script.py` does build a Chroma store, but no code path in the
  running application opens it — only `setup.ps1` and `deploy.sh` invoke the
  script, as a separate step.
- That store is built with **hash-based embeddings**: a SHA-256 digest seeds a
  random vector (`ingestion_script.py:34-66`). The vectors carry no semantic
  meaning, so even if the application queried the store, retrieval would not
  work.
- Real retrieval is `DatasetAnalyzer.find_similar_issues`
  (`app/services/dataset_analyzer.py:232`), in memory over the JSON knowledge
  base, using Gemini embeddings and cosine similarity.

This is the only correction a reviewer could call a misrepresentation rather
than a slip, because chapter 5 claims retrieval behaviour the code lacks.

**Decision taken: Option A.** Reasons recorded below in case the panel asks.

### Option A — change the thesis (recommended, ~1 hour)

With 30 articles an in-memory retriever is the right engineering choice, and
saying so is stronger than adding a vector database to match a sentence.

| Page | Current | Replace with |
| --- | --- | --- |
| 41 | "embeddings, ChromaDB retrieval and evidence-linked diagnosis" | "embeddings, semantic retrieval over the approved knowledge base, and evidence-linked diagnosis" |
| 42 (5.3.2) | "converted with the text-embedding-004 model and stored in ChromaDB. At query time, semantic retrieval is filtered by environment and approval status." | See the full replacement paragraph below. |
| 46 (Table 5.2) | "ChromaDB + text-embedding-004 — Semantic knowledge retrieval" | "Google gemini-embedding-001 — Semantic knowledge retrieval over the approved article set" |
| 46 (5.5.2) | "LangChain supports retrieval and agent composition, while ChromaDB stores document vectors." | "Retrieval and agent composition are implemented directly against the Gemini SDK. Article vectors are held in an in-memory index and cached per process." |
| 47, 51 | ChromaDB listed among integrated components | "the knowledge retrieval service" |

#### Replacement paragraph for 5.3.2

Paste this in place of the current sentence. Every clause is something the code
actually does, so each one is defensible under questioning.

> Article text is converted to vectors with the `gemini-embedding-001` model and
> held in an in-memory index, cached per process. At query time the user's
> description is embedded as a query vector and compared by cosine similarity
> against every approved article; a small bonus is added where the classifier's
> category agrees with the article's category, and matches above a calibrated
> threshold of 0.70 are returned, ranked by similarity weighted with prior usage.
> Category agreement is a ranking hint rather than a filter, because the
> classifier and the knowledge base draw their labels from different
> vocabularies. Drafts awaiting review are never indexed, so the system cannot
> ground an answer on an unreviewed fix of its own. The similarity score of the
> best match is carried forward as the evidence-quality factor in the risk
> assessment, which is the mechanism by which a weak retrieval reduces
> permitted autonomy.

**Two claims in the current sentence must not survive the rewrite:**

1. **"filtered by environment"** — there is no environment filter anywhere, and
   the 30 knowledge-base articles have no environment field (their keys are
   `id`, `title`, `category`, `issue_pattern`, `summary`, `resolution_steps`,
   `last_resolution`, `used_in_tickets`). Option B would not rescue this claim
   either; it would need the dataset re-labelled. Delete it.
2. **"filtered by ... approval status"** — this one is real, but it works by
   inclusion, not filtering: `load_approved_articles`
   (`dataset_analyzer.py:51`) merges only reviewer-approved learned articles
   into the index. The wording above states it accurately.

### Option B — change the code (rejected, and why)

Point `ingestion_script.py` at real Gemini embeddings and make `DatasetAnalyzer`
query Chroma. Rejected for three reasons, in increasing order of seriousness:

1. **It cannot save the 5.3.2 sentence.** The environment-filtering claim fails
   for lack of metadata, not for lack of a vector store.
2. **It breaks the knowledge learning loop.** Approved articles are merged into
   the index at runtime; the ingestion script deletes and rebuilds the store
   (`shutil.rmtree`). Learned knowledge would be wiped on every re-ingest unless
   write-on-approval plumbing were added.
3. **It touches the evidence path.** Retrieval similarity feeds
   `evidence_quality` in `risk_signals.py:58`, which feeds the risk score.
   Re-plumbing retrieval risks moving the chapter 6 evaluation numbers that are
   already written up.

At 30 articles, a vector database is over-engineering. That is the answer to
give if a panel member asks why ChromaDB was dropped.

### LangChain has the same problem

Table 5.2 and 5.5.2 credit LangChain for retrieval and agent workflow. Nothing
in `backend/app/` imports it. Remove it from the technology table, or mark it as
a declared dependency not used in the final implementation.

Note that `requirements.txt` still pins `langchain`, `langchain-chroma` and
`chromadb`, and a stale 2 MB `backend/data/processed/chroma_db/` sits on disk.
These do not affect the thesis wording, but they do mean the repository
currently corroborates the sentence being corrected. Worth a separate cleanup
commit if time allows.

---

## 2. Small factual fixes

### Page 9, Table 1.1 — action count

- **Says:** "Whitelisted system action management (50+ safe operations)"
- **Actual:** 26 actions (25 until `enable_startup_item` was added on
  22 September 2026 so that the registered rollback could actually run)
- **Change to:** "26 whitelisted operations, each with defined preconditions,
  postconditions and rollback availability"

A stronger claim than a bigger number. Every one of the 26 has a verification
contract, and the two figures are checked against each other by a test, so
the number is worth quoting exactly rather than rounding up.

### Page 48, section 6.2 — test environment

**Largely resolved on 21 September 2026 by running on real Windows.** The
sentence still needs a small change, but for a different reason than before.

- **Says:** "The test plan uses an isolated **Windows** test environment and
  predefined, non-destructive action adapters."
- **Was:** development and evaluation both ran on macOS through a simulated
  driver, so "Windows" was simply untrue.
- **Now:** the catalogue has been executed on an isolated Windows machine
  (`DESKTOP-2MDI0I9`) through the endpoint agent, with the real PowerShell
  driver. The remaining inaccuracy is narrower: the **evaluation** still runs on
  macOS with the simulated driver, because controlled fault injection and exact
  repeatability require it.
- **Change to:** "The test plan uses an isolated Windows test environment with
  predefined, non-destructive action adapters, reached through an endpoint
  agent. Execution is routed through a driver layer, so the same risk,
  approval and verification logic runs unchanged against either target. The
  comparative evaluation uses the simulated driver, which allows controlled
  fault injection and exact repeatability."

Page 25 already says "or state-transition simulator", so chapter 3 is already
consistent. Only 6.2 is absolute.

**Worth reporting in chapter 6 as a finding.** Two defects in post-action
verification appeared only on real hardware, and both passed in simulation:

1. The Windows driver snapshotted *all* system state rather than the scope the
   action's contract declares, so a read-only diagnostic was compared against
   the process list. Windows starts and stops processes continuously, so the
   check failed every time.
2. Even with the scope narrowed, free disk space moved about 10 MB during the
   second the command ran, as the operating system wrote logs. Exact equality
   therefore failed on a live machine.

Both are fixed, with regression tests. The point worth making is that a
verification mechanism validated only against a simulator can be systematically
wrong in the one setting it exists for, which is an argument for the real-target
run rather than against it.

### Page 46, section 5.5.2 — scikit-learn

- **Says:** "scikit-learn predictive models from the earlier concept are excluded"
- **Actual:** `requirements.txt` still installs it; `services/predictive_service.py`
  and `models/ml/` still exist
- **Fix:** delete that code, or add "Predictive components from the earlier
  concept remain in the repository as inactive legacy code and are excluded
  from the evaluation."

### Embedding model, everywhere

`text-embedding-004` was withdrawn and now returns 404. Replace with
`gemini-embedding-001`. Covered by the ChromaDB rewrite above.

### Docker Compose

Table 5.2 lists it and `docker-compose.yml` exists. No change needed.

---

## 3. Things to add

Built and tested, not yet in the thesis. Additions in your favour.

**The driver layer (5.3.4).** Execution routes through interchangeable drivers
— `simulated`, `posix`, `hybrid`, `powershell` — and the layers above cannot
tell which is in use. This is the clean answer to "how did you test destructive
actions?"

**Knowledge learned from solved problems (chapter 5).** A verified fix for a
problem no article covered becomes a draft. The draft has no article id and is
not retrievable until a reviewer approves it. Same human-in-the-loop principle
as risky remediation, applied to what the system may learn.

**The evaluation harness (6.4.3).** 30 labelled scenarios plus two recovery
cases, three conditions, three repeats, deterministic, calls no language model.
Reproducibility was confirmed: 96 of 96 cases stable.

⚠️ **Decision needed.** The thesis fixes the set at thirty. EV-31 and EV-32
were added on 22 September 2026 because none of the thirty ever reached the
rollback path, so rollback frequency and outcome — which novelty 14 requires
— were being reported from zero attempts. Either say "thirty labelled
scenarios for retrieval and risk analysis, with two further cases exercising
recovery", or drop the two and report rollback as untested. The first is
recommended and is what the table above assumes. `tests/test_evaluation.py`
keeps the two counts separate so either wording stays checkable.

**Recovery, and what verifies it (5.3.4 or chapter 5).** A failed remediation
is rolled back where the catalogue holds a true inverse, and **the rollback is
itself post-checked against observed state**. This is the contribution's own
principle applied to its recovery path: a rollback reporting success is not a
machine restored, and an unverified rollback escalates rather than closing the
case. Two of the 26 actions have a registered rollback; the rest escalate,
which is a deliberate refusal to improvise an undo.

**Historical real-hardware run requires a narrower claim.** A rollback path ran
through the endpoint agent on Windows on 22 September 2026. It demonstrated
real PowerShell execution and detection that the requested disable had not
held. However, the old snapshot stored only whether the startup item was
enabled. Because the item was enabled both before and after recovery, that
record does not prove that the rollback restored the original command. It must
not be cited as verified restoration.

On 26 September 2026, startup state was strengthened with endpoint-computed
fingerprints of the live and saved command values. The new postcondition
requires the restored fingerprint to match the saved fingerprint and requires
the backup to be consumed. A no-op rollback therefore fails instead of being
reported as restored. A new real-Windows run is still required before Chapter
5 can claim verified restoration on hardware.

Two defects surfaced only because the path was finally exercised, and both are
worth reporting in chapter 6 as findings:

1. The registered rollback named an action that was not in the catalogue, so
   every attempt raised and the request escalated saying "no safe rollback is
   defined" — which was untrue. A path that is never exercised is not a path.
2. The Windows driver could not read startup state at all, so on a real
   machine every startup remediation post-checked as inconclusive and no
   rollback could ever be verified there. This is the same lesson as the two
   verification defects already recorded for 6.2: a mechanism validated only
   against a simulator can be systematically wrong in the setting it exists
   for.
3. The first readable startup snapshot represented each item only as enabled
   or disabled. A self-re-registered item was already enabled before rollback,
   so a rollback that did nothing could satisfy the old postcondition. The
   fingerprint-and-backup-consumption checks correct this, but still require a
   fresh real-device run.

**Results (chapter 7)** — 32 scenarios x 3 repeats, run on 22 September 2026
with the recovery cases included (the previous table, 30 scenarios and 90 runs
per condition, is superseded):

| Measure | A (advice) | B (uniform gating) | C (risk-adaptive) |
| --- | --- | --- | --- |
| Runs | 96 | 96 | 96 |
| Unsafe cases executed | 0 | 36 | 0 |
| Unsafe prevention rate | 1.00 | 0.00 | 1.00 |
| Actions executed | 0 | 93 | 57 |
| Verified resolved | 0 | 69 | 36 |
| Faults reported as success | 0 | 0 | 0 |
| Required human approval | 0 | 96 | 72 |
| Pre-check failures | 0 | 3 | 3 |
| Rollback attempted | 0 | 6 | 6 |
| Rollback succeeded (verified) | 0 | 3 | 3 |
| Audit completeness | 1.00 | 1.00 | 1.00 |

Lead with this: uniform gating (B) put a human in the loop for every action and
still executed all 36 unsafe cases, because a reviewer who confirms everything
confirms the bad ones too. Risk-adaptive routing (C) blocked all 36 **and**
asked for 24 fewer approvals — safer and less work.

Re-run before submitting so the numbers match the final commit.

---

## 4. Limitations to state

Stating these yourself is worth more than having a panel find them.

### Labels were author-assigned

The evaluation reports risk-classification accuracy of **1.00**. Do not present
that as a finding. The reference labels were written by the same person who
wrote the risk engine, so a perfect score shows internal consistency, not
agreement with expert judgement.

6.3 already requires independent labelling. Either:

1. **Get the labels re-done independently** by a supervisor or classmate, using
   the five factors without seeing system output — then report inter-rater
   agreement; or
2. **Say what they are:** "Reference labels were author-assigned; the reported
   accuracy is a consistency check between specification and implementation
   rather than a validity measure."

Option 1 is much stronger and costs one person an hour.

### Diagnostics read the host, not the user's device

> Diagnostics currently read the host running the backend. A production
> deployment requires a lightweight endpoint agent so that each user's own
> device is inspected. The driver interface is designed for this: an endpoint
> agent would be one further driver, with no change to the risk, approval or
> verification layers.

The last sentence matters — it shows the architecture anticipated the gap.

### No real users

Controlled scenario testing, not a field study. Cite the Design Science framing
already in chapter 3.

### Free-tier API limits

The Gemini free tier allows 20 requests per model per day. This is why the
evaluation harness avoids the chat model entirely — it explains a design choice
rather than admitting a weakness.

---

## 5. Checklist

Hardest first.

- [ ] **ChromaDB** — Option A chosen; rewrite pages 41, 42, 46, 47, 51
- [ ] **Page 42, 5.3.2** — paste the replacement paragraph; delete the
      "filtered by environment" claim (no such field exists)
- [ ] **LangChain** — remove from Table 5.2 and 5.5.2, or mark unused
- [ ] **Embedding model** — `text-embedding-004` → `gemini-embedding-001`
- [ ] **Page 9, Table 1.1** — "50+ safe operations" → 26 with contracts
- [ ] **Page 48, 6.2** — keep "Windows" (it is now true) but say the
      evaluation uses the simulated driver, and add the endpoint agent
- [ ] **Page 46, 5.5.2** — resolve the scikit-learn contradiction
- [ ] **Add** the driver layer to 5.3.4
- [ ] **Add** knowledge learned from solved problems to chapter 5
- [ ] **Add** the implemented evaluation harness to 6.4.3
- [ ] **Add** the results table to chapter 7
- [ ] **Add** recovery and the verified rollback to chapter 5, and the two
      rollback cases to 6.4.3
- [ ] **Decide** the scenario wording: thirty labelled cases plus two recovery
      cases, or thirty and rollback reported as untested
- [ ] **Add** the four limitations above
- [ ] **Decide** on independent labelling — the only item needing another person

### Before submitting

- [ ] Re-run the evaluation so numbers match the final commit
- [ ] Record the commit hash beside the results table
- [ ] Check no remaining sentence claims something the code does not do

---

## What is already correct

Do not change these by mistake.

| Thesis says | Status |
| --- | --- |
| `S = 0.30I + 0.20C + 0.20E + 0.15R + 0.15A`, factors 1–3 | Implemented exactly |
| `C = 4 - confidence_rating` inversion | Implemented |
| Override rules dominate the score | Implemented, five of them |
| Single-use token bound to action, target, parameters, and expiry; approver identity stored separately | Implemented and tested |
| Changing an action or parameter invalidates approval | Implemented and tested |
| Pre-action and post-action verification | Implemented |
| Test cases TC04, TC06, TC07, TC08, TC09 | Each has a test named after it |
| Audit trail across every decision point | Implemented |
| Five specialised agents (Table 1.1) | All five exist |
| React, FastAPI, Gemini, SQLite, Docker Compose | Correct |
