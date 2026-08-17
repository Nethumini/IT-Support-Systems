import { useState } from 'react'
import { X, AlertTriangle, Shield, Zap, Clock, CheckCircle, XCircle, Loader, Play, Terminal } from 'lucide-react'
import '../styles/components/ActionModal.css'

/**
 * Action Permission Modal - Shows action details and requests user approval
 */
function ActionModal({ 
  isOpen, 
  onClose, 
  action, 
  onApprove, 
  onCancel,
  isExecuting = false,
  result = null 
}) {
  const [highRiskConfirmed, setHighRiskConfirmed] = useState(false)
  
  if (!isOpen || !action) return null
  
  const isHighRisk = action.risk_level === 'high' || action.risk_level === 'medium'
  const canExecute = !isHighRisk || highRiskConfirmed

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
      case 'low':
        return <Shield className="risk-icon low" />
      case 'medium':
        return <AlertTriangle className="risk-icon medium" />
      case 'high':
        return <AlertTriangle className="risk-icon high" />
      default:
        return <Shield className="risk-icon" />
    }
  }

  const getRiskLabel = (riskLevel) => {
    switch (riskLevel) {
      case 'low':
        return { text: 'Low Risk', description: 'Safe operation, read-only or minimal impact' }
      case 'medium':
        return { text: 'Medium Risk', description: 'May affect running applications' }
      case 'high':
        return { text: 'High Risk', description: 'System-level changes, may require restart' }
      default:
        return { text: 'Unknown', description: '' }
    }
  }

  const riskInfo = getRiskLabel(action.risk_level)

  return (
    <div className="action-modal-overlay" onClick={onClose}>
      <div className="action-modal" onClick={e => e.stopPropagation()}>
        <div className="action-modal-header">
          <div className="action-modal-title">
            <Zap className="action-icon" />
            <h2>Automated Action</h2>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X />
          </button>
        </div>

        <div className="action-modal-content">
          {/* Action Details */}
          <div className="action-details">
            <h3>{action.name}</h3>
            <p className="action-description">{action.description}</p>
            
            {/* Risk Level */}
            <div className={`risk-badge ${action.risk_level}`}>
              {getRiskIcon(action.risk_level)}
              <div className="risk-text">
                <span className="risk-label">{riskInfo.text}</span>
                <span className="risk-description">{riskInfo.description}</span>
              </div>
            </div>

            {/* Parameters */}
            {action.parameters && Object.keys(action.parameters).length > 0 && (
              <div className="action-params">
                <h4>Parameters:</h4>
                <div className="params-list">
                  {Object.entries(action.parameters).map(([key, value]) => (
                    <div key={key} className="param-item">
                      <span className="param-key">{key}:</span>
                      <span className="param-value">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Estimated Duration */}
            <div className="action-duration">
              <Clock size={16} />
              <span>Estimated time: ~{action.estimated_duration || 5} seconds</span>
            </div>

            {/* Command Preview (for transparency) */}
            {action.command_preview && (
              <div className="command-preview">
                <h4><Terminal size={14} /> Command to execute:</h4>
                <code>{action.command_preview}</code>
              </div>
            )}
          </div>

          {/* Execution Status */}
          {isExecuting && (
            <div className="execution-status executing">
              <Loader className="spin" />
              <span>Executing action...</span>
            </div>
          )}

          {/* Result */}
          {result && (
            <div className={`execution-result ${result.success ? 'success' : 'error'}`}>
              {result.success ? (
                <>
                  <CheckCircle className="result-icon" />
                  <div className="result-text">
                    <strong>Success!</strong>
                    <p>{result.message}</p>
                    {result.output && (
                      <pre className="result-output">{JSON.stringify(result.output, null, 2)}</pre>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <XCircle className="result-icon" />
                  <div className="result-text">
                    <strong>Failed</strong>
                    <p>{result.message || result.error}</p>
                  </div>
                </>
              )}
            </div>
          )}
          
          {/* High Risk Confirmation */}
          {isHighRisk && !result && !isExecuting && (
            <div className="high-risk-confirmation">
              <AlertTriangle size={18} className="warning-icon" />
              <label className="confirmation-checkbox">
                <input
                  type="checkbox"
                  checked={highRiskConfirmed}
                  onChange={(e) => setHighRiskConfirmed(e.target.checked)}
                />
                <span>
                  I understand this action may affect running processes or system settings. 
                  {action.id?.startsWith('kill_process') && (
                    <strong> This will terminate the process immediately.</strong>
                  )}
                </span>
              </label>
            </div>
          )}
        </div>

        <div className="action-modal-footer">
          {!result && !isExecuting && (
            <>
              <button className="btn-cancel" onClick={onCancel}>
                <XCircle size={18} />
                Cancel
              </button>
              <button 
                className="btn-approve" 
                onClick={onApprove}
                disabled={!canExecute}
                title={!canExecute ? "Please confirm you understand the risks" : ""}
              >
                <Play size={18} />
                Execute Action
              </button>
            </>
          )}
          
          {(result || isExecuting) && (
            <button className="btn-close" onClick={onClose}>
              Close
            </button>
          )}
        </div>

        {/* Security Notice */}
        <div className="security-notice">
          <Shield size={14} />
          <span>
            This action will be executed on your local system. 
            Only approved, safe commands are allowed.
          </span>
        </div>
      </div>
    </div>
  )
}

/**
 * Inline Action Button - Shows in chat when bot suggests an action
 */
export function ActionButton({ action, onExecute, isLoading = false }) {
  const getRiskClass = (level) => {
    switch (level) {
      case 'low': return 'risk-low'
      case 'medium': return 'risk-medium'
      case 'high': return 'risk-high'
      default: return ''
    }
  }

  return (
    <button 
      className={`action-button ${getRiskClass(action.risk_level)}`}
      onClick={() => onExecute(action)}
      disabled={isLoading}
    >
      {isLoading ? (
        <Loader className="spin" size={16} />
      ) : (
        <Zap size={16} />
      )}
      <span>{action.name}</span>
      {action.risk_level !== 'low' && (
        <span className="risk-indicator">{action.risk_level}</span>
      )}
    </button>
  )
}

/**
 * Action Suggestions Panel - Shows suggested actions based on issue
 */
export function ActionSuggestions({ suggestions, onSelectAction, userEmail }) {
  const [loadingAction, setLoadingAction] = useState(null)

  if (!suggestions || suggestions.length === 0) return null

  const handleSelect = async (action) => {
    setLoadingAction(action.id)
    try {
      await onSelectAction(action)
    } finally {
      setLoadingAction(null)
    }
  }

  return (
    <div className="action-suggestions">
      <div className="suggestions-header">
        <Zap size={16} />
        <span>Suggested Actions</span>
      </div>
      <div className="suggestions-list">
        {suggestions.map((action) => (
          <ActionButton
            key={action.id}
            action={action}
            onExecute={handleSelect}
            isLoading={loadingAction === action.id}
          />
        ))}
      </div>
    </div>
  )
}

export default ActionModal
