"""Risk-adaptive assessment for proposed remediation actions.

Implements the five-factor weighted model from the AutoOps AI thesis (5.3.3):

    S = 0.30*I + 0.20*C + 0.20*E + 0.15*R + 0.15*A

Each factor is scored 1-3 from structured case data. The score places the action
in a LOW / MEDIUM / HIGH class, which in turn selects an approval route.

Three design rules carried over from the thesis, all deliberate:

1. **No LLM scores itself.** Every number here comes from structured fields or
   the action catalogue. A language model may propose an action; it never rates
   the risk of its own proposal.
2. **Overrides dominate the score.** A weighted average can quietly dilute one
   catastrophic factor. Missing evidence, an irreversible change to a shared
   resource, or a privileged security action forces HIGH regardless of the sum.
3. **Everything is replayable.** The factor vector, weights, threshold version
   and any override that fired are all returned, so the same input can be
   re-scored later during evaluation.

Confidence and evidence quality are held positively everywhere a human reads
them (3 = best) and inverted only inside the calculation, per thesis 5.3.3:
``C = 4 - confidence_rating``.

This module is pure: no database, no network, no LLM. That is what makes it
unit-testable at the boundaries, which thesis 6.4.1 requires.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional

__all__ = [
    "RiskLevel",
    "ApprovalRoute",
    "RiskFactors",
    "RiskPolicy",
    "RiskAssessment",
    "RiskEngine",
    "DEFAULT_POLICY",
]

MIN_FACTOR = 1
MAX_FACTOR = 3


class RiskLevel(str, Enum):
    """Risk class assigned to a proposed action."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ApprovalRoute(str, Enum):
    """Who, if anyone, may authorise the action."""

    #: Eligible for automatic execution. Still requires an allow-listed action
    #: and passing preconditions - classification is not permission.
    AUTO_CANDIDATE = "auto_candidate"
    #: The affected user, or support personnel with explicit auto-resolution
    #: authority, must approve.
    USER_APPROVAL = "user_approval"
    #: A second principal at support level 2 or above must approve, or the
    #: action is blocked and escalated.
    EXPERT_APPROVAL_OR_BLOCK = "expert_approval_or_block"


def _validate_factor(name: str, value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an int between {MIN_FACTOR} and {MAX_FACTOR}, got {value!r}")
    if not MIN_FACTOR <= value <= MAX_FACTOR:
        raise ValueError(f"{name} must be between {MIN_FACTOR} and {MAX_FACTOR}, got {value}")
    return value


@dataclass(frozen=True)
class RiskFactors:
    """The five factors, each scored 1 (least risk) to 3 (most risk).

    Note the direction: ``diagnostic_uncertainty`` and ``evidence_weakness`` are
    already inverted. Build them from human-readable ratings with
    :meth:`from_ratings` rather than inverting by hand at each call site.
    """

    impact: int
    diagnostic_uncertainty: int
    evidence_weakness: int
    irreversibility: int
    affected_scope: int

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            _validate_factor(name, value)

    @classmethod
    def from_ratings(
        cls,
        *,
        impact: int,
        confidence_rating: int,
        evidence_quality: int,
        irreversibility: int,
        affected_scope: int,
    ) -> "RiskFactors":
        """Build factors from positively-stated ratings.

        ``confidence_rating`` and ``evidence_quality`` are 3 = best, 1 = worst,
        which is how they are stored and shown. They are inverted here, once,
        as ``4 - rating`` (thesis 5.3.3).
        """
        _validate_factor("confidence_rating", confidence_rating)
        _validate_factor("evidence_quality", evidence_quality)
        return cls(
            impact=impact,
            diagnostic_uncertainty=(MAX_FACTOR + 1) - confidence_rating,
            evidence_weakness=(MAX_FACTOR + 1) - evidence_quality,
            irreversibility=irreversibility,
            affected_scope=affected_scope,
        )

    def as_dict(self) -> Dict[str, int]:
        return asdict(self)


@dataclass(frozen=True)
class RiskPolicy:
    """Weights and thresholds. Configuration, not code.

    ``version`` is recorded on every assessment so a result can be tied to the
    policy that produced it. Bump it whenever a weight or threshold changes,
    otherwise historical results become unreproducible.
    """

    version: str = "v1"

    weight_impact: float = 0.30
    weight_diagnostic_uncertainty: float = 0.20
    weight_evidence_weakness: float = 0.20
    weight_irreversibility: float = 0.15
    weight_affected_scope: float = 0.15

    #: Score at or below this is LOW. Score above ``medium_max`` is HIGH.
    #: Calibrate against labelled scenarios; these are starting values.
    low_max: float = 1.60
    medium_max: float = 2.20

    #: An action's catalogue risk acts as a floor: context may raise an action's
    #: risk but never lower it below how the catalogue classifies it.
    enforce_catalogue_floor: bool = True

    def weights(self) -> Dict[str, float]:
        return {
            "impact": self.weight_impact,
            "diagnostic_uncertainty": self.weight_diagnostic_uncertainty,
            "evidence_weakness": self.weight_evidence_weakness,
            "irreversibility": self.weight_irreversibility,
            "affected_scope": self.weight_affected_scope,
        }

    def __post_init__(self) -> None:
        total = sum(self.weights().values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"weights must sum to 1.0, got {total}")
        if not 0 < self.low_max < self.medium_max:
            raise ValueError(
                f"thresholds must satisfy 0 < low_max < medium_max, got {self.low_max} and {self.medium_max}"
            )


DEFAULT_POLICY = RiskPolicy()

#: Risk levels ordered least to most severe, for floor comparisons.
_SEVERITY = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2}

