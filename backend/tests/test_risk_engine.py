"""Unit tests for the risk engine.

Covers what thesis 6.4.1 names: factor normalisation, weighted scoring,
threshold boundaries and safety overrides. Boundary values get particular
attention because a small score change alters the authority route.
"""
import pytest

from app.services.risk_engine import (
    DEFAULT_POLICY,
    ApprovalRoute,
    RiskAssessment,
    RiskEngine,
    RiskFactors,
    RiskLevel,
    RiskPolicy,
)


@pytest.fixture
def engine():
    return RiskEngine()


def factors(impact=1, uncertainty=1, evidence=1, irreversibility=1, scope=1):
    """Least-risky factors by default; override only what a test is about."""
    return RiskFactors(
        impact=impact,
        diagnostic_uncertainty=uncertainty,
        evidence_weakness=evidence,
        irreversibility=irreversibility,
        affected_scope=scope,
    )


# --------------------------------------------------------------------------
# Factor validation
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bad", [0, 4, -1, 100])
def test_factor_out_of_range_is_rejected(bad):
    with pytest.raises(ValueError):
        factors(impact=bad)


@pytest.mark.parametrize("bad", [1.5, "2", None, True])
def test_factor_wrong_type_is_rejected(bad):
    with pytest.raises((TypeError, ValueError)):
        factors(impact=bad)


def test_all_factors_are_validated_not_just_the_first():
    with pytest.raises(ValueError):
        factors(scope=9)


# --------------------------------------------------------------------------
# Normalisation: confidence and evidence are inverted exactly once
# --------------------------------------------------------------------------

@pytest.mark.parametrize("rating,expected", [(3, 1), (2, 2), (1, 3)])
def test_confidence_rating_is_inverted(rating, expected):
    """Thesis 5.3.3: C = 4 - confidence_rating."""
    f = RiskFactors.from_ratings(
        impact=1, confidence_rating=rating, evidence_quality=3,
        irreversibility=1, affected_scope=1,
    )
    assert f.diagnostic_uncertainty == expected


@pytest.mark.parametrize("quality,expected", [(3, 1), (2, 2), (1, 3)])
def test_evidence_quality_is_inverted(quality, expected):
    f = RiskFactors.from_ratings(
        impact=1, confidence_rating=3, evidence_quality=quality,
        irreversibility=1, affected_scope=1,
    )
    assert f.evidence_weakness == expected


def test_high_confidence_and_evidence_give_lowest_risk_contributions():
    """Guards against the inversion being applied twice or not at all."""
    best = RiskFactors.from_ratings(
        impact=1, confidence_rating=3, evidence_quality=3,
        irreversibility=1, affected_scope=1,
    )
    assert best.diagnostic_uncertainty == 1
    assert best.evidence_weakness == 1


# --------------------------------------------------------------------------
# Weighted scoring
# --------------------------------------------------------------------------

def test_all_ones_scores_one(engine):
    """Weights sum to 1.0, so the minimum score is exactly 1.0."""
    assert engine.weighted_score(factors()) == pytest.approx(1.0)


def test_all_threes_scores_three(engine):
    f = factors(impact=3, uncertainty=3, evidence=3, irreversibility=3, scope=3)
    assert engine.weighted_score(f) == pytest.approx(3.0)


def test_score_matches_thesis_formula(engine):
    """S = 0.30I + 0.20C + 0.20E + 0.15R + 0.15A."""
    f = factors(impact=3, uncertainty=2, evidence=1, irreversibility=3, scope=2)
    expected = 0.30 * 3 + 0.20 * 2 + 0.20 * 1 + 0.15 * 3 + 0.15 * 2
    assert engine.weighted_score(f) == pytest.approx(expected)


def test_impact_is_weighted_heaviest(engine):
    """Impact at 0.30 must move the score more than any other single factor."""
    base = engine.weighted_score(factors())
    by_impact = engine.weighted_score(factors(impact=3)) - base
    for other in ("uncertainty", "evidence", "irreversibility", "scope"):
        moved = engine.weighted_score(factors(**{other: 3})) - base
        assert by_impact > moved


def test_weights_must_sum_to_one():
    with pytest.raises(ValueError):
        RiskPolicy(weight_impact=0.9)


def test_thresholds_must_be_ordered():
    with pytest.raises(ValueError):
        RiskPolicy(low_max=2.5, medium_max=1.5)


# --------------------------------------------------------------------------
# Threshold boundaries - a small change here flips the approval route
# --------------------------------------------------------------------------

def test_score_exactly_on_low_boundary_is_low(engine):
    assert engine.classify_score(DEFAULT_POLICY.low_max) is RiskLevel.LOW


