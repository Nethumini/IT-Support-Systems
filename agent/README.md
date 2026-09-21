# AutoOps endpoint agent

Runs on a user's machine. Asks the backend for work, runs it locally, reports
what happened.

Without it, diagnostics only ever read the machine hosting the backend. With it,
a remediation can target the computer that actually has the problem.

## What it is allowed to do

It receives a **registered action id**, never a command. It looks the id up in
its own copy of the action catalogue and refuses anything it does not recognise.
So a compromised server cannot use the agent to run arbitrary code.

It also cannot approve anything. Risk scoring, approval and verification all
happen on the server. The agent runs what was already decided and reports the
result.

## Setup on the Windows machine

**1. Install Python 3.12** from python.org. Tick *Add Python to PATH*.

**2. Copy the project** to the Windows machine, or clone it.

**3. Install what it needs:**

```powershell
python -m venv venv
venv\Scripts\pip install httpx psutil pydantic pydantic-settings sqlalchemy ^
    python-dotenv bcrypt passlib python-jose cryptography email-validator
```

The last five are not used by the agent itself. They come in because the agent
reads the project's settings file, which imports the authentication helpers.
Installing the full `requirements.txt` also works and is simpler if you are
unsure.

**4. Register this machine.** On the backend, as an administrator:

```bash
curl -X POST http://<backend-host>:8000/api/v1/devices \
  -H "Authorization: Bearer <your admin token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "WIN-LAB-01", "owner_email": "admin@acme.com", "os_name": "Windows", "os_version": "11"}'
```

The response contains a `device_id` and a `secret`. **The secret is shown once.**
Copy it now; it is stored only as a hash and cannot be read back. If you lose it,
register the machine again.

**5. Run the agent:**

```powershell
$env:AUTOOPS_BACKEND_URL = "http://<backend-host>:8000"
$env:AUTOOPS_DEVICE_ID   = "dev_xxxxxxxx"
$env:AUTOOPS_DEVICE_SECRET = "yyyyyyyy"

venv\Scripts\python agent\autoops_agent.py
```

You should see:

```
Agent started on WIN-LAB-01 (Windows) as dev_xxxxxxxx, driver=powershell, backend=...
```

`driver=powershell` is the line that matters. It means the machine chose the real
Windows driver and your 25 catalogue actions will run for real.

## Checking it works

Take one job and stop, instead of looping:

```powershell
venv\Scripts\python agent\autoops_agent.py --once
```

Then, from the backend, propose a remediation with `"device_id": "dev_xxxxxxxx"`
and execute it. The result comes back with `"driver": "agent"`.

## Running it on macOS or Linux

The same file. The machine picks its own driver, so on a Mac you get the
read-only POSIX set instead of PowerShell:

```bash
export AUTOOPS_BACKEND_URL=http://localhost:8000
export AUTOOPS_DEVICE_ID=dev_xxxxxxxx
export AUTOOPS_DEVICE_SECRET=yyyyyyyy
./venv/bin/python agent/autoops_agent.py
```

This is how the work loop is tested without a Windows machine.

## Settings

| Variable | Meaning |
| --- | --- |
| `AUTOOPS_BACKEND_URL` | Where the backend is. Default `http://localhost:8000` |
| `AUTOOPS_DEVICE_ID` | From registration |
| `AUTOOPS_DEVICE_SECRET` | From registration |
| `AUTOOPS_AGENT_DRIVER` | Override the driver. Normally leave unset so the machine chooses |

Command-line flags (`--backend-url`, `--device-id`, `--device-secret`, `--driver`)
override the variables. `--once` takes at most one job and exits. `--verbose`
adds debug logging.

## If something goes wrong

**"The backend rejected this device's credentials"** — wrong id or secret, or an
administrator revoked the device. Revoking is permanent; register it again.

**"Backend unreachable"** — the agent retries every 10 seconds. Check the URL,
and that the Windows machine can reach the backend host (they must be on the
same network, or the backend must be reachable from it).

**Agent polls but never gets a job** — the remediation was not targeted at this
device. Check that `device_id` was passed to `/remediation/propose`.

**Jobs time out** — the server waits 60 seconds. If the agent was not running
when the remediation executed, the job expires and the remediation is marked
failed rather than guessing. Start the agent first.

## Known limitation, stated for the thesis

The agent reports its own machine's state, and post-action verification reads
that report. A compromised agent could therefore claim a fix that did not
happen — the same exposure any monitoring agent has. Closing it needs attested
measurement, which is beyond this prototype.

What the server does control: a fabricated report is still recorded, still
attributable to one revocable device credential, and still comparable with the
before-snapshot from the same run.