_ROUTE_BY_LEVEL = {
    RiskLevel.LOW: ApprovalRoute.AUTO_CANDIDATE,
    RiskLevel.MEDIUM: ApprovalRoute.USER_APPROVAL,
    RiskLevel.HIGH: ApprovalRoute.EXPERT_APPROVAL_OR_BLOCK,
}


@dataclass
class RiskAssessment:
    """The full, replayable result of one assessment."""

    factors: RiskFactors
    weighted_score: float
    level: RiskLevel
    route: ApprovalRoute
    #: Names of override rules that fired, in the order checked. Empty when the
    #: level came from the score alone.
    overrides: List[str] = field(default_factory=list)
    #: Level the score alone produced, before overrides. Kept for evaluation:
    #: the gap between this and ``level`` is what the safety rules contributed.
    score_level: Optional[RiskLevel] = None
    policy_version: str = DEFAULT_POLICY.version
    weights: Dict[str, float] = field(default_factory=dict)
    explanation: List[str] = field(default_factory=list)

    @property
    def requires_human_approval(self) -> bool:
        return self.route is not ApprovalRoute.AUTO_CANDIDATE

    @property
    def is_blocked_from_automation(self) -> bool:
        """True when an LLM or agent must not execute this on its own."""
        return self.level is RiskLevel.HIGH

    def to_dict(self) -> Dict:
        """Flat dict for persistence and audit logging."""
        return {
            "factors": self.factors.as_dict(),
            "weighted_score": self.weighted_score,
            "level": self.level.value,
            "route": self.route.value,
            "overrides": list(self.overrides),
            "score_level": self.score_level.value if self.score_level else None,
            "policy_version": self.policy_version,
            "weights": dict(self.weights),
            "explanation": list(self.explanation),
        }


