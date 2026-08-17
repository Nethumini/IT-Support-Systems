import { Navigate } from 'react-router-dom'
import Dashboard from '../components/Dashboard'
import TicketList from '../components/TicketList'
import SystemMonitoring from '../components/SystemMonitoring'
import Reports from '../components/Reports'
import Settings from '../components/Settings'
import AutomationPage from '../components/AutomationPage'
import ErrorCodesPage from '../components/ErrorCodesPage'
import KnowledgeBasePage from '../components/KnowledgeBasePage'
import UserManagement from '../components/UserManagement'
import AuditLogs from '../components/AuditLogs'
import RoleHierarchy from '../components/RoleHierarchy'
import Login from '../components/Login'
import Register from '../components/Register'
import { ROUTES } from './constants'

// Chat component will be passed as prop to avoid circular dependency
export const getAuthenticatedRoutes = (ChatPage) => [
  {
    path: ROUTES.DASHBOARD,
    element: Dashboard,
    requiresAuth: true
  },
  {
    path: ROUTES.CHAT,
    element: ChatPage,
    requiresAuth: true
  },
  {
    path: ROUTES.TICKETS,
    element: TicketList,
    requiresAuth: true
  },
  {
    path: ROUTES.MONITORING,
    element: SystemMonitoring,
    requiresAuth: true
  },
  {
    path: ROUTES.REPORTS,
    element: Reports,
    requiresAuth: true
  },
  {
    path: ROUTES.AUTOMATION,
    element: AutomationPage,
    requiresAuth: true
  },
  {
    path: ROUTES.ERROR_CODES,
    element: ErrorCodesPage,
    requiresAuth: true
  },
  {
    path: ROUTES.KNOWLEDGE_BASE,
    element: KnowledgeBasePage,
    requiresAuth: true
  },
  {
    path: ROUTES.USER_MANAGEMENT,
    element: UserManagement,
    requiresAuth: true
  },
  {
    path: ROUTES.AUDIT_LOGS,
    element: AuditLogs,
    requiresAuth: true
  },
  {
    path: '/role-hierarchy',
    element: RoleHierarchy,
    requiresAuth: true
  },
  {
    path: ROUTES.SETTINGS,
    element: Settings,
    requiresAuth: true
  },
  {
    path: ROUTES.ROOT,
    element: () => <Navigate to={ROUTES.DASHBOARD} replace />,
    requiresAuth: true
  }
]

export const publicRoutes = [
  {
    path: ROUTES.LOGIN,
    element: Login,
    requiresAuth: false
  },
  {
    path: ROUTES.REGISTER,
    element: Register,
    requiresAuth: false
  },
  {
    path: '*',
    element: () => <Navigate to={ROUTES.LOGIN} replace />,
    requiresAuth: false
  }
]
