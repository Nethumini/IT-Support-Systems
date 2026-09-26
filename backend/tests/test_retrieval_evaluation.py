"""Tests for the labelled retrieval benchmark and its metric calculations."""
import json
from pathlib import Path

import pytest

from evaluation.retrieval_evaluation import (
    DEFAULT_QUERY_PATH,
    RetrievalQuery,
    load_query_set,
    measure_query,
    relevant_rank,
    run_queries,
    summarize,
)


DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "ticketing_system_data_new.json"


def _query(relevant=("KB-002",)):
    return RetrievalQuery(
        id="RQ-TEST",
        query="test query",
        category="software",
        relevant_kb_ids=tuple(relevant),
        label_reason="fixed test label",
    )


def _result(kb_id, score=0.8):
    return {"kb_id": kb_id, "title": kb_id, "similarity_score": score}


def test_query_set_has_one_label_for_every_fixed_kb_article():
    metadata, queries = load_query_set()
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    kb_ids = {article["id"] for article in dataset["knowledge_base"]}
    labelled_ids = {kb_id for query in queries for kb_id in query.relevant_kb_ids}

    assert metadata["version"] == "1.0"
    assert len(queries) == 30
    assert len({query.id for query in queries}) == len(queries)
    assert labelled_ids == kb_ids


def test_every_label_has_a_reason_and_valid_category():
    _, queries = load_query_set()
    allowed = {"account", "hardware", "network", "performance", "security", "software"}
    for query in queries:
        assert query.label_reason
        assert query.category in allowed


def test_loader_rejects_duplicate_query_ids(tmp_path):
    payload = {
        "queries": [
            {"id": "same", "query": "a", "category": "x", "relevant_kb_ids": ["KB-1"], "label_reason": "a"},
            {"id": "same", "query": "b", "category": "x", "relevant_kb_ids": ["KB-2"], "label_reason": "b"},
        ]
    }
    path = tmp_path / "duplicate.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_query_set(path)


def test_relevant_rank_accepts_any_prelabelled_relevant_article():
    assert relevant_rank(["KB-001", "KB-003"], ["KB-002", "KB-003"]) == 2
    assert relevant_rank(["KB-001"], ["KB-002"]) is None


def test_measure_query_reports_rank_one_hit():
    row = measure_query(_query(), [_result("KB-002"), _result("KB-003")])
    assert row["hit_at_1"] is True
    assert row["hit_at_3"] is True
    assert row["reciprocal_rank"] == 1.0
    assert row["outcome"] == "correct_at_rank_1"


def test_measure_query_reports_lower_rank_and_reciprocal_rank():
    row = measure_query(
        _query(),
        [_result("KB-001"), _result("KB-002"), _result("KB-003")],
    )
    assert row["hit_at_1"] is False
    assert row["hit_at_3"] is True
    assert row["relevant_rank"] == 2
    assert row["reciprocal_rank"] == 0.5
    assert row["outcome"] == "relevant_below_rank_1"


def test_measure_query_distinguishes_no_result_from_wrong_result():
    no_result = measure_query(_query(), [])
    wrong_result = measure_query(_query(), [_result("KB-099")])
    assert no_result["outcome"] == "no_results_above_threshold"
    assert wrong_result["outcome"] == "relevant_missing_from_top_k"


def test_summary_has_explicit_numerators_and_denominators():
    rows = [
        {**measure_query(_query(), [_result("KB-002")]), "elapsed_ms": 10},
        {**measure_query(_query(), [_result("KB-001"), _result("KB-002")]), "elapsed_ms": 20},
        {**measure_query(_query(), []), "elapsed_ms": 30},
    ]
    report = summarize(rows)
    assert report["hit_at_1"] == {"hits": 1, "total": 3, "rate": 0.333333}
    assert report["hit_at_3"] == {"hits": 2, "total": 3, "rate": 0.666667}
    assert report["mean_reciprocal_rank"] == {
        "reciprocal_rank_sum": 1.5,
        "total": 3,
        "value": 0.5,
    }
    assert len(report["errors_for_review"]) == 2
    assert report["timing"]["mean_ms"] == 20.0


def test_summary_refuses_empty_input():
    with pytest.raises(ValueError, match="empty"):
        summarize([])


def test_run_queries_uses_the_production_retrieval_interface():
    class FakeAnalyzer:
        def __init__(self):
            self.calls = []

        def find_similar_issues(self, description, category, limit=3):
            self.calls.append((description, category, limit))
            return [_result("KB-002")]

    analyzer = FakeAnalyzer()
    rows = run_queries(analyzer, [_query()], limit=3)
    assert analyzer.calls == [("test query", "software", 3)]
    assert rows[0]["hit_at_1"] is True
    assert rows[0]["elapsed_ms"] >= 0


def test_default_query_file_is_versioned_next_to_the_harness():
    assert DEFAULT_QUERY_PATH.name == "retrieval_queries.json"
    assert DEFAULT_QUERY_PATH.exists()
