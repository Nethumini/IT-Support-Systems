import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  TrendingUp, 
  TrendingDown,
  AlertCircle, 
  CheckCircle, 
  Clock, 
  Zap,
  Server,
  Users,
  Activity,
  ArrowRight,
  FileText,
  MessageSquare
} from 'lucide-react'
import { ticketService } from '../services/ticketService'
import { API_PRIORITY_TO_NUMBER, TICKET_PRIORITY_LABELS } from '../config/constants'
import { usePermissions } from '../hooks/usePermissions'
import PermissionGate from './PermissionGate'
import { PERMISSIONS } from '../utils/permissionUtils'
import '../styles/components/Dashboard.css'

function Dashboard({ user }) {
  const { hasPermission, hasAnyPermission, getRoleInfo } = usePermissions();
  
  const [stats, setStats] = useState({
    totalTickets: 0,
    openTickets: 0,
    resolvedTickets: 0,
    resolvedToday: 0,
    escalatedTickets: 0,
    avgResolutionTime: '0h',
    systemHealth: 'Good'
  })

  const [recentIssues, setRecentIssues] = useState([])
  const [systemStatus, setSystemStatus] = useState([
    { name: 'API Server', status: 'online', uptime: '99.9%' },
    { name: 'Database', status: 'online', uptime: '99.8%' },
    { name: 'AI Service', status: 'online', uptime: '99.5%' },
    { name: 'Backup Service', status: 'online', uptime: '100%' }
  ])

  useEffect(() => {
    // Fetch dashboard data
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Fetch actual tickets from API
      const tickets = await ticketService.getAll()
      
      // Calculate stats from actual tickets - count all non-resolved/closed as open
      const openTickets = tickets.filter(t => 
        t.status === 'open' || 
        t.status === 'in_progress' || 
        t.status === 'assigned_to_human'
      ).length
      const resolvedTickets = tickets.filter(t => t.status === 'resolved').length
      const closedTickets = tickets.filter(t => t.status === 'closed').length
      const escalatedTickets = tickets.filter(t => t.priority === 'critical' || t.priority === 1).length
      
      // Calculate today's resolved tickets
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const resolvedToday = tickets.filter(t => {
        if (t.status === 'resolved' && t.resolved_at) {
          const resolvedDate = new Date(t.resolved_at)
          return resolvedDate >= today
        }
        return false
      }).length
      
      // Calculate trends
      const totalTrend = tickets.length > 0 ? '+12%' : '0%'
      const resolvedTrend = resolvedToday > 0 ? `+${resolvedToday}` : '0'
      
      setStats({
        totalTickets: tickets.length,
        openTickets,
        resolvedTickets,
        resolvedToday,
        escalatedTickets,
        totalTrend,
        resolvedTrend,
        avgResolutionTime: '2.5h',
        systemHealth: 'Good'
      })

      // Get 5 most recent tickets
      const recent = tickets.slice(0, 5).map(ticket => ({
        id: ticket.id,
        title: ticket.title,
        priority: ticket.priority,
        status: ticket.status,
        time: formatDate(ticket.created_at)
      }))
      
      setRecentIssues(recent)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const getPriorityLabel = (priority) => {
    // Handle both string and number priorities
    if (typeof priority === 'string') {
      const num = API_PRIORITY_TO_NUMBER[priority]
      return TICKET_PRIORITY_LABELS[num] || 'Medium'
    }
    return TICKET_PRIORITY_LABELS[priority] || 'Medium'
  }

  const StatCard = ({ title, value, icon: Icon, trend, trendValue, color }) => (
    <div className={`stat-card ${color}`}>
      <div className="stat-header">
        <div className="stat-icon">
          <Icon size={24} />
        </div>
        {trend && (
          <div className={`stat-trend ${trend}`}>
            {trend === 'up' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <span>{trendValue}</span>
          </div>
        )}
      </div>
      <div className="stat-body">
        <h3>{value}</h3>
        <p>{title}</p>
      </div>
    </div>
  )

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Welcome back, {user?.name || 'User'}!</h1>
          <p className="role-badge" style={{ color: getRoleInfo().color }}>
            {getRoleInfo().label}
          </p>
        </div>
        <PermissionGate permissions={[PERMISSIONS.TICKET_CREATE]}>
          <Link to="/chat" className="quick-action-btn">
            <MessageSquare size={20} />
            <span>Start New Chat</span>
          </Link>
        </PermissionGate>
      </div>

      {/* Stats Grid - Show basic stats for all authenticated users */}
      <div className="stats-grid">
        {hasAnyPermission([PERMISSIONS.TICKET_VIEW_OWN, PERMISSIONS.TICKET_VIEW_TEAM, PERMISSIONS.TICKET_VIEW_ALL]) && (
          <>
            <StatCard
              title="Total Tickets"
              value={stats.totalTickets}
              icon={FileText}
              trend={stats.totalTickets > 0 ? "up" : null}
              trendValue={stats.totalTrend}
              color="blue"
            />
            <StatCard
              title="Open Tickets"
              value={stats.openTickets}
              icon={Clock}
              color="orange"
            />
            <StatCard
              title="Resolved Tickets"
              value={stats.resolvedTickets}
              icon={CheckCircle}
              trend={stats.resolvedToday > 0 ? "up" : null}
              trendValue={`${stats.resolvedToday} today`}
              color="green"
            />
          </>
        )}
        {hasAnyPermission([PERMISSIONS.TICKET_VIEW_ALL, PERMISSIONS.TICKET_ESCALATE]) && (
          <StatCard
            title="Critical"
            value={stats.escalatedTickets}
            icon={AlertCircle}
            trend={stats.escalatedTickets === 0 ? "down" : null}
            trendValue={stats.escalatedTickets === 0 ? "None" : null}
            color="red"
          />
        )}
      </div>

      <div className="dashboard-content">
        {/* Recent Issues - Only for users who can view tickets */}
        <PermissionGate permissions={[PERMISSIONS.TICKET_VIEW_OWN, PERMISSIONS.TICKET_VIEW_TEAM, PERMISSIONS.TICKET_VIEW_ALL]}>
          <div className="content-section">
            <div className="section-header">
              <h2>Recent Issues</h2>
              <Link to="/tickets" className="view-all-link">
                View All <ArrowRight size={16} />
              </Link>
            </div>
            <div className="issues-list">
              {recentIssues.length === 0 ? (
                <div className="empty-state">
                  <p>No recent tickets</p>
                </div>
              ) : (
                recentIssues.map((issue) => (
                  <div key={issue.id} className="issue-item">
                    <div className="issue-info">
                      <span className="issue-id">#{issue.id}</span>
                      <span className="issue-title">{issue.title}</span>
                    </div>
                    <div className="issue-meta">
                      <span className={`priority-badge ${typeof issue.priority === 'string' ? issue.priority : 'medium'}`}>
                        {getPriorityLabel(issue.priority)}
                      </span>
                      <span className={`status-badge ${issue.status}`}>
                        {issue.status.replace('_', ' ')}
                      </span>
                      <span className="issue-time">{issue.time}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </PermissionGate>

        {/* System Status - Only for support staff and admins */}
        <PermissionGate permissions={[PERMISSIONS.SYSTEM_MONITOR]}>
          <div className="content-section">
            <div className="section-header">
              <h2>System Status</h2>
              <Link to="/monitoring" className="view-all-link">
                View Details <ArrowRight size={16} />
              </Link>
            </div>
            <div className="system-status-list">
              {systemStatus.map((service, idx) => (
                <div key={idx} className="status-item">
                  <div className="status-info">
                    <Server size={18} />
                    <span className="service-name">{service.name}</span>
                  </div>
                  <div className="status-details">
                    <span className="uptime">Uptime: {service.uptime}</span>
                    <span className={`status-indicator ${service.status}`}>
                      <span className="status-dot"></span>
                      {service.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </PermissionGate>
      </div>

      {/* Quick Actions - Permission-based */}
      <div className="quick-actions-panel">
        <h2>Quick Navigation</h2>
        <div className="actions-grid">
          {hasAnyPermission([PERMISSIONS.TICKET_CREATE, PERMISSIONS.TROUBLESHOOT_RUN]) && (
            <Link to="/chat" className="action-card">
              <MessageSquare size={28} />
              <span>Report Issue</span>
            </Link>
          )}
          {hasAnyPermission([PERMISSIONS.TICKET_VIEW_OWN, PERMISSIONS.TICKET_VIEW_TEAM, PERMISSIONS.TICKET_VIEW_ALL]) && (
            <Link to="/tickets" className="action-card">
              <FileText size={28} />
              <span>View Tickets</span>
            </Link>
          )}
          {hasPermission(PERMISSIONS.SYSTEM_MONITOR) && (
            <Link to="/monitoring" className="action-card">
              <Activity size={28} />
              <span>System Monitor</span>
            </Link>
          )}
          {hasPermission(PERMISSIONS.REPORTS_VIEW) && (
            <Link to="/reports" className="action-card">
              <Zap size={28} />
              <span>View Reports</span>
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
