# ICACT 2026 — Compliance Report and Submission Blockers

Companion to `ICACT2026_paper_draft.md`. Read the **Blockers** section first.

---

## 1. Submission Blockers — the paper cannot be submitted until these are resolved

| # | Blocker | Why it blocks | Effort |
|---|---|---|---|
| **B1** | **No experimental results exist.** No evaluation harness, no results files, empty databases (0 tickets, 0 audit entries), 2 trivial health-check tests. | ICACT is a peer-reviewed conference. A paper with no Results section is desk-rejected. This is the single largest gap. | High — 2–3 weeks |
| **B2** | **Four fabricated references** in the interim report (verified absent from all databases). | Fabricated citations are research misconduct, not a formatting error. Detected easily by reviewers. | Done — removed in draft |
| **B3** | **Release-note metrics are unsupported.** 85% / 90% / 95% / 60% appear nowhere in the repository as measured artefacts. | Publishing unmeasured numbers is fabrication. | Must regenerate or drop |
| **B4** | **Interim report contradicts the implementation** on five factual points (see §2). | Reviewers cross-check claims against described systems. | Low — corrected in draft |
| **B5** | **ML model provenance unrecoverable.** No training script, no training data; label-encoder classes don't match system categories; models pickled under scikit-learn 1.5.1 but loaded under 1.7.2 (version-mismatch warning). | Cannot claim a model whose training data you cannot describe. | Medium — retrain with recorded protocol, or drop the claim |
| **B6** | **Blind-review status unconfirmed.** The CFP page does not state it. | Wrong anonymisation = desk rejection. | Trivial — check CMT |

---

## 2. Interim Report vs. Actual Implementation

Verified by direct inspection of source. **The right-hand column is what your code does.**

| Claim in interim report / release notes | Verified reality |
|---|---|
| "50+ safe actions" | **25** active (`action_executor_agent.py`); 2 more commented out. Tiers: 14 low, 8 medium, 3 high |
| "SLA Breach Predictor (Random Forest)" | **LinearRegression**, 3 features (`category_code`, `priority`, `word_count`), predicts resolution *hours* — a regression, not breach classification |
| "System Health Predictor (Random Forest)" | ✅ Correct — `RandomForestClassifier`, 100 trees, 4 features (cpu/ram/disk/temp), binary |
| "RAG Engine (ChromaDB) + LangChain" | **Neither is in the runtime path.** Live retrieval = `text-embedding-004` + NumPy cosine similarity in memory. ChromaDB/LangChain appear only in standalone `ingestion_script.py` |
| `ingestion_script.py` embeddings | ⚠️ Defaults to `USE_LOCAL_EMBEDDINGS=true` → **SHA-256-seeded pseudo-random vectors with no semantic meaning.** If you ever ingest with this path, retrieval is noise |
| "200 users, historical tickets, KB articles" | **5 users, 5 tickets, 6 KB articles, 4 conversations** (28 KB JSON) |
| "5 specialized agents" | ✅ Correct |
| "5 roles, RBAC, JWT + bcrypt, audit logging" | ✅ Correct — 5 roles, 24 permission constants, 90 assignments |
| "React 18 + Vite, FastAPI, SQLite, Docker" | ✅ Correct (~11,600 LOC backend) |

**Two of these are also code defects worth fixing regardless of the paper:** the hash-based embedding default, and the scikit-learn version mismatch on model load.

---

## 3. Recommended Figures and Tables

Six pages in IEEE two-column supports roughly **4 figures + 4 tables**. Prioritised:

### Must have

| ID | Content | Notes |
|---|---|---|
| **Fig. 1** | Layered architecture — frontend → API/RBAC → orchestration (5 agents) → services → data | Redraw from interim report Fig. p9. **Add a visual privilege boundary** around the Action Executor — that is the paper's thesis and the current diagram doesn't show it |
| **Fig. 2** | Remediation pipeline: intent → registry lookup → parameter validation → approval gate → execute → audit. Show rejection paths | New. This is your novelty; it needs its own figure |
| **Table I** | Agent responsibilities + privilege separation (untrusted input / may execute) | In draft. The two right-hand columns carry the argument |
| **Table VI** | **Adversarial containment results** by attack class and control that caught it | Headline result. Does not exist yet |

### Should have

| ID | Content |
|---|---|
| **Fig. 3** | Threshold sweep for retrieval cut-off — turns an arbitrary constant into a tuned parameter |
| **Table II** | Priority scoring factors and weights (transcribe exactly from `dataset_analyzer.py`) |
| **Table III** | Action registry: 6 categories × 3 risk tiers |
| **Table IV/V** | Classification and retrieval metrics |