def test_score_just_above_low_boundary_is_medium(engine):
    assert engine.classify_score(DEFAULT_POLICY.low_max + 0.001) is RiskLevel.MEDIUM


def test_score_exactly_on_medium_boundary_is_medium(engine):
    assert engine.classify_score(DEFAULT_POLICY.medium_max) is RiskLevel.MEDIUM


def test_score_just_above_medium_boundary_is_high(engine):
    assert engine.classify_score(DEFAULT_POLICY.medium_max + 0.001) is RiskLevel.HIGH


def test_minimum_possible_score_is_low(engine):
    assert engine.classify_score(1.0) is RiskLevel.LOW


def test_maximum_possible_score_is_high(engine):
    assert engine.classify_score(3.0) is RiskLevel.HIGH


# --------------------------------------------------------------------------
# Routing
# --------------------------------------------------------------------------

def test_low_routes_to_auto_candidate(engine):
    result = engine.assess(factors())
    assert result.level is RiskLevel.LOW
    assert result.route is ApprovalRoute.AUTO_CANDIDATE
    assert result.requires_human_approval is False


def test_medium_routes_to_user_approval(engine):
    result = engine.assess(factors(impact=2, uncertainty=2, evidence=2, irreversibility=2, scope=2))
    assert result.level is RiskLevel.MEDIUM
    assert result.route is ApprovalRoute.USER_APPROVAL
    assert result.requires_human_approval is True


def test_high_routes_to_expert_or_block(engine):
    result = engine.assess(factors(impact=3, uncertainty=3, evidence=3, irreversibility=3, scope=3))
    assert result.level is RiskLevel.HIGH
    assert result.route is ApprovalRoute.EXPERT_APPROVAL_OR_BLOCK
    assert result.is_blocked_from_automation is True


# --------------------------------------------------------------------------
# Override rules - these must beat the weighted score
# --------------------------------------------------------------------------

def test_missing_evidence_forces_high_despite_low_score(engine):
    """The case the thesis singles out: a low average must not authorise
    action on a diagnosis with no supporting evidence."""
    result = engine.assess(factors(), has_required_evidence=False)
    assert result.score_level is RiskLevel.LOW
    assert result.level is RiskLevel.HIGH
    assert "missing_required_evidence" in result.overrides


def test_privileged_security_action_forces_high(engine):
    result = engine.assess(factors(), is_privileged_security_action=True)
    assert result.level is RiskLevel.HIGH
    assert "privileged_security_action" in result.overrides


def test_irreversible_change_to_shared_resource_forces_high(engine):
    result = engine.assess(factors(irreversibility=3, scope=2))
    assert result.level is RiskLevel.HIGH
    assert "irreversible_shared_resource" in result.overrides


def test_irreversible_change_on_own_device_is_not_overridden(engine):
    """Scope 1 is the user's own device - irreversibility alone must not
    trigger the shared-resource override."""
    result = engine.assess(factors(irreversibility=3, scope=1))
    assert "irreversible_shared_resource" not in result.overrides


def test_no_rollback_on_critical_resource_forces_high(engine):
    result = engine.assess(factors(scope=3), rollback_available=False)
    assert result.level is RiskLevel.HIGH
    assert "no_rollback_on_critical_resource" in result.overrides


def test_catalogue_risk_acts_as_a_floor(engine):
    """A normally-dangerous action cannot be talked down by gentle context."""
    result = engine.assess(factors(), catalogue_risk=RiskLevel.HIGH)
    assert result.score_level is RiskLevel.LOW
    assert result.level is RiskLevel.HIGH
    assert "catalogue_floor" in result.overrides


def test_catalogue_floor_does_not_lower_a_high_context_score(engine):
    """The floor raises only. A LOW catalogue action with terrible context
    stays HIGH."""
    result = engine.assess(
        factors(impact=3, uncertainty=3, evidence=3, irreversibility=3, scope=3),
        catalogue_risk=RiskLevel.LOW,
    )
    assert result.level is RiskLevel.HIGH
    assert "catalogue_floor" not in result.overrides


def test_catalogue_floor_can_be_disabled_by_policy():
    engine = RiskEngine(RiskPolicy(enforce_catalogue_floor=False))
    result = engine.assess(factors(), catalogue_risk=RiskLevel.HIGH)
    assert result.level is RiskLevel.LOW


def test_several_overrides_are_all_recorded(engine):
    result = engine.assess(
        factors(irreversibility=3, scope=3),
        has_required_evidence=False,
        is_privileged_security_action=True,
        rollback_available=False,
    )
    assert result.level is RiskLevel.HIGH
    for name in (
        "missing_required_evidence",
        "privileged_security_action",
        "irreversible_shared_resource",
        "no_rollback_on_critical_resource",
    ):
        assert name in result.overrides


