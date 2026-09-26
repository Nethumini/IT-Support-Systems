"""Reproducible measures for the labelled knowledge-retrieval evaluation.

The labels live in ``retrieval_queries.json`` and are loaded before retrieval.
This module deliberately contains no model-specific ranking logic: the real
``DatasetAnalyzer.find_similar_issues`` path supplies the ranked results, and
these functions only measure and preserve what it returned.
"""
from __future__ import annotations

import json
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence


DEFAULT_QUERY_PATH = Path(__file__).with_name("retrieval_queries.json")


@dataclass(frozen=True)
class RetrievalQuery:
    id: str
    query: str
    category: str
    relevant_kb_ids: tuple[str, ...]
    label_reason: str


def load_query_set(path: Path | str = DEFAULT_QUERY_PATH) -> tuple[Dict[str, Any], List[RetrievalQuery]]:
    """Load and validate labels without invoking the embedding provider."""
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    raw_queries = payload.get("queries")
    if not isinstance(raw_queries, list) or not raw_queries:
        raise ValueError("retrieval query set must contain a non-empty 'queries' list")

    queries: List[RetrievalQuery] = []
    seen: set[str] = set()
    for raw in raw_queries:
        try:
            query_id = str(raw["id"]).strip()
            query_text = str(raw["query"]).strip()
            category = str(raw["category"]).strip()
            relevant = tuple(str(item).strip() for item in raw["relevant_kb_ids"])
            reason = str(raw["label_reason"]).strip()
        except (KeyError, TypeError) as exc:
            raise ValueError(f"invalid retrieval query record: {raw!r}") from exc

        if not query_id or query_id in seen:
            raise ValueError(f"blank or duplicate retrieval query id: {query_id!r}")
        if not query_text or not category or not relevant or not reason:
            raise ValueError(f"incomplete retrieval query: {query_id}")
        if len(set(relevant)) != len(relevant):
            raise ValueError(f"duplicate relevant KB id for query: {query_id}")

        seen.add(query_id)
        queries.append(RetrievalQuery(
            id=query_id,
            query=query_text,
            category=category,
            relevant_kb_ids=relevant,
            label_reason=reason,
        ))

    metadata = {key: value for key, value in payload.items() if key != "queries"}
    return metadata, queries


def relevant_rank(ranked_ids: Sequence[str], relevant_ids: Iterable[str]) -> Optional[int]:
    """Return the one-based rank of the first relevant result, if present."""
    relevant = set(relevant_ids)
    return next((index for index, kb_id in enumerate(ranked_ids, start=1)
                 if kb_id in relevant), None)


def measure_query(query: RetrievalQuery, results: Sequence[Dict[str, Any]], *, limit: int = 3) -> Dict[str, Any]:
    """Convert one ranked result list into an auditable per-query record."""
    ranked = list(results[:limit])
    ranked_ids = [str(result.get("kb_id", "")) for result in ranked]
    rank = relevant_rank(ranked_ids, query.relevant_kb_ids)

    if not ranked:
        outcome = "no_results_above_threshold"
    elif rank == 1:
        outcome = "correct_at_rank_1"
    elif rank is not None:
        outcome = "relevant_below_rank_1"
    else:
        outcome = "relevant_missing_from_top_k"

    row: Dict[str, Any] = {
        "query_id": query.id,
        "query": query.query,
        "category": query.category,
        "relevant_kb_ids": list(query.relevant_kb_ids),
        "label_reason": query.label_reason,
        "returned_kb_ids": ranked_ids,
        "relevant_rank": rank,
        "hit_at_1": rank == 1,
        "hit_at_3": rank is not None and rank <= 3,
        "reciprocal_rank": round(1 / rank, 6) if rank is not None else 0.0,
        "outcome": outcome,
    }
    for index in range(limit):
        result = ranked[index] if index < len(ranked) else {}
        position = index + 1
        row[f"rank_{position}_kb_id"] = result.get("kb_id")
        row[f"rank_{position}_title"] = result.get("title")
        row[f"rank_{position}_score"] = result.get("similarity_score")
    return row


def run_queries(analyzer: Any, queries: Sequence[RetrievalQuery], *, limit: int = 3) -> List[Dict[str, Any]]:
    """Run labels through the production retrieval method and time each call."""
    rows: List[Dict[str, Any]] = []
    for query in queries:
        started = time.perf_counter()
        results = analyzer.find_similar_issues(query.query, query.category, limit=limit)
        elapsed_ms = (time.perf_counter() - started) * 1000
        row = measure_query(query, results, limit=limit)
        row["elapsed_ms"] = round(elapsed_ms, 3)
        rows.append(row)
    return rows


def summarize(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate retrieval results with visible numerators and denominators."""
    total = len(rows)
    if total == 0:
        raise ValueError("cannot summarize an empty retrieval evaluation")

    hit_1 = sum(bool(row["hit_at_1"]) for row in rows)
    hit_3 = sum(bool(row["hit_at_3"]) for row in rows)
    reciprocal_sum = round(sum(float(row["reciprocal_rank"]) for row in rows), 6)
    outcome_counts = Counter(str(row["outcome"]) for row in rows)
    errors = [
        {
            "query_id": row["query_id"],
            "outcome": row["outcome"],
            "relevant_kb_ids": row["relevant_kb_ids"],
            "returned_kb_ids": row["returned_kb_ids"],
            "label_reason": row["label_reason"],
        }
        for row in rows
        if row["outcome"] != "correct_at_rank_1"
    ]

    return {
        "queries": total,
        "hit_at_1": {
            "hits": hit_1,
            "total": total,
            "rate": round(hit_1 / total, 6),
        },
        "hit_at_3": {
            "hits": hit_3,
            "total": total,
            "rate": round(hit_3 / total, 6),
        },
        "mean_reciprocal_rank": {
            "reciprocal_rank_sum": reciprocal_sum,
            "total": total,
            "value": round(reciprocal_sum / total, 6),
        },
        "outcomes": dict(sorted(outcome_counts.items())),
        "errors_for_review": errors,
        "timing": {
            "scope": "retrieval-function wall time; first query includes uncached document embeddings",
            "total_ms": round(sum(float(row["elapsed_ms"]) for row in rows), 3),
            "mean_ms": round(sum(float(row["elapsed_ms"]) for row in rows) / total, 3),
        },
    }
