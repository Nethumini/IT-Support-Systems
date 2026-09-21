"""Send one remediation to a device, and print what came back.

A demo and smoke-test helper. It walks the real path - propose, assess, execute,
verify - against a machine running the agent, so the output is the evidence that
remote remediation works end to end.

Run the agent first, in another terminal. If it is not listening, the job expires
and the remediation is reported as failed rather than as done, which is the
intended behaviour and worth showing too.

Usage::

    python agent/try_device.py --device-id dev_xxxxxxxx

    python agent/try_device.py --device-id dev_xxxxxxxx \\
        --action check_disk_space --backend-url http://192.168.1.48:8000
"""
from __future__ import annotations

import argparse
import json
import sys

import httpx

DEFAULT_BACKEND_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

#: A read-only diagnostic. Safe to repeat, and its post-check asserts that
#: nothing changed - so a pass proves the loop, not just that a command ran.
DEFAULT_ACTION = "check_disk_space"

#: Low on every factor: this is a read-only check with good evidence behind it,
#: so the engine should route it to automatic execution. Chosen to demonstrate
#: the loop, not to exercise the scoring - the risk tests do that.
LOW_RISK_FACTORS = {
    "impact": 1,
    "confidence_rating": 3,
    "evidence_quality": 3,
    "irreversibility": 1,
    "affected_scope": 1,
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--device-id", required=True, help="From device registration")
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    parser.add_argument("--action", default=DEFAULT_ACTION)
    parser.add_argument("--email", default="admin@acme.com")
    parser.add_argument("--password", default="admin123")
    args = parser.parse_args(argv)

    base = f"{args.backend_url.rstrip('/')}{API_PREFIX}"
    client = httpx.Client(base_url=base, timeout=120.0)

    login = client.post("/login", json={"email": args.email, "password": args.password})
    if login.status_code != 200:
        print(f"Login failed ({login.status_code}): {login.text[:200]}")
        return 1
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    print(f"Proposing {args.action} on {args.device_id} ...")
    proposed = client.post("/remediation/propose", headers=headers, json={
        "reported_problem": "Checking free disk space on this machine",
        "action_id": args.action,
        "parameters": {},
        "diagnosis": f"Run {args.action} to read current state",
        "evidence": [{
            "kb_id": "KB-007",
            "title": "C: drive almost full on Windows laptop",
            "similarity_score": 0.79,
        }],
        "device_id": args.device_id,
        "factors": LOW_RISK_FACTORS,
        "catalogue_risk": "low",
    })
    if proposed.status_code != 201:
        print(f"Propose failed ({proposed.status_code}): {proposed.text[:300]}")
        return 1

    request = proposed.json()
    print(f"  risk   : {request['risk_level']} (score {request['risk_score']:.2f})")
    print(f"  route  : {request['approval_route']}")
    print(f"  device : {request['device_id']}")

    print("\nExecuting - the agent should pick this up within a few seconds ...")
    run = client.post(
        "/remediation/execute", headers=headers,
        json={"remediation_id": request["id"]},
    )
    if run.status_code != 200:
        print(f"Execute failed ({run.status_code}): {run.text[:300]}")
        print("\nIf this says the device did not respond, the agent was not running.")
        return 1

    result = run.json()
    execution = result.get("execution_result") or {}
    post = result.get("post_check") or {}

    print(f"\n  status       : {result['status']}")
    print(f"  verification : {result['verification_status']}")
    print(f"  driver       : {execution.get('driver')}")
    print(f"  output       : {execution.get('output')}")
    print(f"  before       : {json.dumps(execution.get('state_before') or {})}")
    print(f"  after        : {json.dumps(execution.get('state_after') or {})}")
    print(f"  post-check   : {post.get('reason')}")

    if execution.get("driver") == "agent":
        print("\nThe action ran on the device, not on the backend host.")
    else:
        print(
            f"\nNote: this ran with the '{execution.get('driver')}' driver, so it "
            f"executed on the backend host. Check the device id was accepted."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
