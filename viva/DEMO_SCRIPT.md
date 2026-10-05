# AutoOps AI: Viva Demo Script (5–10 minutes)

A step-by-step guide for the live demonstration.
For each step you get **what to click**, **what to say**, and **what the panel should notice**.

---

## The one idea to remember

> **"The AI can suggest a fix. It never decides if the fix is allowed to run, and it never decides if the fix worked."**

Everything in the demo shows this sentence in action. If you get nervous, come back to it.

The two claims you are proving:

1. **Weak evidence costs autonomy.** If the system is not sure about the problem, the risk goes up, so a person must approve the fix.
2. **Completion is not resolution.** A command that finishes without error only proves it *ran*. The system checks the real machine afterwards to see if the problem is really fixed.

---

## Demo plan at a glance

| # | Step | Time | What it proves |
|---|------|------|----------------|
| 0 | Start everything (before the panel arrives) | 0:00 | — |
| 1 | Short introduction | 0:30 | The problem and the idea |
| 2 | Log in and show the dashboard | 0:30 | It is a working system |
| 3 | Show the Windows machine and its agent | 1:00 | The fix runs on the user's real machine |
| 4 | Chat: report a problem, then run the fix | 3:00 | Risk scoring, approval, real checking (claim 2) |
| 5 | Chat: a vague problem | 1:00 | Weak evidence raises the risk (claim 1) |
| 6 | Audit log | 0:30 | Every decision is recorded |
| 7 | Evaluation results in the terminal | 1:30 | Measured results, not just one demo |
| 8 | Closing sentence | 0:20 | — |

**Total: about 8 minutes.** If time is short, skip Step 6. If the panel wants more, use the extras at the end.

---

## The day before the viva

- [ ] **Test the whole demo once, the day before.** Not on the viva day.
- [ ] **Gemini quota:** the free plan gives about **20 requests per day for each model** (about 7–10 chat messages). On the viva morning, set a model you have **not used that day** in `backend\.env` (`GEMINI_MODEL=...`). Each model has its own allowance.
- [ ] **Embedding model:** check that `backend\.env` has `EMBEDDING_MODEL=models/gemini-embedding-001`. Old names like `text-embedding-004` no longer work.
- [ ] Keep the **device ID and device secret** of your Windows machine somewhere safe (the secret is shown only once).
- [ ] Charge the laptop. Turn off notifications and auto-updates.
- [ ] Run the tests once so you know they pass:
  ```powershell
  cd backend
  ..\venv\Scripts\python.exe -m pytest tests/ -q
  ```
- [ ] Take **screenshots of a good run** of Steps 3–7. If the internet or the AI fails on the day, you show these instead.

---

## Step 0: Start everything (before the panel enters)

Open **three PowerShell windows**.

**Window 1: backend**
```powershell
cd D:\RESEARCH\IT-Support-Systems
.\run.ps1
```
Wait until you see `Application startup complete`.

**Window 2: frontend**
```powershell
cd D:\RESEARCH\IT-Support-Systems
.\run-frontend.ps1
```
Open **http://localhost:5173** in the browser.