class RiskEngine:
    """Scores proposed remediation actions against a :class:`RiskPolicy`."""

    def __init__(self, policy: RiskPolicy = DEFAULT_POLICY) -> None:
        self.policy = policy

    # -- scoring -------------------------------------------------------------

    def weighted_score(self, factors: RiskFactors) -> float:
        weights = self.policy.weights()
        values = factors.as_dict()
        total = sum(weights[name] * values[name] for name in weights)
        # Guard against float drift making a boundary test flap.
        return round(total, 6)

    def classify_score(self, score: float) -> RiskLevel:
        if score <= self.policy.low_max:
            return RiskLevel.LOW
        if score <= self.policy.medium_max:
            return RiskLevel.MEDIUM
        return RiskLevel.HIGH

    # -- assessment ----------------------------------------------------------

    def assess(
        self,
        factors: RiskFactors,
        *,
        catalogue_risk: Optional[RiskLevel] = None,
        is_privileged_security_action: bool = False,
        has_required_evidence: bool = True,
        rollback_available: bool = True,
    ) -> RiskAssessment:
        """Assess one proposed action.

        Args:
            factors: The five scored factors.
            catalogue_risk: How the action registry classifies this action,
                independent of context. Acts as a floor when the policy enables
                it, so a normally-dangerous action cannot be talked down.
            is_privileged_security_action: Touches credentials, identity, or
                security controls. Always HIGH.
            has_required_evidence: Whether the evidence the action type requires
                was actually retrieved. False always forces HIGH - acting on a
                diagnosis with no supporting evidence is the case the thesis
                singles out.
            rollback_available: Whether a tested rollback exists for this action.

        Returns:
            A :class:`RiskAssessment` carrying the score, level, route, any
            overrides that fired, and a human-readable explanation.
        """
        score = self.weighted_score(factors)
        score_level = self.classify_score(score)
        level = score_level
        overrides: List[str] = []
        explanation = self._explain_factors(factors)

        explanation.append(
            f"Weighted score {score:.3f} falls in {score_level.value.upper()} "
            f"(low <= {self.policy.low_max}, medium <= {self.policy.medium_max})."
        )

        # --- Override rules. Each may only raise the level, never lower it. ---

        if not has_required_evidence:
            overrides.append("missing_required_evidence")
            explanation.append(
                "OVERRIDE: the evidence this action type requires was not retrieved, "
                "so the diagnosis is unsupported. Forced to HIGH."
            )
            level = RiskLevel.HIGH

        if is_privileged_security_action:
            overrides.append("privileged_security_action")
            explanation.append(
                "OVERRIDE: action affects credentials, identity or security controls. Forced to HIGH."
            )
            level = RiskLevel.HIGH

        if factors.irreversibility == MAX_FACTOR and factors.affected_scope >= 2:
            overrides.append("irreversible_shared_resource")
            explanation.append(
                "OVERRIDE: irreversible change affecting a shared resource. Forced to HIGH."
            )
            level = RiskLevel.HIGH

        if not rollback_available and factors.affected_scope == MAX_FACTOR:
            overrides.append("no_rollback_on_critical_resource")
            explanation.append(
                "OVERRIDE: no tested rollback for an action on a shared, critical resource. Forced to HIGH."
            )
            level = RiskLevel.HIGH

        if (
            self.policy.enforce_catalogue_floor
            and catalogue_risk is not None
            and _SEVERITY[catalogue_risk] > _SEVERITY[level]
        ):
            overrides.append("catalogue_floor")
            explanation.append(
                f"OVERRIDE: the action catalogue classifies this action as "
                f"{catalogue_risk.value.upper()}; context may raise that but not lower it."
            )
            level = catalogue_risk

        route = _ROUTE_BY_LEVEL[level]
        explanation.append(f"Route: {route.value}.")

        return RiskAssessment(
            factors=factors,
            weighted_score=score,
            level=level,
            route=route,
            overrides=overrides,
            score_level=score_level,
            policy_version=self.policy.version,
            weights=self.policy.weights(),
            explanation=explanation,
        )

    # -- explanation ---------------------------------------------------------

    _FACTOR_LABELS = {
        "impact": ("Impact", {1: "local or minor", 2: "material but contained", 3: "severe or organisation-wide"}),
        "diagnostic_uncertainty": (
            "Diagnostic uncertainty",
            {1: "confident diagnosis", 2: "some doubt", 3: "low or conflicting signals"},
        ),
        "evidence_weakness": (
            "Evidence weakness",
            {1: "approved and corroborated", 2: "single or dated source", 3: "no supporting evidence"},
        ),
        "irreversibility": (
            "Irreversibility",
            {1: "tested rollback exists", 2: "reversible with effort", 3: "no safe rollback"},
        ),
        "affected_scope": (
            "Affected scope",
            {1: "the user's own device", 2: "shared, non-critical", 3: "shared and critical"},
        ),
    }

    def _explain_factors(self, factors: RiskFactors) -> List[str]:
        weights = self.policy.weights()
        lines = []
        for name, value in factors.as_dict().items():
            label, meanings = self._FACTOR_LABELS[name]
            contribution = weights[name] * value
            lines.append(
                f"{label}: {value}/3 ({meanings[value]}) "
                f"x {weights[name]:.2f} = {contribution:.2f}"
            )
        return lines
