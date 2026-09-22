"""Drive one remediation through to recovery and print what happened.

Propose, assess, approve, execute, verify, and - when the post-check fails -
roll back and verify that too. Every stage is printed, so this doubles as the
demonstration script for the recovery path.

Runs against the host by default. Pass ``--device`` to run on an enrolled
machine instead; nothing else about the workflow changes, which is the point
worth making when showing it.

    python demo_rollback.py --item Teams
    python demo_rollback.py --item Teams --device <device-id>

Standard library only, so it runs anywhere the backend is reachable.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

TIMEOUT = 180  # a device may take a while to poll for its work


def call(url: str, payload: Optional[Dict[str, Any]] = None, token: Optional[str] = None) -> Any:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        sys.exit(f"\n{exc.code} from {url}\n{body}\n")
    except urllib.error.URLError as exc:
        sys.exit(f"\nCannot reach {url}: {exc.reason}\n")


def show(title: str, *lines: str) -> None:
    print(f"\n{title}")
    for line in lines:
        print(f"  {line}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="http://localhost:8000")
    parser.add_argument("--email", default="admin@acme.com")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--item", default="Teams", help="Startup item to disable")
    parser.add_argument("--device", default=None, help="Enrolled device id; omit to use the host")
    args = parser.parse_args()

    api = f"{args.backend.rstrip('/')}/api/v1"

    auth = call(f"{api}/login", {"email": args.email, "password": args.password})
    token = auth["access_token"]
    target = args.device or "the host running the backend"
    show("Signed in", f"{args.email} -> {target}")

    # Whether an action has a rollback is a property of its contract, which the
    # catalogue endpoint publishes. It is an input to the risk score rather
    # than a field of the request, so it is read from there.
    catalogue = {a["action_id"]: a for a in call(f"{api}/remediation/actions", token=token)["actions"]}
    has_rollback = catalogue.get("disable_startup_item", {}).get("has_rollback")

    # Factors as a human would state them: one machine, good evidence, and a
    # registered rollback makes it reversible. Medium risk, so it needs a
    # human approval - the same route the evaluation takes under condition C.
    proposal = call(f"{api}/remediation/propose", {
        "reported_problem": f"{args.item} starts itself every time I log in",
        "action_id": "disable_startup_item",
        "parameters": {"item_name": args.item},
        "diagnosis": f"{args.item} is registered to run at startup",
        "evidence": [{"kb_id": "KB-012", "similarity_score": 0.78}],
        "device_id": args.device,
        "catalogue_risk": "medium",
        "factors": {
            "impact": 2,
            "confidence_rating": 3,
            "evidence_quality": 3,
            "irreversibility": 1,
            "affected_scope": 1,
        },
    }, token)

    remediation_id = proposal["id"]
    show(
        f"1. Proposed and assessed (#{remediation_id})",
        f"risk      : {proposal['risk_level']} (score {proposal['risk_score']})",
        f"route     : {proposal['approval_route']}",
        f"rollback  : {'available' if has_rollback else 'none'}",
        f"status    : {proposal['status']}",
    )

    approval = call(f"{api}/remediation/approve", {"remediation_id": remediation_id}, token)
    show("2. Approved", f"single-use token issued to {args.email}")

    print("\n3. Executing (a device may take up to a minute to pick up the job)...")
    final = call(f"{api}/remediation/execute", {
        "remediation_id": remediation_id,
        "token": approval["approval_token"],
    }, token)

    execution = final.get("execution_result") or {}
    post = final.get("post_check") or {}
    show(
        "4. Ran and post-checked",
        f"driver    : {execution.get('driver')}",
        f"command   : {'succeeded' if execution.get('success') else 'failed'}"
        f"  <- this alone proves only that it ran",
        f"post-check: {final.get('verification_status')}",
        f"reason    : {post.get('reason', '')}",
    )

    rollback = final.get("rollback_result") or {}
    if not final.get("rollback_attempted"):
        show("5. Recovery", "no rollback was needed")
    elif rollback.get("verified"):
        show(
            "5. Rolled back and verified",
            f"action    : {rollback.get('action_id')}",
            f"command   : {'succeeded' if rollback.get('success') else 'failed'}",
            f"post-check: {(rollback.get('verification') or {}).get('reason', '')}",
        )
    else:
        show(
            "5. Rollback attempted and NOT verified - escalated",
            f"command   : {'succeeded' if rollback.get('success') else 'failed'}",
            f"error     : {rollback.get('error', '-')}",
            f"escalation: {final.get('escalation_reason', '')}",
        )

    print(f"\nFinal status: {final['status']}")
    print(f"Full trail  : {api}/remediation/{remediation_id}\n")

    expected = {"completed", "rolled_back", "escalated"}
    return 0 if final["status"] in expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