def test_no_overrides_recorded_when_none_apply(engine):
    result = engine.assess(factors())
    assert result.overrides == []
    assert result.level == result.score_level


# --------------------------------------------------------------------------
# Replayability - thesis 5.3.3 requires the same input to be re-scorable
# --------------------------------------------------------------------------

def test_assessment_is_deterministic(engine):
    f = factors(impact=2, uncertainty=2, evidence=3, irreversibility=2, scope=2)
    first = engine.assess(f)
    second = engine.assess(f)
    assert first.to_dict() == second.to_dict()


def test_assessment_records_policy_version_and_weights(engine):
    result = engine.assess(factors())
    assert result.policy_version == DEFAULT_POLICY.version
    assert result.weights == DEFAULT_POLICY.weights()
    assert sum(result.weights.values()) == pytest.approx(1.0)


def test_to_dict_is_serialisable_for_audit(engine):
    import json

    result = engine.assess(factors(impact=3), catalogue_risk=RiskLevel.MEDIUM)
    payload = json.dumps(result.to_dict())
    restored = json.loads(payload)
    assert restored["level"] in {"low", "medium", "high"}
    assert restored["factors"]["impact"] == 3
    assert isinstance(restored["explanation"], list)


def test_score_level_is_preserved_separately_from_final_level(engine):
    """Evaluation needs to know what the score said before safety rules acted."""
    result = engine.assess(factors(), has_required_evidence=False)
    assert result.score_level is RiskLevel.LOW
    assert result.level is RiskLevel.HIGH


# --------------------------------------------------------------------------
# Explanation - it must be readable, and name every factor
# --------------------------------------------------------------------------

def test_explanation_mentions_every_factor(engine):
    result = engine.assess(factors(impact=2))
    text = " ".join(result.explanation)
    for label in ("Impact", "Diagnostic uncertainty", "Evidence weakness",
                  "Irreversibility", "Affected scope"):
        assert label in text


def test_explanation_states_the_override_reason(engine):
    result = engine.assess(factors(), has_required_evidence=False)
    text = " ".join(result.explanation)
    assert "OVERRIDE" in text
    assert "evidence" in text.lower()


def test_explanation_reports_the_route(engine):
    result = engine.assess(factors())
    assert any("Route:" in line for line in result.explanation)


# --------------------------------------------------------------------------
# Scenario checks matching the planned viva demos
# --------------------------------------------------------------------------

def test_demo_low_risk_temp_file_cleanup(engine):
    """Strong evidence, reversible, user's own machine -> automatic."""
    f = RiskFactors.from_ratings(
        impact=1, confidence_rating=3, evidence_quality=3,
        irreversibility=1, affected_scope=1,
    )
    result = engine.assess(f, catalogue_risk=RiskLevel.LOW)
    assert result.level is RiskLevel.LOW
    assert result.route is ApprovalRoute.AUTO_CANDIDATE


def test_demo_medium_risk_kill_browser_process(engine):
    """Interrupts the user's work, but reversible and well evidenced."""
    f = RiskFactors.from_ratings(
        impact=2, confidence_rating=3, evidence_quality=2,
        irreversibility=2, affected_scope=1,
    )
    result = engine.assess(f, catalogue_risk=RiskLevel.MEDIUM)
    assert result.level is RiskLevel.MEDIUM
    assert result.route is ApprovalRoute.USER_APPROVAL


def test_demo_high_risk_winsock_reset(engine):
    """System-wide, needs a restart, catalogued high -> blocked pending expert."""
    f = RiskFactors.from_ratings(
        impact=3, confidence_rating=2, evidence_quality=2,
        irreversibility=3, affected_scope=2,
    )
    result = engine.assess(f, catalogue_risk=RiskLevel.HIGH)
    assert result.level is RiskLevel.HIGH
    assert result.is_blocked_from_automation is True


def test_demo_weak_evidence_raises_a_safe_action(engine):
    """The link the thesis argues for: weak evidence costs autonomy, even for
    an action that is normally automatic."""
    strong = RiskFactors.from_ratings(
        impact=1, confidence_rating=3, evidence_quality=3,
        irreversibility=1, affected_scope=1,
    )
    weak = RiskFactors.from_ratings(
        impact=1, confidence_rating=1, evidence_quality=1,
        irreversibility=1, affected_scope=1,
    )
    assert engine.assess(strong, catalogue_risk=RiskLevel.LOW).route is ApprovalRoute.AUTO_CANDIDATE
    assert engine.assess(weak, catalogue_risk=RiskLevel.LOW).route is not ApprovalRoute.AUTO_CANDIDATE
