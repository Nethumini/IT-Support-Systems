"""Run the labelled retrieval benchmark through the production retriever.

Usage from ``backend``::

    DEBUG=false ../venv/bin/python -m evaluation.run_retrieval_evaluation \
        --confirm-external-data

The command makes live embedding API calls. It writes a CSV containing every
ranked outcome and a JSON summary containing the configuration, hashes,
explicit metric denominators, and structured cases for error analysis.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from app.config import get_settings
from app.services.dataset_analyzer import DatasetAnalyzer
from evaluation.retrieval_evaluation import (
    DEFAULT_QUERY_PATH,
    load_query_set,
    run_queries,
    summarize,
)


RESULTS_DIR = Path(__file__).parent / "results"
DEFAULT_DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "ticketing_system_data_new.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=Path(__file__).resolve().parents[2],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _working_tree_dirty() -> bool | None:
    """Record whether the commit identifier fully describes the evaluated code."""
    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=Path(__file__).resolve().parents[2],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return bool(status.strip())
    except Exception:
        return None


def _csv_row(row: Dict[str, Any]) -> Dict[str, Any]:
    serializable = dict(row)
    serializable["relevant_kb_ids"] = ";".join(row["relevant_kb_ids"])
    serializable["returned_kb_ids"] = ";".join(row["returned_kb_ids"])
    return serializable


def main() -> int:
    parser = argparse.ArgumentParser(description="AutoOps AI labelled retrieval evaluation")
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERY_PATH)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--out", type=Path, default=RESULTS_DIR)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument(
        "--confirm-external-data",
        action="store_true",
        help=("confirm that sending the labelled queries and KB title/pattern text "
              "to the configured embedding provider is authorized"),
    )
    args = parser.parse_args()
    if args.limit < 3:
        parser.error("--limit must be at least 3 to calculate Hit@3")
    if not args.confirm_external_data:
        parser.error(
            "live evaluation sends query and knowledge-base text to the configured "
            "embedding provider; rerun with --confirm-external-data only when authorized"
        )

    metadata, queries = load_query_set(args.queries)
    analyzer = DatasetAnalyzer(dataset_path=str(args.dataset))
    known_ids = set(analyzer.knowledge_base)
    unknown = sorted({kb_id for query in queries for kb_id in query.relevant_kb_ids
                      if kb_id not in known_ids})
    if unknown:
        raise ValueError(f"query labels refer to KB ids absent from the dataset: {unknown}")

    print("=" * 74)
    print("AutoOps AI - labelled retrieval evaluation")
    print("=" * 74)
    print(f"Queries   : {len(queries)} (label set {metadata.get('version', 'unknown')})")
    print(f"KB items  : {len(known_ids)}")
    print(f"Model     : {get_settings().embedding_model}")
    print(f"Threshold : > {analyzer.SIMILARITY_THRESHOLD}")
    print(f"Top-k     : {args.limit}")
    print(f"Commit    : {_commit()}")
    print(f"Dirty tree: {_working_tree_dirty()}")
    print()

    rows = run_queries(analyzer, queries, limit=args.limit)
    metrics = summarize(rows)
    print(f"Hit@1     : {metrics['hit_at_1']['hits']}/{metrics['hit_at_1']['total']} "
          f"({metrics['hit_at_1']['rate']:.3f})")
    print(f"Hit@3     : {metrics['hit_at_3']['hits']}/{metrics['hit_at_3']['total']} "
          f"({metrics['hit_at_3']['rate']:.3f})")
    print(f"MRR       : {metrics['mean_reciprocal_rank']['reciprocal_rank_sum']}/"
          f"{metrics['mean_reciprocal_rank']['total']} "
          f"({metrics['mean_reciprocal_rank']['value']:.3f})")
    print(f"Non-top-1 : {len(metrics['errors_for_review'])}")
    print()

    args.out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    csv_path = args.out / f"retrieval-runs-{stamp}.csv"
    json_path = args.out / f"retrieval-summary-{stamp}.json"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        csv_rows = [_csv_row(row) for row in rows]
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    settings = get_settings()
    summary = {
        "generated_at": datetime.now().isoformat(),
        "commit": _commit(),
        "working_tree_dirty": _working_tree_dirty(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "query_set": {
            **metadata,
            "path": str(args.queries),
            "sha256": _sha256(args.queries),
        },
        "knowledge_base": {
            "path": str(args.dataset),
            "sha256": _sha256(args.dataset),
            "articles": len(known_ids),
        },
        "retriever": {
            "implementation": "DatasetAnalyzer.find_similar_issues",
            "embedding_model": settings.embedding_model,
            "similarity_threshold_strictly_greater_than": analyzer.SIMILARITY_THRESHOLD,
            "category_match_bonus": analyzer.CATEGORY_MATCH_BONUS,
            "ranking": "0.8 * rounded cosine similarity with category bonus + 0.2 * (used_count / 100)",
            "limit": args.limit,
            "cache_scope": "in-process",
        },
        "metrics": metrics,
    }
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Per-query data: {csv_path}")
    print(f"Summary       : {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
