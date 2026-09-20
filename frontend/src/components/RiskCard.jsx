import { useState } from 'react'
import PropTypes from 'prop-types'
import { ShieldCheck, ShieldAlert, ShieldX, ChevronDown, ChevronUp, Check, X } from 'lucide-react'
import { remediationService } from '../services/remediationService'

/**
 * Shows the risk assessment behind one proposed action, and the decision the
 * user is being asked to make.
 *
 * What the panel sees at a viva is this component: the factor breakdown, the
 * approval route, and afterwards whether the problem was actually verified as
 * solved. So it shows the working, not just a verdict.
 */

const RISK_META = {
  low: { label: 'Low risk', Icon: ShieldCheck, className: 'risk-low' },
  medium: { label: 'Medium risk', Icon: ShieldAlert, className: 'risk-medium' },
  high: { label: 'High risk', Icon: ShieldX, className: 'risk-high' }
}

const ROUTE_TEXT = {
  auto_candidate: 'Can run automatically',
  user_approval: 'Needs your approval',
  expert_approval_or_block: 'Blocked — needs an IT expert'
}

const VERIFICATION_TEXT = {
  verified_success: 'Verified: the problem is fixed',
  verified_failure: 'Verified: the problem is NOT fixed',
  inconclusive: 'Could not verify — not reported as fixed'
}

/**
 * A diagnostic action reads state and changes nothing, so "the problem is
 * fixed" would be false even when its check passes. It confirmed the reading,
 * not a resolution.
 */
function verificationText(outcome) {
  const isDiagnostic = outcome?.post_check?.expected === 'no change to system state'
  if (isDiagnostic && outcome.verification_status === 'verified_success') {
    return 'Checked — no change made'
  }
  return VERIFICATION_TEXT[outcome?.verification_status] || outcome?.status
}

export default function RiskCard({ action, onOutcome }) {
  const [expanded, setExpanded] = useState(false)
  const [busy, setBusy] = useState(false)
  const [outcome, setOutcome] = useState(null)
  const [error, setError] = useState(null)

  if (!action?.risk_level) return null

  const meta = RISK_META[action.risk_level] || RISK_META.medium
  const { Icon } = meta
  const route = action.approval_route
  const blocked = route === 'expert_approval_or_block'
  const needsApproval = route === 'user_approval'
  const canRun = route === 'auto_candidate'

  const finish = (result) => {
    setOutcome(result)
    if (onOutcome) onOutcome(result)
  }

  const run = async (withApproval) => {
    setBusy(true)
    setError(null)
    try {
      const result = withApproval
        ? await remediationService.approveAndExecute(action.remediation_id)
        : await remediationService.execute(action.remediation_id)
      finish(result)
    } catch (err) {
      setError(err?.message || 'Could not run this action')
    } finally {
      setBusy(false)
    }
  }

  const decline = async () => {
    setBusy(true)
    setError(null)
    try {
      const result = await remediationService.reject(action.remediation_id, 'Declined by user')
      finish(result)
    } catch (err) {
      setError(err?.message || 'Could not reject this action')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className={`risk-card ${meta.className}`}>
      <div className="risk-head">
        <Icon size={16} />
        <span className="risk-label">{meta.label}</span>
        {action.risk_score != null && (
          <span className="risk-score">score {Number(action.risk_score).toFixed(2)}</span>
        )}
        <button
          type="button"
          className="risk-toggle"
          onClick={() => setExpanded(!expanded)}
          aria-expanded={expanded}
        >
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          {expanded ? 'Hide working' : 'Why?'}
        </button>
      </div>

      <p className="risk-route">{ROUTE_TEXT[route] || route}</p>

      {Array.isArray(action.risk_overrides) && action.risk_overrides.length > 0 && (
        <ul className="risk-overrides">
          {action.risk_overrides.map((name) => (
            <li key={name}>Safety rule applied: {name.replace(/_/g, ' ')}</li>
          ))}
        </ul>
      )}

      {expanded && Array.isArray(action.risk_explanation) && (
        <ol className="risk-working">
          {action.risk_explanation.map((line, i) => (
            <li key={i}>{line}</li>
          ))}
        </ol>
      )}

      {error && <p className="risk-error">{error}</p>}

      {outcome ? (
        <div className={`risk-outcome outcome-${outcome.verification_status || outcome.status}`}>
          <strong>{verificationText(outcome)}</strong>
          {outcome.post_check?.reason && <p>{outcome.post_check.reason}</p>}
          {outcome.status === 'escalated' && outcome.escalation_reason && (
            <p>{outcome.escalation_reason}</p>
          )}
        </div>
      ) : (
        <div className="risk-actions">
          {canRun && (
            <button type="button" className="risk-btn run" disabled={busy} onClick={() => run(false)}>
              {busy ? 'Running…' : 'Run it'}
            </button>
          )}
          {needsApproval && (
            <>
              <button type="button" className="risk-btn approve" disabled={busy} onClick={() => run(true)}>
                <Check size={14} /> {busy ? 'Working…' : 'Approve and run'}
              </button>
              <button type="button" className="risk-btn decline" disabled={busy} onClick={decline}>
                <X size={14} /> No thanks
              </button>
            </>
          )}
          {blocked && (
            <p className="risk-blocked">
              This will not run automatically. It has been sent to an IT expert for review.
            </p>
          )}
        </div>
      )}
    </div>
  )
}

RiskCard.propTypes = {
  action: PropTypes.shape({
    remediation_id: PropTypes.number,
    risk_level: PropTypes.string,
    risk_score: PropTypes.number,
    approval_route: PropTypes.string,
    risk_explanation: PropTypes.array,
    risk_overrides: PropTypes.array
  }).isRequired,
  onOutcome: PropTypes.func
}
