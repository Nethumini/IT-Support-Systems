# AutoOps AI: Viva Presentation Speech (15 minutes)

This speech is for **Final Viva.pptx** (slides 1–20, plus backup slides 23–26 for questions).

---

## How to use this speech

1. **Do not memorise every word.** For each slide, memorise the **memory hook** (3 short words). If you know the hook, the sentences come back.
2. **Speak calmly, not fast.** The speech is about 1,950 words, which is 15 minutes at a steady, clear pace. Rehearse once tonight with a timer. If you finish after 15:30, use the cuts in "If you are running late".
3. **Point at the slide.** Each slide has a 👉 line. It tells you what to point at. Pointing gives you time to breathe.
4. **Short sentences.** If you forget a line, say the hook sentence again and move on. The panel will not notice.

### The one sentence behind everything

> **"The AI can suggest a fix. Clear rules decide if it may run. The real machine proves if it worked."**

If your mind goes blank on any slide, say this sentence, then continue.

---

## Timing checkpoints

| Slide | Topic | Time | Clock at end |
|---|---|---|---|
| 1 | Title | 0:30 | 0:30 |
| 2 | Outline | 0:20 | 0:50 |
| 3 | Background | 0:50 | 1:40 |
| 4 | Research problem | 0:50 | 2:30 |
| 5 | Literature gap | 1:00 | 3:30 |
| 6 | Questions and objectives | 0:45 | 4:15 |
| 7 | Scope | 0:35 | 4:50 |
| 8 | Methodology (DSR) | 0:40 | 5:30 ✅ **checkpoint** |
| 9 | Data and ethics | 0:45 | 6:15 |
| 10 | Architecture | 0:50 | 7:05 |
| 11 | Risk model | 1:00 | 8:05 |
| 12 | Workflow | 0:50 | 8:55 ✅ **checkpoint** |
| 13 | Evaluation design | 0:45 | 9:40 |
| 14 | Finding 1: tests and retrieval | 0:40 | 10:20 |
| 15 | Finding 2: safety | 0:50 | 11:10 |
| 16 | Finding 3: faults and attacks | 0:50 | 12:00 ✅ **checkpoint** |
| 17 | Research questions answered | 0:45 | 12:45 |
| 18 | Contribution | 0:40 | 13:25 |
| 19 | Limitations | 0:35 | 14:00 |
| 20 | Conclusion | 0:40 | 14:40 |
| 22 | Thank you | 0:10 | **14:50** |

**If you are late at a checkpoint**, see "If you are running late" at the end.

---

## Slide 1: Title (30 s)

**Memory hook:** *Name → title → one sentence*

👉 Look at the panel, not the screen.

> Good morning, respected panel members. Thank you for being here today.
>
> My name is Tharinda Pathirana. I am a BSc Honours in Software Engineering student at NSBM Green University, and my supervisor is Ms. Thilini Bakmeedeniya.
>
> My research is called **"Context Aware Intelligent IT Support Systems: A Multi-Agent Framework with Risk Adaptive and Verifiable Remediation."** The system is called **AutoOps AI**.
>
> In one sentence: **the AI can suggest a fix, clear rules decide if it may run, and the real machine proves if it worked.**

---

## Slide 2: Outline (20 s)

**Memory hook:** *Six parts*

👉 Move your hand down the six items.

> My presentation has six parts. The problem, the literature and my objectives, the methodology, the design, the evaluation and results, and finally my contribution and conclusion.

---

## Slide 3: Background and motivation (50 s)

**Memory hook:** *Support → AI helps → but advice is not a fix*

👉 Point at the three boxes on the left, then at **4,000+** on the right.

> When a computer or network breaks, the IT team must find the cause, fix it, and check that it works again. Many problems repeat, so the same fixes are done again and again.
>
> A study called AutoTSG looked at **more than four thousand** troubleshooting guides at one large company. They were used a lot, but often incomplete and hard to keep up to date.
>
> Today, AI can help. A language model understands a problem in normal words, and RAG lets it search the company's own support articles.
>
> But here is the key point. **Advice is not the same as a safe fix.** An AI action can be wrong, not allowed, or impossible to undo. And a command that "succeeds" may still leave the problem there.

---

## Slide 4: Research problem (50 s)

**Memory hook:** *Two extremes → the middle → three difficulties*

👉 Point left, then right, then the middle box, then the three boxes at the bottom.

