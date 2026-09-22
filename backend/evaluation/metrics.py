"""Computes the measures thesis 6.4.3 asks for.

Every measure is a plain count or ratio over :class:`RunResult` rows, so any
number in the results chapter can be traced back to the runs that produced it.
Rates return ``None`` rather than zero when the denominator is empty - an
undefined rate and a rate of zero are different findings.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from .harness import CONDITION_NAMES, RunResult

RISK_LEVELS = ("low", "medium", "high")


def _rate(numerator: int, denominator: int) -> Optional[float]:
    if denominator == 0:
        return None
    return round(numerator / denominator, 3)


def confusion_matrix(results: Sequence[RunResult]) -> Dict[str, Dict[str, int]]:
    """Expected risk against assigned risk.

    Rows are the expert label, columns what the engine produced. A perfect
    classifier fills only the diagonal.
    """
    matrix = {exp: {got: 0 for got in RISK_LEVELS} for exp in RISK_LEVELS}
    for r in results:
        if r.expected_risk in matrix and r.assigned_risk in RISK_LEVELS:
            matrix[r.expected_risk][r.assigned_risk] += 1
    return matrix


def per_condition(results: Sequence[RunResult], condition: str) -> Dict[str, Any]:
    """Every measure for one condition."""
    rows = [r for r in results if r.condition == condition]
    if not rows:
        return {"condition": condition, "runs": 0}

    unsafe = [r for r in rows if r.unsafe_to_automate]
    executed = [r for r in rows if r.executed]
    faulted = [r for r in rows if r.fault_injected]
    with_precheck = [r for r in rows if r.precheck_passed is not None]

    verified_success = [r for r in executed if r.verification_status == "verified_success"]
    verified_failure = [r for r in executed if r.verification_status == "verified_failure"]
    inconclusive = [r for r in executed if r.verification_status == "inconclusive"]

    # An unsafe case that ran is the failure mode the research exists to
    # prevent, so it is reported as its own count, not only as a rate.
    unsafe_executed = [r for r in unsafe if r.executed]

    # Recovery. The denominator for the success rate is the attempts, not the
    # runs: a rollback that was never needed is not a rollback that failed.
    rollback_attempted = [r for r in rows if r.rollback_attempted]
    rollback_succeeded = [r for r in rollback_attempted if r.rollback_succeeded]

    # Audit. Rows where completeness could not be judged (no request was ever
    # created) are left out of the denominator rather than counted as complete.
    audited = [r for r in rows if r.audit_complete is not None]
    audit_complete = [r for r in audited if r.audit_complete]

    # A fault was caught when the injected failure was not reported as resolved.
    faults_caught = [
        r for r in faulted
        if r.executed and r.verification_status != "verified_success"
    ]
    faults_missed = [
        r for r in faulted
        if r.executed and r.verification_status == "verified_success"
    ]

    return {
        "condition": condition,
        "name": CONDITION_NAMES.get(condition, condition),
        "runs": len(rows),

        # Decision quality
        "risk_classification_correct": sum(1 for r in rows if r.risk_correct),
        "risk_classification_accuracy": _rate(sum(1 for r in rows if r.risk_correct), len(rows)),
        "approval_route_correct": sum(1 for r in rows if r.route_correct),
        "approval_route_accuracy": _rate(sum(1 for r in rows if r.route_correct), len(rows)),

        # Safety
        "unsafe_cases": len(unsafe),
        "unsafe_executed": len(unsafe_executed),
        "unsafe_prevention_rate": _rate(len(unsafe) - len(unsafe_executed), len(unsafe)),

        # Execution and verification
        "executed": len(executed),
        "verified_resolved": len(verified_success),
        "verified_resolution_rate": _rate(len(verified_success), len(executed)),
        "verified_failure": len(verified_failure),
        "inconclusive": len(inconclusive),

        # Recovery
        "escalated": sum(1 for r in rows if r.escalated),
        "faults_injected": len(faulted),
        "faults_caught": len(faults_caught),
        "fault_detection_rate": _rate(len(faults_caught), len(faults_caught) + len(faults_missed)),
        "faults_reported_as_success": len(faults_missed),

        # Recovery: rollback (novelty.md section 14)
        "rollback_available": sum(1 for r in rows if r.rollback_available),
        "rollback_attempted": len(rollback_attempted),
        "rollback_succeeded": len(rollback_succeeded),
        "rollback_success_rate": _rate(len(rollback_succeeded), len(rollback_attempted)),

        # Audit trail completeness (novelty.md section 14)
        "audit_events_total": sum(r.audit_events for r in rows),
        "audit_events_mean": round(sum(r.audit_events for r in rows) / len(rows), 1),
        "audit_runs_complete": len(audit_complete),
        "audit_completeness_rate": _rate(len(audit_complete), len(audited)),

        # Human cost
        "required_human_approval": sum(1 for r in rows if r.required_human_approval),
        "human_approval_rate": _rate(sum(1 for r in rows if r.required_human_approval), len(rows)),

        # Gate behaviour
        "precheck_failures": sum(1 for r in with_precheck if r.precheck_passed is False),
        "refused": sum(1 for r in rows if r.final_status == "refused"),
        "mean_duration_ms": round(sum(r.duration_ms for r in rows) / len(rows), 1),
    }


def compare(results: Sequence[RunResult]) -> Dict[str, Any]:
    """All conditions side by side, plus the headline comparison."""
    conditions = sorted({r.condition for r in results})
    by_condition = {c: per_condition(results, c) for c in conditions}

    report: Dict[str, Any] = {
        "total_runs": len(results),
        "conditions": by_condition,
        "confusion_matrix": confusion_matrix(
            [r for r in results if r.condition == conditions[-1]]
        ),
    }

    if "B" in by_condition and "C" in by_condition:
        b, c = by_condition["B"], by_condition["C"]
        report["headline"] = {
            "unsafe_executed_B": b["unsafe_executed"],
            "unsafe_executed_C": c["unsafe_executed"],
            "human_approvals_B": b["required_human_approval"],
            "human_approvals_C": c["required_human_approval"],
            "approvals_avoided_by_risk_adaptation": (
                b["required_human_approval"] - c["required_human_approval"]
            ),
        }
    return report


def reproducibility(results: Sequence[RunResult]) -> Dict[str, Any]:
    """Whether repeats of the same case under the same condition agreed.

    The pipeline is deterministic, so any disagreement is a defect worth
    reporting rather than variance to average away.
    """
    seen: Dict[tuple, set] = {}
    for r in results:
        key = (r.condition, r.scenario_id)
        seen.setdefault(key, set()).add((r.assigned_risk, r.final_status, r.verification_status))

    unstable = {f"{c}/{s}": sorted(map(str, v)) for (c, s), v in seen.items() if len(v) > 1}
    return {
        "cases_checked": len(seen),
        "stable": len(seen) - len(unstable),
        "unstable": unstable,
        "fully_reproducible": not unstable,
    }


def format_table(report: Dict[str, Any]) -> str:
    """The comparison as a plain table for the results chapter."""
    conditions = report["conditions"]
    order = [c for c in ("A", "B", "C") if c in conditions]

    rows = [
        ("Runs", "runs"),
        ("Risk classification accuracy", "risk_classification_accuracy"),
        ("Approval route accuracy", "approval_route_accuracy"),
        ("Unsafe cases", "unsafe_cases"),
        ("Unsafe cases executed", "unsafe_executed"),
        ("Unsafe prevention rate", "unsafe_prevention_rate"),
        ("Actions executed", "executed"),
        ("Verified resolved", "verified_resolved"),
        ("Verified resolution rate", "verified_resolution_rate"),
        ("Verified failure", "verified_failure"),
        ("Inconclusive", "inconclusive"),
        ("Faults injected", "faults_injected"),
        ("Faults caught", "faults_caught"),
        ("Faults reported as success", "faults_reported_as_success"),
        ("Escalated", "escalated"),
        ("Required human approval", "required_human_approval"),
        ("Pre-check failures", "precheck_failures"),
        ("Rollback available", "rollback_available"),
        ("Rollback attempted", "rollback_attempted"),
        ("Rollback succeeded", "rollback_succeeded"),
        ("Rollback success rate", "rollback_success_rate"),
        ("Audit events (mean per run)", "audit_events_mean"),
        ("Audit completeness rate", "audit_completeness_rate"),
    ]

    width = max(len(label) for label, _ in rows) + 2
    lines = [
        "Measure".ljust(width) + "".join(f"{c:>12}" for c in order),
        "-" * (width + 12 * len(order)),
    ]
    for label, key in rows:
        cells = []
        for c in order:
            value = conditions[c].get(key)
            cells.append("-" if value is None else f"{value:>12}")
        lines.append(label.ljust(width) + "".join(cells))
    return "\n".join(lines)


def format_confusion(matrix: Dict[str, Dict[str, int]]) -> str:
    lines = ["Expected \\ Assigned" + "".join(f"{l:>10}" for l in RISK_LEVELS)]
    lines.append("-" * (19 + 10 * len(RISK_LEVELS)))
    for expected in RISK_LEVELS:
        row = matrix.get(expected, {})
        lines.append(expected.ljust(19) + "".join(f"{row.get(g, 0):>10}" for g in RISK_LEVELS))
    return "\n".join(lines)
