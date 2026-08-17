import { useState } from 'react'
import { Shield, AlertCircle, CheckCircle, X, Info } from 'lucide-react'
import '../styles/components/PermissionModal.css'

function PermissionModal({ isOpen, onClose, onGrant, onDeny }) {
  const [understood, setUnderstood] = useState(false)

  if (!isOpen) return null

  const handleGrant = () => {
    if (understood) {
      onGrant()
    }
  }

  return (
    <div className="permission-modal-overlay" onClick={onDeny}>
      <div className="permission-modal" onClick={(e) => e.stopPropagation()}>
        <div className="permission-header">
          <div className="permission-icon-wrapper">
            <Shield size={32} />
          </div>
          <h2>System Information Access</h2>
        </div>

        <div className="permission-body">
          <div className="permission-info">
            <Info size={20} />
            <p>
              This application would like to access system information to provide 
              accurate monitoring data. This includes:
            </p>
          </div>

          <div className="permission-list">
            <div className="permission-item">
              <CheckCircle size={18} className="available" />
              <div>
                <strong>CPU Information</strong>
                <span>Number of CPU cores, architecture</span>
              </div>
            </div>
            <div className="permission-item">
              <CheckCircle size={18} className="available" />
              <div>
                <strong>Memory Usage</strong>
                <span>JavaScript heap memory (browser memory)</span>
              </div>
            </div>
            <div className="permission-item">
              <CheckCircle size={18} className="available" />
              <div>
                <strong>Storage Information</strong>
                <span>Browser storage quota and usage</span>
              </div>
            </div>
            <div className="permission-item">
              <CheckCircle size={18} className="available" />
              <div>
                <strong>Network Status</strong>
                <span>Connection type and speed</span>
              </div>
            </div>
            <div className="permission-item">
              <AlertCircle size={18} className="limited" />
              <div>
                <strong>System-Level Data</strong>
                <span>Full Task Manager data is not available due to browser security restrictions</span>
              </div>
            </div>
          </div>

          <div className="permission-warning">
            <AlertCircle size={18} />
            <div>
              <strong>Important:</strong>
              <p>
                Web browsers cannot access full system Task Manager data for security reasons. 
                We can only access limited browser-level information. Some metrics may be 
                simulated based on available data.
              </p>
            </div>
          </div>

          <div className="permission-checkbox">
            <label>
              <input
                type="checkbox"
                checked={understood}
                onChange={(e) => setUnderstood(e.target.checked)}
              />
              <span>I understand the limitations and want to proceed</span>
            </label>
          </div>
        </div>

        <div className="permission-actions">
          <button className="permission-btn-deny" onClick={onDeny}>
            <X size={18} />
            Deny
          </button>
          <button 
            className="permission-btn-grant" 
            onClick={handleGrant}
            disabled={!understood}
          >
            <CheckCircle size={18} />
            Grant Access
          </button>
        </div>
      </div>
    </div>
  )
}

export default PermissionModal