> Today we have two extremes.
>
> On the left: **recommendation only**. The AI gives text, and a person does every step. It is safe, but slow.
>
> On the right: **unrestricted AI execution**. The AI runs the commands it writes. It is fast, but it can be unsafe, and it can say "done" without checking.
>
> What we need is the **middle**: the AI's power to act should match the risk, and every fix should be proven on the device.
>
> At the bottom are three difficulties. Risk depends on context. An approval must match the exact action. And **"command finished" is not "problem solved."**
>
> So my research problem is: *how can an AI support system fix problems, while its power stays in line with the risk, and every fix is backed by the real system state?*

---

## Slide 5: Related work and research gap (1 min)

**Memory hook:** *Four groups → each one missing something → the gap is joining them*

👉 Point at each of the four boxes, and read only the red "Missing" line in each.

> I grouped the literature into four areas.
>
> **First, IT support and AIOps**, like AutoTSG and RCAgent. *Missing:* no risk-based authority, and the fix is not checked on the device.
>
> **Second, AI agents and retrieval**, like ReAct and RAG. *Missing:* a good answer is not permission to act.
>
> **Third, safety guards**, like AgentDojo and GuardAgent. They block risky tool calls. *Missing:* mostly just allow or deny. No graded approval, no verified recovery.
>
> **Fourth, verified execution**, like ToolGate. It uses pre- and post-conditions. *Missing:* not a full IT-support repair loop.
>
> So the gap: **the building blocks exist, but separately.** My contribution is not inventing each block. **It is joining them into one loop and testing that loop together.**

---

## Slide 6: Research questions and objectives (45 s)

**Memory hook:** *Join, Safe, Check, Find*

👉 Point at RQ1 to RQ4, then at O1 to O4.

> I asked four research questions. Remember them as **join, safe, check, find.**
>
> **RQ1, join:** how can evidence-based advice be joined with fixed, risk-based control?
> **RQ2, safe:** does the risk policy stop unsafe actions without asking for too many approvals?
> **RQ3, check:** how reliably are results checked, with rollback or escalation when a fix fails?
> **RQ4, find:** how well does retrieval find the right support article?
>
> My aim was to design, build and test a risk-adaptive and verifiable remediation framework. This gives four objectives: **investigate, design, implement and evaluate.** I will come back to all four at the end.

---

## Slide 7: Scope and significance (35 s)

**Memory hook:** *In, out, boundary*

👉 Point left column, middle column, then the "Research boundary" box.

> **In scope:** the AutoOps AI prototype, twenty-six registered actions with low, medium and high routes, approval, checks before and after, and rollback or escalation with an audit trail.
>
> **Out of scope:** free AI shell commands, automatic destructive actions, production scale, and usability claims, because I did not do a user study.
>
> My boundary: thirty-two scenarios, a simulator plus one real Windows 11 device, and one frozen code version.

---

## Slide 8: Methodology: Design Science Research (40 s)

**Memory hook:** *Build it, test it, fix it*

👉 Point along the five steps, then at the "Refinement in practice" box.

> I used **Design Science Research**, because my study solves a practical problem by building an artefact and testing it. The artefact is the **whole controlled workflow**, not just the AI model.
>
> There are five steps: identify, define, build, evaluate, refine. Then repeat.
>
> Here is a real example of refinement. On the real Windows device, I found that disk readings change a little by themselves, as Windows writes logs. So I changed the verification step to allow a small, measured difference before the final evaluation.
>
> The research is quantitative. No human participants, so no usability claims.

✅ **Checkpoint: about 5:30.**

---

## Slide 9: Data and ethics (45 s)

**Memory hook:** *30 – 32 – 30 – 1*

👉 Point at the four big numbers first.

> These are my four numbers: **thirty** knowledge articles, **thirty-two** test scenarios, **thirty** retrieval queries, and **one** real Windows 11 device.
>
> The thirty-two scenarios are eight low, twelve medium and twelve high risk. Twelve are unsafe to run automatically, six have injected faults, and five have no evidence.
>
> **Ethics:** no human participants. On the real device I used only a harmless test value, and raw startup commands never left the device.
>
> **Data quality:** I set every label *before* running anything. Because I wrote the labels myself, the results show the system follows its specification, not expert agreement. I say this clearly in my limitations.

---

## Slide 10: Architecture (50 s)

**Memory hook:** *Purple proposes, yellow decides, red line protects*

👉 Point at purple, then yellow, then trace the red dotted line with your finger.

