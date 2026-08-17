import QuickActions from './QuickActions'
import '../styles/components/QuickActionsPage.css'

function QuickActionsPage() {
  return (
    <div className="quick-actions-page">
      <div className="page-header">
        <h1>Quick Actions</h1>
        <p>Common troubleshooting actions and commands for IT support</p>
      </div>
      <QuickActions hideHeader={true} />
    </div>
  )
}

export default QuickActionsPage

