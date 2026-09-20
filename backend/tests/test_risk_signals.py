"""Tests for turning chat signals into risk factors."""
import pytest

from app.services.risk_signals import (
    confidence_rating,
    evidence_quality,
    factors_for_action,
    has_required_evidence,
)


def test_no_citations_is_weakest_evidence():
    assert evidence_quality([]) == 1
    assert evidence_quality(None) == 1


def test_strong_match_is_best_evidence():
    assert evidence_quality([{"similarity_score": 0.83}]) == 3


def test_borderline_match_is_middling():
    assert evidence_quality([{"similarity_score": 0.72}]) == 2


def test_best_match_wins_not_the_count():
    """Three weak matches are the same weak claim repeated, not strong evidence."""
    many_weak = [{"similarity_score": 0.55}] * 3
    assert evidence_quality(many_weak) == 1


@pytest.mark.parametrize("conf,expected", [(0.95, 3), (0.70, 2), (0.40, 1), (None, 1)])
def test_confidence_bands(conf, expected):
    assert confidence_rating(conf) == expected


def test_diagnostic_needs_no_evidence():
    """Reading state is how evidence is gathered; requiring evidence first
    would be circular."""
    assert has_required_evidence("list_top_processes", []) is True
    assert has_required_evidence("check_disk_space", None) is True


def test_state_changing_action_needs_evidence():
    assert has_required_evidence("clear_temp_files", []) is False
    assert has_required_evidence("clear_temp_files", [{"kb_id": "KB-007"}]) is True


def test_unknown_action_needs_evidence():
    assert has_required_evidence("not_an_action", []) is False


def test_weak_evidence_raises_risk_of_a_safe_action():
    """The mechanism the thesis argues for: poor evidence costs autonomy."""
    action = {"action_id": "clear_temp_files", "risk_level": "low"}
    strong = factors_for_action(action, citations=[{"similarity_score": 0.85}], classifier_confidence=0.9)
    weak = factors_for_action(action, citations=[], classifier_confidence=0.3)
    assert weak.evidence_weakness > strong.evidence_weakness
    assert weak.diagnostic_uncertainty > strong.diagnostic_uncertainty


def test_read_only_action_scores_lowest_impact():
    factors = factors_for_action({"action_id": "check_disk_space", "risk_level": "low"})
    assert factors.impact == 1
    assert factors.irreversibility == 1
    assert factors.affected_scope == 1


def test_system_wide_action_has_wider_scope():
    factors = factors_for_action({"action_id": "reset_winsock", "risk_level": "high"})
    assert factors.affected_scope == 2
    assert factors.irreversibility == 3