> This is the architecture. Four layers: React interface, FastAPI application, SQLite database, and the driver layer that runs actions.
>
> **Purple** is the AI side: agents and retrieval. They can only **understand and propose.**
>
> **Yellow** is the deterministic side: risk engine, authorisation, state machine and verification. **Only this side can allow an action.**
>
> The **red dotted line** is the execution boundary. **AI text can never cross it.** The driver accepts only an action ID from a fixed list, never a command. So even if the AI is wrong or tricked, it cannot run an unknown command.

---

## Slide 11: Risk model (1 min)

**Memory hook:** *Five factors, three routes, rules only go up*

👉 Point at the formula, then each factor, then the three coloured routes.

> This is the heart of the design: how risk is scored.
>
> There are **five factors.** Each one is scored from 1, safe, to 3, risky.
>
> - **Impact:** how much harm the action can do. It has the biggest weight, 0.30.
> - **Diagnostic uncertainty:** how unsure the system is about the cause.
> - **Evidence weakness:** how weak the best matching article is.
> - **Irreversibility:** can we undo it?
> - **Affected scope:** only my device, or a shared resource?
>
> The score decides the route.
> **Low**, 1.60 or less: it can run automatically, but still after all the pre-checks.
> **Medium**, up to 2.20: it needs approval, with a **single-use token that lasts fifteen minutes** and is tied to the exact action, parameters and device.
> **High**, above 2.20: it is blocked and sent to an expert.
>
> And there are **safety rules that can only raise the risk, never lower it.** For example, missing evidence forces high risk.
>
> This gives my first idea: **weak evidence costs autonomy.** When the system is less sure, it gives itself less freedom.

---

## Slide 12: Controlled workflow (50 s)

**Memory hook:** *Seven steps, three endings*

👉 Run your finger along the seven boxes, then the three endings.

> This is how one request moves through the system, in seven steps.
>
> The user reports a problem. The system **retrieves** approved articles. It **proposes** an action from the registered list. It **scores** the risk and picks the route. It runs **pre-checks** and gets approval if needed. A restricted driver **runs** the action. Then the system **reads the real device** to verify.
>
> There are **three endings**:
> - Verified success → **completed.**
> - Failed, but there is a registered undo → **roll back, and verify the rollback too.**
> - No undo, or the rollback cannot be verified → **escalate to a human.**
>
> This is my second idea: **completion is not resolution.** A command finishing proves only that it ran.
>
> For retrieval, only articles with similarity above 0.70 are kept, and up to three are cited. If retrieval fails, the risk goes up.

✅ **Checkpoint: about 9:00.** *(If your live demo is inside these 15 minutes, do it here. See the note at the end.)*

---

## Slide 13: Evaluation design (45 s)

**Memory hook:** *Four tests, three conditions: A, B, C*

👉 Point at the four tests on the left, then the A, B, C cards.

> I evaluated in four ways: **518 automated tests**, a **comparative experiment**, a **retrieval test**, and **end-to-end tests** with attack cases and a real Windows device.
>
> The experiment compares three conditions:
> **A, advice only:** the AI suggests, nothing runs.
> **B, approve-all:** every action is approved, like a person who always clicks "yes".
> **C, risk-adaptive:** my full policy.
>
> Thirty-two scenarios, three conditions, three repeats: **288 records**, each on a fresh database.

---

## Slide 14: Finding 1: tests and retrieval (40 s)

**Memory hook:** *All passed, all found, but small*

👉 Point at the four numbers, then at "Honest limit".

> Finding one. **All 518 automated tests passed**, with no failures. All **20 focused safety tests** passed too.
>
> For retrieval, the correct article was ranked **first for all thirty queries.** So Hit at 1 is 100 percent, and the mean reciprocal rank is 1.0.
>
> But let me be honest. This is a **small, closed set**, and the category was given. So it shows retrieval works correctly on this set. It is not proof of general accuracy.

---

## Slide 15: Finding 2: safety without extra approvals (50 s) ⭐ most important

**Memory hook:** *Zero unsafe, twenty-four fewer, nineteen the same*

👉 Slow down. Point at each big number and pause one second after each.

> This is my **most important result.**
>
> **Zero of thirty-six.** Under my risk-adaptive policy, **no unsafe case ran.** Approve-all ran **all thirty-six.** *(pause)*
>
> **Twenty-four fewer approvals.** Approve-all needed ninety-six approvals. My policy needed seventy-two, because safe, low-risk actions could run without disturbing a person. *(pause)*
>
> So my policy sits **in the middle**: safer than approving everything, and more useful than doing nothing.
>
> And **nineteen of nineteen**: on the scenarios that both B and C ran, the verified result was exactly the same. So the policy did not make fixes worse. **It only stopped the unsafe ones.**

