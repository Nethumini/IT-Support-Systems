import { Database, ArrowRight, Clock } from 'lucide-react'
import '../styles/components/KnowledgeBasePage.css'

function KnowledgeBasePage() {
  return (
    <div className="knowledge-base-container">
      <div className="knowledge-base-card">
        <Database size={64} className="knowledge-base-icon" />
        <h1>Knowledge Base</h1>
        <p>
          This feature is coming soon! Access comprehensive documentation, 
          troubleshooting guides, and solutions to common IT issues.
        </p>
        <div className="features-list">
          <div className="feature-item">
            <ArrowRight size={18} />
            <span>Searchable documentation library</span>
          </div>
          <div className="feature-item">
            <ArrowRight size={18} />
            <span>Step-by-step troubleshooting guides</span>
          </div>
          <div className="feature-item">
            <ArrowRight size={18} />
            <span>Common issues and solutions</span>
          </div>
          <div className="feature-item">
            <ArrowRight size={18} />
            <span>Best practices and tips</span>
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

export default KnowledgeBasePage