### Drop

- The interim report's conversation-flow flowchart (p10) — superseded by Fig. 2
- The literature conceptual map (p16) — standard in a thesis, wastes a page in a 6-page paper

### Production requirements
- **Vector source** (draw.io/Inkscape/matplotlib) → export **PDF or EPS**, not PNG. Vector satisfies "300 DPI or above" unconditionally.
- Caption font **Times New Roman 8 pt**; captions below figures, above tables (IEEE).
- Tables as native Word tables — **never images** (checklist requires editable).
- Check legibility in greyscale; do not encode meaning in colour alone.

---

## 4. ICACT Formatting Checklist

Source: `conference-template-a4.docx` (standard IEEE A4 two-column) + the CFP checklist.

| Requirement | Status |
|---|---|
| Page limit: 6 pages | ⏳ Draft is ~4.5 pp; will reach ~6 with figures + results |
| Page size: A4 | ✅ Use the supplied template — do not use the US-Letter variant |
| Body font: Times New Roman 10 pt | ⚠️ Template default is 10 pt; **verify after pasting** |
| Figure/table/caption font: 8 pt | ⚠️ Set manually |
| Abstract ≤ 300 words | ✅ 283 |
| Keywords ≤ 5 | ✅ Exactly 5 |
| Format: PDF | ⏳ Export at the end; embed all fonts |
| Plagiarism ≤ 30% excl. references | ⏳ **Run Turnitin before submitting.** Text reused verbatim from the interim report will match your own prior submission — rewrite rather than paste |
| Citation style: IEEE numbered [1] | ✅ |
| Track selection | ⏳ Recommend **"Intelligent, Secure & Scalable Computing Systems"** — best fit for the security-architecture framing |
| Blind submission | ❓ **Verify on CMT.** If required: remove author block, anonymise "NSBM", cite own work in third person |
| Submission portal | CMT: `https://cmt3.research.microsoft.com/ICACT2026` |
| Deadline | ❓ **[INFORMATION NEEDED]** — not on the CFP page you provided |

### Word-transfer procedure
1. Open `conference-template-a4.docx`, **Save As** a new file — do not edit the template.
2. Replace content section by section, applying template styles (`papertitle`, `Author`, `Abstract`, `Keywords`, `Heading1`, `Heading2`, `BodyText`).
3. Paste as **plain text** to avoid importing Markdown formatting.
4. Delete the template's instructional text and the sponsor text box if unfunded.
5. Do not alter margins, column widths or line spacing.

---

## 5. Missing Information

### Critical — paper cannot proceed
1. **All experimental results** (E1–E5 in draft §V). Nothing exists.
2. **ML training provenance** — data, size, splits, validated metrics. Currently unrecoverable.
3. **Blind-review status.**

### Required before submission
4. Institutional email / ORCID.
5. Co-author and supervisor names, if any.
6. Submission deadline.
7. Exact priority-scoring weights transcribed into Table II.
8. LLM model version + access date (results are not reproducible without them).
9. Ethics approval reference, if human participants are used in evaluation.

### Recommended
10. **Expand the knowledge base.** Six articles will not support a credible retrieval evaluation, and a reviewer will say so.
11. Fix the hash-based embedding default in `ingestion_script.py`.
12. Retrain and re-pickle ML models under the current scikit-learn version.

---

## 6. Suggested Path Forward

Your **architecture and its security argument are genuinely publishable** — the privilege-separation
framing is a real contribution and, as far as the verified literature shows, under-explored in ITSM. The
implementation is substantial and real. What is missing is evidence.

**If the deadline allows 3+ weeks — full paper.**
Run E1 (classification, ~150 messages), E4 (adversarial safety, ~50–100 prompts), E5 (end-to-end vs.
advice-only). E4 is the highest value per hour invested: it directly tests the central claim and no
comparable system reports it. Expand the KB to 30–50 articles first so E2 is meaningful.

**If the deadline is tight — reposition.**
Submit as a **short / work-in-progress paper** built on E4 alone: "Constraining the Action Space:
Privilege Separation for Safe Autonomous Remediation." One rigorous safety experiment on a focused claim
is far stronger than five weak ones, and it is honest about maturity.

**What not to do.** Do not submit with the release-note metrics presented as results. They are
unsupported by any artefact in the repository, and a reviewer asking for the evaluation setup would
expose this immediately.