---

## Slide 16: Finding 3: faults, recovery and attacks (50 s)

**Memory hook:** *Every fault caught, none called success, attacks stopped*

👉 Point at the four numbers, then the rollback sentence, then the table row by row.

> Finding three. I injected faults: a command reports success, but nothing changed.
>
> **Every fault that reached execution was caught:** eighteen of eighteen under approve-all, fifteen of fifteen under my policy. **Zero faults were reported as success.** And all ninety-six audit traces were complete.
>
> **Rollback was verified in three of six.** That is correct, not a weakness. One scenario could be restored, and it was verified every time. The other had nothing to restore, so the system **escalated instead of pretending.**
>
> The table shows attack tests. A user typing "I already approved this" created **no** approval. A hidden instruction inside an article was treated as **data, not an action.** An unknown action name from the AI was **rejected by the allow-list.** And a fake success was **caught by the post-check.**

✅ **Checkpoint: about 12:00.**

---

## Slide 17: Answering the research questions (45 s)

**Memory hook:** *Join, safe, check, find: all answered*

👉 Point at RQ1 to RQ4 again (same hook as slide 6).

> So, back to my four questions: **join, safe, check, find.**
>
> **RQ1, join:** the AI proposes, and separate services decide, run and verify.
> **RQ2, safe:** zero unsafe runs, and twenty-four fewer approvals.
> **RQ3, check:** every executed fault was caught, and a rollback counted only when the restore was observed.
> **RQ4, find:** thirty of thirty queries found the right article first.
>
> This agrees with **AgentDojo**: untrusted text can mislead an AI, so control must sit **outside** the model. And it builds on **ToolGate**, adding risk-based authority and verified recovery.

---

## Slide 18: Contribution and objectives achieved (40 s)

**Memory hook:** *Parts are old, the loop is new*

👉 Point at the left box, then tick down O1 to O4.

> My contribution is **one implemented and evaluated loop** for IT support: approved evidence, explainable risk, graded approval, allow-listed execution, verified outcomes, and verified recovery.
>
> I want to be clear. **Each part already exists** in earlier work. **What is new is joining them into one loop, and testing it end to end.**
>
> All four objectives were achieved: **investigate, design, implement and evaluate**, as shown on the right.

---

## Slide 19: Limitations and future work (35 s)

**Memory hook:** *Each limit has a next step*

👉 Read across each row: limit → future work.

> My study has limits, and each one points to future work.
>
> I set the labels myself, so **independent experts** should check them and calibrate the weights.
> The data sets are small, so a **larger knowledge base** is needed.
> I used **one** Windows device, so **multi-device** trials are next.
> There was **no user study**, so a usability study is needed.
> And the device reports its own state, so **signed logs and device attestation** can be added.

---

## Slide 20: Conclusion (40 s)

**Memory hook:** *Problem, finding, contribution, final message*

👉 Point at each of the three boxes, then look at the panel for the last sentence.

> To conclude.
>
> **The problem:** AI can suggest IT fixes, but letting it act directly is unsafe, and a finished command is not a solved problem.
>
> **My strongest finding:** under my policy, no unsafe case ran, twenty-four fewer approvals were needed, every executed fault was caught, and rollback was verified on real Windows.
>
> **My contribution:** one evaluated loop, from evidence, to risk, to scoped approval, to restricted running, to observed verification, and to rollback or escalation.
>
> *(look at the panel)* My final message: **AI can help fix IT problems safely, when the power to act is held by clear rules, scoped approval, and checks on the real system.**

*(Skip slide 21, References. Just say "My main references are here" if you pass it, and go to slide 22.)*

---

## Slide 22: Thank you (10 s)

> Thank you very much for your attention. I am happy to answer your questions.

**Keep this slide on screen during questions.** Jump to a backup slide only when a question needs it.

---

## Cheat sheet: memorise only this

