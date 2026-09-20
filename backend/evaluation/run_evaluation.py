"""Run the controlled comparative evaluation and write the results.

    cd backend
    ../venv/bin/python -m evaluation.run_evaluation

Writes a CSV of every run and a JSON summary into ``evaluation/results/``,
and prints the comparison table for the results chapter.

Calls no chat model, so it costs no API quota and can be re-run freely. The
run is deterministic: the same commit and scenario set produce the same
numbers, which is what thesis 6.2 means by repeatability.
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import platform
import subprocess
import sys

# Every step of every run writes an audit entry, which is the point - but 270
# runs of it would bury the results table. Audit rows still go to the database
# and can be inspected there; only the console output is quietened. Escalations
# and denials log at ERROR and WARNING, so this has to sit above those.
logging.disable(logging.ERROR)
from datetime import datetime
from pathlib import Path

from evaluation.harness import CONDITION_NAMES, run_all
from evaluation.metrics import (
    compare,
    format_confusion,
    format_table,
    reproducibility,
)
from evaluation.scenarios import SCENARIOS, summary

RESULTS_DIR = Path(__file__).parent / "results"


def _commit() -> str:
    """The commit these numbers came from, recorded alongside them."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=Path(__file__).resolve().parents[2],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="AutoOps AI controlled evaluation")
    parser.add_argument("--repeats", type=int, default=3,
                        help="runs per scenario per condition (thesis 6.4.3 uses 3)")
    parser.add_argument("--conditions", default="A,B,C",
                        help="comma-separated subset of A,B,C")
    parser.add_argument("--out", default=str(RESULTS_DIR),
                        help="directory for the CSV and JSON output")
    args = parser.parse_args()

    conditions = [c.strip().upper() for c in args.conditions.split(",") if c.strip()]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    composition = summary()
    print("=" * 74)
    print("AutoOps AI - controlled comparative evaluation")
    print("=" * 74)
    print(f"Scenarios : {composition['total']} "
          f"(low {composition['by_expected_risk']['low']}, "
          f"medium {composition['by_expected_risk']['medium']}, "
          f"high {composition['by_expected_risk']['high']})")
    print(f"            {composition['unsafe_to_automate']} unsafe to automate, "
          f"{composition['with_injected_fault']} with injected faults, "
          f"{composition['without_evidence']} without evidence")
    print(f"Conditions: {', '.join(conditions)}  x {args.repeats} repeats")
    for c in conditions:
        print(f"  {c} = {CONDITION_NAMES.get(c, c)}")
    print(f"Commit    : {_commit()}")
    print()

    results = run_all(conditions=conditions, repeats=args.repeats)
    report = compare(results)
    repro = reproducibility(results)

    print(format_table(report))
    print()
    print("Risk classification, condition C (expert label vs assigned):")
    print(format_confusion(report["confusion_matrix"]))
    print()

    if "headline" in report:
        h = report["headline"]
        print("Uniform gating (B) vs risk-adaptive (C):")
        print(f"  Unsafe actions executed : B={h['unsafe_executed_B']}  C={h['unsafe_executed_C']}")
        print(f"  Human approvals needed  : B={h['human_approvals_B']}  C={h['human_approvals_C']}")
        print(f"  Approvals avoided by risk adaptation: {h['approvals_avoided_by_risk_adaptation']}")
        print()

    print(f"Reproducible across repeats: {repro['fully_reproducible']} "
          f"({repro['stable']}/{repro['cases_checked']} cases stable)")
    if repro["unstable"]:
        print("  UNSTABLE:")
        for key, values in repro["unstable"].items():
            print(f"    {key}: {values}")
    print()

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    csv_path = out_dir / f"runs-{stamp}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        rows = [r.to_dict() for r in results]
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            row["overrides"] = ";".join(row["overrides"])
            writer.writerow(row)

    json_path = out_dir / f"summary-{stamp}.json"
    json_path.write_text(json.dumps({
        "generated_at": datetime.now().isoformat(),
        "commit": _commit(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "repeats": args.repeats,
        "conditions": conditions,
        "scenario_composition": composition,
        "report": report,
        "reproducibility": repro,
    }, indent=2), encoding="utf-8")

    print(f"Per-run data : {csv_path}")
    print(f"Summary      : {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
