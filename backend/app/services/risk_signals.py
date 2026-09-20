"""Derives risk factors from what the chat actually observed.

The risk engine takes five numbers. This module produces them from the signals
the conversation already has: how well the knowledge base matched, how sure the
classifier was, and what the action catalogue says about the action itself.

Two properties matter here:

* **No LLM scores its own proposal.** Every number below comes from a
  similarity score, a classifier confidence, or a static property of the
  action. The model that suggested the action has no say in how risky it is
  judged to be.
* **Weak evidence costs autonomy.** A poor knowledge-base match raises
  ``evidence_weakness``, which raises the score, which can push a normally
  automatic action into requiring approval. That link is the mechanism the
  thesis argues for, so it is implemented here rather than described.

Thresholds are module constants so they can be calibrated against labelled
scenarios and reported, as thesis 5.3.3 requires of every threshold.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.services.risk_engine import RiskFactors, RiskLevel
from app.services.verification import CONTRACTS

#: Similarity at or above this counts as strong, corroborated evidence.
STRONG_EVIDENCE = 0.80
#: Below this, a match is too weak to ground an action on.
WEAK_EVIDENCE = 0.70

#: Classifier confidence bands.
HIGH_CONFIDENCE = 0.85
MEDIUM_CONFIDENCE = 0.65

#: Actions whose effect reaches beyond the user's own session. Everything else
#: is assumed to affect only the user's device, which is the common case.
SHARED_SCOPE_ACTIONS = {
    "reset_winsock": 2,
    "reset_network_adapter": 2,
    "restart_service": 2,
    "release_renew_ip": 2,
    "flush_dns": 2,
}

#: Actions touching credentials, identity or security controls. These force
#: HIGH through an override rather than through the score.
PRIVILEGED_SECURITY_ACTIONS: set = set()

_IMPACT_BY_CATALOGUE_RISK = {
    RiskLevel.LOW: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
}


def evidence_quality(citations: Optional[List[Dict[str, Any]]]) -> int:
    """Rate retrieved evidence 1 (none) to 3 (strong, corroborated).

    Uses the best match only. Three weak matches are not better evidence than
    one weak match - they are the same weak claim repeated.
    """
    if not citations:
        return 1
    scores = [c.get("similarity_score") or 0 for c in citations]
    best = max(scores) if scores else 0
    if best >= STRONG_EVIDENCE:
        return 3
    if best >= WEAK_EVIDENCE:
        return 2
    return 1


def confidence_rating(classifier_confidence: Optional[float]) -> int:
    """Rate diagnostic confidence 1 (low) to 3 (confident)."""
    if classifier_confidence is None:
        return 1
    if classifier_confidence >= HIGH_CONFIDENCE:
        return 3
    if classifier_confidence >= MEDIUM_CONFIDENCE:
        return 2
    return 1


def catalogue_risk(action: Dict[str, Any]) -> Optional[RiskLevel]:
    """Read the action's own risk level from the suggestion payload."""
    raw = (action.get("risk_level") or "").strip().lower()
    try:
        return RiskLevel(raw) if raw else None
    except ValueError:
        return None


def _impact(action_id: str, level: Optional[RiskLevel]) -> int:
    contract = CONTRACTS.get(action_id)
    if contract is not None and contract.read_only:
        return 1
    return _IMPACT_BY_CATALOGUE_RISK.get(level, 2)


def _irreversibility(action_id: str, level: Optional[RiskLevel]) -> int:
    """1 when it can be undone, 3 when it cannot.

    A read-only action changes nothing, so there is nothing to reverse. An
    action with a registered rollback is reversible. Everything else cannot be
    undone, and is rated by how far its effect reaches.
    """
    contract = CONTRACTS.get(action_id)
    if contract is None:
        return 3  # unknown action: assume the worst
    if contract.read_only:
        return 1
    if contract.has_rollback:
        return 1
    return 3 if level is RiskLevel.HIGH else 2


def _affected_scope(action_id: str) -> int:
    contract = CONTRACTS.get(action_id)
    if contract is not None and contract.read_only:
        return 1
    return SHARED_SCOPE_ACTIONS.get(action_id, 1)


def factors_for_action(
    action: Dict[str, Any],
    *,
    citations: Optional[List[Dict[str, Any]]] = None,
    classifier_confidence: Optional[float] = None,
) -> RiskFactors:
    """Build the five factors for one suggested action.

    Args:
        action: The suggestion payload, carrying at least ``action_id`` and
            optionally the catalogue ``risk_level``.
        citations: Knowledge-base articles behind the diagnosis, as returned to
            the user. Their best similarity score sets evidence quality.
        classifier_confidence: How sure the intent classifier was, 0 to 1.
    """
    action_id = action.get("action_id") or action.get("id") or ""
    level = catalogue_risk(action)

    return RiskFactors.from_ratings(
        impact=_impact(action_id, level),
        confidence_rating=confidence_rating(classifier_confidence),
        evidence_quality=evidence_quality(citations),
        irreversibility=_irreversibility(action_id, level),
        affected_scope=_affected_scope(action_id),
    )


def is_privileged_security_action(action_id: str) -> bool:
    return action_id in PRIVILEGED_SECURITY_ACTIONS


def has_required_evidence(
    action_id: str,
    citations: Optional[List[Dict[str, Any]]],
) -> bool:
    """Whether the evidence this action *requires* was actually retrieved.

    The thesis override is "missing **required** evidence" (5.3.3), and a
    read-only diagnostic requires none: reading disk space or listing processes
    is how evidence gets gathered in the first place. Blocking diagnostics for
    lack of evidence would be circular - the system could never collect the
    evidence that would let it act.

    An action that changes state does require evidence, and gets no such
    exemption.
    """
    contract = CONTRACTS.get(action_id)
    if contract is not None and contract.read_only:
        return True
    return bool(citations)


def explain_signals(
    citations: Optional[List[Dict[str, Any]]],
    classifier_confidence: Optional[float],
) -> Dict[str, Any]:
    """The raw signals behind the ratings, for the audit trail and the UI."""
    best = max((c.get("similarity_score") or 0 for c in citations), default=0) if citations else 0
    return {
        "evidence_count": len(citations or []),
        "best_similarity": round(best, 3),
        "evidence_quality": evidence_quality(citations),
        "classifier_confidence": classifier_confidence,
        "confidence_rating": confidence_rating(classifier_confidence),
        "thresholds": {
            "strong_evidence": STRONG_EVIDENCE,
            "weak_evidence": WEAK_EVIDENCE,
            "high_confidence": HIGH_CONFIDENCE,
            "medium_confidence": MEDIUM_CONFIDENCE,
        },
    }
