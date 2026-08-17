import { NavLink } from 'react-router-dom'
import { useMemo } from 'react'
import { 
  LayoutDashboard, 
  MessageSquare, 
  FileText, 
  Activity, 
  BarChart3, 
  Settings, 
  LogOut, 
  Bot,
  User,
  Shield,
  Bell,
  Database,
  Zap,
  AlertCircle,
  Rocket,
  Users,
  FileCheck
} from 'lucide-react'
import ThemeToggle from './ThemeToggle'
import { usePermissions } from '../hooks/usePermissions'
import { PERMISSIONS } from '../utils/permissionUtils'
import '../styles/components/Sidebar.css'

function Sidebar({ user, onLogout }) {
  const { hasPermission, hasAnyPermission, isAdmin, getRoleInfo } = usePermissions();

  // Define navigation items with permission requirements
  const allNavItems = [
    { 
      path: '/dashboard', 
      icon: LayoutDashboard, 
      label: 'Dashboard',
      permissions: [PERMISSIONS.DASHBOARD_VIEW]
    },
    { 
      path: '/quick-actions', 
      icon: Rocket, 
      label: 'Quick Actions',
      permissions: [PERMISSIONS.TICKET_CREATE]
    },
    { 
      path: '/chat', 
      icon: MessageSquare, 
      label: 'AI Support Chat',
      permissions: [PERMISSIONS.TICKET_CREATE, PERMISSIONS.TROUBLESHOOT_RUN]
    },
    { 
      path: '/tickets', 
      icon: FileText, 
      label: 'Tickets',
      permissions: [PERMISSIONS.TICKET_VIEW_OWN, PERMISSIONS.TICKET_VIEW_TEAM, PERMISSIONS.TICKET_VIEW_ALL]
    },
    { 
      path: '/monitoring', 
      icon: Activity, 
      label: 'System Monitoring',
      permissions: [PERMISSIONS.SYSTEM_MONITOR]
    },
    { 
      path: '/reports', 
      icon: BarChart3, 
      label: 'Reports & Analytics',
      permissions: [PERMISSIONS.REPORTS_VIEW]
    },
    { 
      path: '/automation', 
      icon: Zap, 
      label: 'Automation Rules',
      permissions: [PERMISSIONS.SYSTEM_ADMIN],
      adminOnly: true
    },
    { 
      path: '/error-codes', 
      icon: AlertCircle, 
      label: 'Error Codes',
      permissions: [PERMISSIONS.KB_VIEW]
    },
    { 
      path: '/knowledge-base', 
      icon: Database, 
      label: 'Knowledge Base',
      permissions: [PERMISSIONS.KB_VIEW]
    },
    { 
      path: '/users', 
      icon: Users, 
      label: 'User Management',
      permissions: [PERMISSIONS.USER_VIEW],
      adminOnly: true
    },
    { 
      path: '/audit-logs', 
      icon: FileCheck, 
      label: 'Audit Logs',
      permissions: [PERMISSIONS.USER_VIEW, PERMISSIONS.SYSTEM_ADMIN],
      adminOnly: true
    },
    { 
      path: '/settings', 
      icon: Settings, 
      label: 'Settings',
      permissions: [] // Available to all
    }
  ];

  // Filter navigation items based on user permissions
  const navItems = useMemo(() => {
    return allNavItems.filter(item => {
      // If no permissions required, show to everyone
      if (!item.permissions || item.permissions.length === 0) return true;
      
      // Check if user has any of the required permissions
      return hasAnyPermission(item.permissions);
    });
  }, [hasAnyPermission])

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <Bot size={32} strokeWidth={2} />
          <div className="logo-text">
            <h2>IT Support Systems</h2>
            <span className="tagline">IT Support System</span>
          </div>
        </div>
      </div>

      <div className="sidebar-user">
        <div className="user-avatar">
          <User size={20} />
        </div>
        <div className="user-info">
          <span className="user-name">{user?.name || 'Guest'}</span>
          <span className="user-tier" style={{ color: getRoleInfo().color }}>
            <Shield size={12} />
            {getRoleInfo().label}
          </span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''} ${item.adminOnly ? 'admin-only' : ''}`}
            title={item.adminOnly ? 'Admin Only' : item.label}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
            {item.adminOnly && <Shield size={14} className="admin-badge" />}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <ThemeToggle />
        <button onClick={onLogout} className="logout-btn">
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