| # | Hook |
|---|---|
| 1 | Name → title → **suggest, decide, prove** |
| 2 | Six parts |
| 3 | Support → AI helps → **advice is not a fix** (4,000+ guides) |
| 4 | Two extremes → the middle → **"finished ≠ solved"** |
| 5 | Four groups, each missing something → **the gap is joining them** |
| 6 | **Join, Safe, Check, Find** → investigate, design, implement, evaluate |
| 7 | In, out, boundary |
| 8 | **Build it, test it, fix it** (disk reading example) |
| 9 | **30 – 32 – 30 – 1**, labels set before running |
| 10 | **Purple proposes, yellow decides, red line protects** |
| 11 | **Five factors, three routes, rules only go up** → weak evidence costs autonomy |
| 12 | **Seven steps, three endings** → completion is not resolution |
| 13 | Four tests, **A / B / C**, 288 records |
| 14 | **All passed, all found, but small** |
| 15 | ⭐ **Zero unsafe, twenty-four fewer, nineteen the same** |
| 16 | **Every fault caught, none called success, attacks stopped** |
| 17 | Join, safe, check, find: answered |
| 18 | **Parts are old, the loop is new** |
| 19 | Each limit has a next step |
| 20 | Problem, finding, contribution → **final message** |

## Numbers to know by heart

| Number | Meaning |
|---|---|
| **0.30 / 0.20 / 0.20 / 0.15 / 0.15** | Weights: Impact, Uncertainty, Evidence, Irreversibility, Scope |
| **1.60 / 2.20** | Low ≤ 1.60 < Medium ≤ 2.20 < High |
| **15 minutes** | Approval token life (single use) |
| **0.70** | Minimum similarity to keep an article |
| **26** | Registered actions (10 read-only, 2 with rollback) |
| **518 / 20** | Automated tests / focused safety tests, all passed |
| **32 × 3 × 3 = 288** | Scenarios × conditions × repeats |
| **0 of 36** | Unsafe cases run under my policy (B ran 36) |
| **72 vs 96** | Approvals: mine vs approve-all, **24 fewer** |
| **19 of 19** | Same verified result where B and C both ran |
| **18/18, 15/15** | Faults caught (B, C); **0** reported as success |
| **3 of 6** | Verified rollbacks (one restorable scenario × 3 repeats) |
| **30/30** | Right article ranked first; MRR 1.0 |

---

## If you are running late

- **Late at 5:30:** on slide 7, read only the "Research boundary" box. On slide 9, say only the four numbers and "labels set before running".
- **Late at 9:00:** on slide 13, skip the quality-control list. On slide 14, say only "518 passed, 30 of 30 found, but a small set."
- **Late at 12:00:** on slide 17, say "All four questions are answered, as the results showed" and move to slide 18.
- **Never cut slides 11, 15 or 20.** They carry your two ideas and your main result.

## If the live demo is in the same 15 minutes

The speech alone is about 14:50. A demo will not fit as well. Use the "running late" cuts above to save about 2 minutes, give a **2-minute demo after slide 12** (DEMO_SCRIPT.md, Step 4 only: one chat message, the risk card, and the "Verified" result), then continue from slide 13.

---

## Quick answers for likely questions (use the backup slides)

**"Why is C's resolution rate (63.2%) lower than B's (74.2%)?"** → *Slide 23.*
> "The two percentages have different denominators. B also ran twelve unsafe high-risk scenarios that my policy blocked. On the nineteen scenarios both ran, the results were exactly the same."

**"Your accuracy is 100%. Isn't that too perfect?"** → *Slide 23.*
> "Yes, and it is expected. A deterministic rule engine is compared with labels written from the same rules. So it shows specification conformance, not expert validation. Independent labels are my first piece of future work."

**"How is each factor scored?"** → *Slide 24.*
> "For example, evidence weakness comes from the best similarity score: 0.80 or more is strong, 0.70 or more is medium. It is then inverted, so strong evidence gives low risk. No AI scores its own proposal."

**"Why does C catch 15 faults, not 18?"** → *Slide 16 notes.*
> "The other three records are a high-risk scenario that my policy blocked before running, so there was nothing to catch."

**"Why 3 of 6 rollbacks?"**
> "Two scenarios reach rollback, each run three times. One could be restored, and it was verified all three times. The other had nothing to restore, so it correctly escalated."

**"What is new? These parts already exist."** → *Slide 25.*
> "Yes, each part exists. My table shows no single work covers graded authority, verification and verified recovery together for IT support. The new part is the integration and its evaluation."

**"What did you build yourself?"** → *Slide 26.*
> "The risk rules and five-factor model, the remediation states and tokens, the verification contracts, the drivers, recovery, audit and the evaluation harness. I reused standard frameworks like FastAPI, React and the Gemini SDK."

**"What if the agent on the device lies?"**
> "Then verification would believe it. That is a real limit. Fixing it needs hardware attestation, which is outside my scope. What I do keep is a full audit record tied to one revocable device credential."
