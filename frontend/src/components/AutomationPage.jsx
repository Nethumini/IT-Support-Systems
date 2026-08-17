import { Zap, ArrowRight, Clock } from 'lucide-react'
import '../styles/components/AutomationPage.css'

function AutomationPage() {
  return (
    <div className="automation-container">
      <div className="automation-card">
        <Zap size={64} className="automation-icon" />
        <h1>Automation Rules</h1>
        <p>
          This feature is coming soon! Here you'll be able to create automated workflows, 
          set up triggers, and define custom rules for ticket handling.
        </p>
        <div className="features-list">
          <div className="feature-item">
            <ArrowRight size={18} />
            <span>Auto-assign tickets based on category</span>
          </div>
          <div className="feature-item">
            <ArrowRight size={18} />
            <span>Trigger actions on ticket status changes</span>
          </div>
          <div className="feature-item">
            <ArrowRight size={18} />
            <span>Schedule automated system checks</span>
          </div>
          <div className="feature-item">
            <ArrowRight size={18} />
            <span>Set up email notifications and alerts</span>
          </div>
        </div>
        <div className="coming-soon-badge">
          <Clock size={16} />
          <span>Coming Soon</span>
        </div>
      </div>
    </div>
  )
}

export default AutomationPage