**Window 3: the endpoint agent** (the small program on the user's machine)
```powershell
cd D:\RESEARCH\IT-Support-Systems
$env:AUTOOPS_BACKEND_URL   = "http://localhost:8000"
$env:AUTOOPS_DEVICE_ID     = "dev_xxxxxxxx"     # your device id
$env:AUTOOPS_DEVICE_SECRET = "yyyyyyyy"         # your device secret
venv\Scripts\python agent\autoops_agent.py
```
You must see a line that ends with **`driver=powershell`**. This means real Windows commands will run.

Leave these windows open, but keep the **browser** in front.

---

## Step 1: Introduction (30 seconds)

**Say:**

> "IT support teams get many simple, repeated problems, like a full disk or a network that is not working. AI chatbots can suggest fixes, but there are two dangers. First, the AI may be wrong and still run a risky command. Second, a command can finish without error and the problem is still there.
>
> My system, AutoOps AI, lets the AI *suggest* a fix. Then a separate risk engine decides if it may run, and after it runs, the system *checks the real machine* to see if the problem is really fixed."

---

## Step 2: Log in and show the dashboard (30 seconds)

**Do:**
1. Log in with **admin@acme.com / admin123**.
2. The **Dashboard** opens.

**Say:**

> "This is the support portal. It has normal helpdesk parts: tickets, a knowledge base, users and audit logs. My research contribution is inside the **AI Support Chat** and the remediation workflow behind it. I will show that now."

Do not spend time on the other pages.

---

## Step 3: Show the user's machine (1 minute)

**Do:** Click **Endpoint Devices** in the left menu.

**Point at:** your Windows machine in the list, and that it is **online / recently seen**.

**Say:**

> "The fix must run on the machine that has the problem, not on the server. So a small agent runs on the user's Windows machine. You can see it in this window (point at Window 3).
>
> Two safety points:
> - The agent **asks** the server for work. The server never connects into the user's machine.
> - The agent receives only an **action ID**, like `flush_dns`, never a command. It looks the ID up in its own fixed list of 25 safe actions. So even if someone attacked the server, they could not make it run any command they want."

---

## Step 4: The main demo, from a reported problem to a checked fix (3 minutes)

### 4a. Report a problem

**Do:** Click **AI Support Chat**. Type:

> `Some websites are not opening on my computer. I think it is a DNS problem.`

**Say while it loads (it can take 10–30 seconds):**

> "The system now does three things. It searches the knowledge base for similar solved problems. It asks the AI to suggest a fix from a fixed list. Then, separately, the risk engine scores that fix. The AI does not give the score."

### 4b. Read the answer

**Point at:** the reply and the **risk card** under it.

**Say:**

> "The AI's answer is based on articles from the knowledge base. Below it is the **risk card**. It shows the **proposed action**, the **risk level**, the **score**, and the **route**, which means what must happen before it can run."

### 4c. Explain the risk score: the most important part

**Do:** Click **"Why?"** on the risk card. The working is shown.

**Say:**

> "The score uses five factors, each from 1 to 3:
>
> **Score = 0.30 × Impact + 0.20 × Confidence + 0.20 × Evidence + 0.15 × Reversibility + 0.15 × Scope**
>
> - Impact: how much the action can disturb the user.
> - Confidence: how sure the classifier is about the problem.
> - Evidence: how close the knowledge-base match was.
> - Reversibility: can we undo it?
> - Scope: one machine or many?
>
> Score 1.60 or lower is **low** risk, up to 2.20 is **medium**, and above that is **high**.
>
> Every number here comes from a similarity score, a classifier confidence, or a fixed property of the action. **No AI gives its own fix a score.**
>
> There are also **safety rules** that can only *raise* the risk, never lower it. For example, a missing piece of evidence, or an action that cannot be undone on a shared resource."

### 4d. Run it

What you see depends on the route:

| The card says | You click | You say |
|---|---|---|
| **Can run automatically** (low risk) | **Run it** | "Low risk and good evidence, so no approval is needed." |
| **Needs your approval** (medium risk) | **Approve and run** | "Medium risk, so a person must approve. The approval is a one-time token, tied to this exact action and these exact settings. If anything changes, the approval is no longer valid." |
| **Blocked: needs an IT expert** (high risk) | Nothing | "High risk, so it will not run. It goes to an IT expert. This is the system protecting the user." |

**Point at Window 3** (the agent). You can see it pick up the job.

> "Now the agent on the Windows machine has taken the job and is running it in real PowerShell."

### 4e. The result: claim 2

**Point at:** the result line on the card, for example **"Verified: the problem is fixed"**.
**Do:** open **"What the machine reported"**.

**Say:**

> "This is the second claim. The command finishing without error is **not** enough. Before the action, the system read the machine's real state. For DNS, that is the number of entries in the DNS cache, and it must not be empty, or there is nothing to flush. After the action, it read it again, and the cache must now have **0 entries**. Only because the real machine shows this does it say **Verified**.
>
> There are three possible results:
> - **Verified fixed:** the state changed as expected.
> - **Verified NOT fixed:** the command ran, but the problem is still there. A rollback is tried, or a person is called.
> - **Could not verify:** the system cannot tell, so it **never** says it is fixed."

### If the system refuses the action: this is also a good result

Sometimes the **pre-check** stops the action. For example, the DNS cache was already empty, or the disk is not really full. The card shows the reason.

**Say:**

> "This is the system working correctly. Before running anything, it checks that the problem really exists on the machine. Here it did not, so it refused. The AI does not decide what is a problem. The real checks do."

---

## Step 5: Weak evidence costs autonomy, claim 1 (1 minute)

**Do:** Start a new chat, or continue, and type something vague:

> `My network is weird.`

**Say:**

> "This message is very vague. The knowledge-base match is weak, and the classifier is less sure. Those two factors go into the score, so the risk goes up. An action that would normally run automatically may now **need approval**, or the system will ask a question first.
>
> This is my first claim: **when the system is less sure, it gives itself less freedom.**"

If the card shows a higher score or "Needs your approval", point at it.
If the assistant only asks a question, say: *"It did not even suggest an action. Without enough evidence it asks first. That is the safest result."*

> ⚠️ Each chat message uses AI quota. Do not send more than 3–4 messages in the whole demo.

---

## Step 6: Audit log (30 seconds)

**Do:** Click **Audit Logs**.

**Say:**

> "Every step is recorded: who proposed, the risk score and the policy version that produced it, who approved, what ran, and what the check found. A person can review afterwards exactly why the system did something."

---

## Step 7: Evaluation results (1.5 minutes)

**Do:** In a PowerShell window (stop nothing, just open a new one):
```powershell
cd D:\RESEARCH\IT-Support-Systems\backend
..\venv\Scripts\python.exe -m evaluation.run_evaluation
```
This takes a few seconds and **uses no AI quota**.

**Say:**

> "One demo is not proof, so I also built a controlled evaluation. There are 32 labelled scenarios. Each one runs under three conditions, three times: 288 runs.
>
> - **A**: advice only, nothing runs.
> - **B**: every action needs the same approval (uniform gating).
> - **C**: my risk-adaptive method."

**Point at these numbers** (they should match the screen):

| Measure | B (same approval for all) | C (risk-adaptive) |
|---|---|---|
| Unsafe actions executed | **36** | **0** |
| Human approvals needed | 96 | **72** (24 fewer) |
| Faults reported as success | 0 | **0** |
| Rollbacks attempted / verified | 6 / 3 | 6 / 3 |
| Reproducible across repeats | — | **Yes** |

**Say:**

> "With uniform gating, 36 unsafe actions ran, because a person approved them anyway. With my method, **zero** unsafe actions ran, and people needed to approve **24 fewer** times. And in all conditions, **no failed fix was ever reported as a success**, because of the post-check."

If the numbers on screen are different, **read the screen** and do not argue with it.

---

## Step 8: Closing (20 seconds)

**Say:**

> "So, to summarise: the AI suggests, the risk engine decides, and the real machine confirms. Weak evidence costs autonomy, and completion is not resolution. Thank you. I am happy to take questions."

---

## Extras if the panel asks for more

### A. The machine is offline, so a ticket is raised
1. Stop the agent (press **Ctrl+C** in Window 3). Wait about **90 seconds**.
2. In the chat, report a problem again.
3. **Say:** *"The machine is not answering, so the system does not pretend. It raises a **HIGH priority ticket**, names the machine, and assigns it to a person."* Then open **Tickets** and show it.
4. Start the agent again afterwards.

### B. Rollback, from the terminal
```powershell
cd D:\RESEARCH\IT-Support-Systems\backend
..\venv\Scripts\python.exe demo_rollback.py --item Teams
```
It prints every stage: proposed → assessed → approved → ran → post-checked → (rollback if needed).
**Say:** *"The command 'succeeded' line proves only that it ran. The post-check line is what matters. A rollback is checked in the same way as any other action. If it cannot be checked, the case goes to a person."*

### C. Knowledge base safety
**Knowledge Base** page: a solved problem becomes a **draft**. Only a reviewer can approve it. **A draft is never used for answers**, so the system cannot learn from its own unchecked guesses.

---

## If something goes wrong during the demo

| Problem | What to do and say |
|---|---|
| Chat is slow | "The AI model call takes 10–30 seconds. The server stays responsive while it waits." Wait calmly. |
| Chat error / quota finished | Change `GEMINI_MODEL` in `backend\.env`, restart Window 1. Or show your screenshots: "This is the same flow from yesterday's run." |
| Agent not online | Restart Window 3. Show Step 7 (the evaluation needs no AI and no agent). |
| Result says "Could not verify" | "This is correct behaviour. The system cannot see a difference, so it refuses to call it fixed, and it escalates." |
| Pre-check refuses | "The problem does not exist on this machine, so the system refuses to act. The checks decide, not the AI." |
| Internet down | Go straight to **Step 7**. It runs fully offline. |

**Golden rule:** an unexpected result is often the system being *safe*. Explain *why* it did that. Do not apologise for it.

---

## Be honest about the limits (say them before the panel finds them)

- The **evaluation runs on a simulated machine**, so faults can be repeated. The **live demo runs on real Windows**. These are two separate claims.
- **Risk labels were assigned by me**, so 100% classification accuracy shows that the code matches its own specification. It is a **consistency check**, not expert agreement.
- **`reset_winsock` will never run on real Windows**, because its pre-condition cannot be read. The system refuses when it cannot check. That is fail-closed, on purpose.
- **`restart_explorer` always ends "Could not verify"**, because nothing on the screen proves it fixed anything.
- The agent **reports its own machine's state**. A hacked agent could lie. Fixing that needs hardware attestation, which is outside this project.
- Only **30 knowledge-base articles**, all about Windows.
- The rollback on real Windows was run, but the **fingerprint-based restore check has not yet been repeated on Windows**. So say "rollback is verified in the evaluation", **not** "verified on real Windows".

---

## Simple meaning of key words

| Word | Simple meaning |
|---|---|
| **Remediation** | A fix for an IT problem |
| **Agent** | A small program on the user's PC that runs the approved fix |
| **Action ID** | The name of a fix from a fixed safe list (for example `flush_dns`), not a command |
| **Risk score** | A number from five factors that decides how careful the system must be |
| **Route** | What must happen before running: auto, user approval, or expert |
| **Override rule** | A safety rule that can only make the risk higher |
| **Approval token** | A one-time permission, tied to one exact action and its settings |
| **Pre-check** | "Does the problem really exist?", checked before running |
| **Post-check / verification** | "Is the problem really gone?", checked by reading the real machine |
| **Inconclusive** | The system cannot tell, so it never says "fixed" |
| **Rollback** | Putting the machine back the way it was |
| **Escalate** | Hand the case to a human |
| **Fail closed** | If unsure, do **not** act |
| **RAG** | The AI answers using knowledge-base articles it found, not only its memory |
