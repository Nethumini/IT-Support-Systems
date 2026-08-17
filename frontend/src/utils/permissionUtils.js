/**
 * Permission utility functions
 * Centralized permission constants and helper functions
 */

// Permission constants - must match backend Permission enum
export const PERMISSIONS = {
  // Ticket permissions
  TICKET_VIEW_OWN: 'ticket:view:own',
  TICKET_VIEW_TEAM: 'ticket:view:team',
  TICKET_VIEW_ALL: 'ticket:view:all',
  TICKET_CREATE: 'ticket:create',
  TICKET_UPDATE_OWN: 'ticket:update:own',
  TICKET_UPDATE_ANY: 'ticket:update:any',
  TICKET_DELETE_OWN: 'ticket:delete:own',
  TICKET_DELETE_ANY: 'ticket:delete:any',
  TICKET_ASSIGN: 'ticket:assign',
  TICKET_ESCALATE: 'ticket:escalate',

  // Troubleshooting permissions
  TROUBLESHOOT_RUN: 'troubleshoot:run',
  TROUBLESHOOT_AUTO_RESOLVE: 'troubleshoot:auto_resolve',
  TROUBLESHOOT_VIEW_LOGS: 'troubleshoot:view_logs',

  // System permissions
  SYSTEM_MONITOR: 'system:monitor',
  SYSTEM_DIAGNOSTICS: 'system:diagnostics',
  SYSTEM_ADMIN: 'system:admin',

  // User management permissions
  USER_VIEW: 'user:view',
  USER_MANAGE: 'user:manage',
  USER_MANAGE_ROLES: 'user:manage_roles',

  // Dashboard & Reports
  DASHBOARD_VIEW: 'dashboard:view',
  REPORTS_VIEW: 'reports:view',
  REPORTS_EXPORT: 'reports:export',

  // Knowledge Base
  KB_VIEW: 'kb:view',
  KB_EDIT: 'kb:edit'
};

// Role constants
export const ROLES = {
  STAFF: 'staff',
  CONTRACTOR: 'contractor',
  MANAGER: 'manager',
  SUPPORT_L1: 'support_l1',
  SUPPORT_L2: 'support_l2',
  SUPPORT_L3: 'support_l3',
  IT_ADMIN: 'it_admin',
  SYSTEM_ADMIN: 'system_admin'
};

// Navigation items with required permissions
export const NAVIGATION_CONFIG = {
  dashboard: {
    path: '/dashboard',
    label: 'Dashboard',
    icon: 'LayoutDashboard',
    permissions: [PERMISSIONS.DASHBOARD_VIEW]
  },
  tickets: {
    path: '/tickets',
    label: 'Tickets',
    icon: 'Ticket',
    permissions: [PERMISSIONS.TICKET_VIEW_OWN, PERMISSIONS.TICKET_VIEW_TEAM, PERMISSIONS.TICKET_VIEW_ALL]
  },
  systemMonitoring: {
    path: '/system-monitoring',
    label: 'System Monitoring',
    icon: 'Activity',
    permissions: [PERMISSIONS.SYSTEM_MONITOR]
  },
  userManagement: {
    path: '/user-management',
    label: 'User Management',
    icon: 'Users',
    permissions: [PERMISSIONS.USER_VIEW]
  },
  reports: {
    path: '/reports',
    label: 'Reports',
    icon: 'BarChart3',
    permissions: [PERMISSIONS.REPORTS_VIEW]
  },
  knowledgeBase: {
    path: '/knowledge-base',
    label: 'Knowledge Base',
    icon: 'BookOpen',
    permissions: [PERMISSIONS.KB_VIEW]
  },
  quickActions: {
    path: '/quick-actions',
    label: 'Quick Actions',
    icon: 'Zap',
    permissions: [PERMISSIONS.TICKET_CREATE]
  },
  automation: {
    path: '/automation',
    label: 'Automation',
    icon: 'Bot',
    permissions: [PERMISSIONS.SYSTEM_ADMIN, PERMISSIONS.IT_ADMIN]
  },
  errorCodes: {
    path: '/error-codes',
    label: 'Error Codes',
    icon: 'AlertTriangle',
    permissions: [PERMISSIONS.KB_VIEW]
  },
  auditLogs: {
    path: '/audit-logs',
    label: 'Audit Logs',
    icon: 'FileText',
    permissions: [PERMISSIONS.USER_VIEW, PERMISSIONS.SYSTEM_ADMIN]
  },
  settings: {
    path: '/settings',
    label: 'Settings',
    icon: 'Settings',
    permissions: [] // Available to all authenticated users
  }
};

/**
 * Check if user can access a navigation item
 * @param {string[]} userPermissions - User's permissions
 * @param {string} navItem - Navigation item key
 * @returns {boolean}
 */
export const canAccessNavItem = (userPermissions, navItem) => {
  const config = NAVIGATION_CONFIG[navItem];
  if (!config) return false;
  
  // If no permissions required, allow access
  if (!config.permissions || config.permissions.length === 0) return true;
  
  // Check if user has any of the required permissions
  return config.permissions.some(perm => userPermissions.includes(perm));
};

/**
 * Filter navigation items based on user permissions
 * @param {string[]} userPermissions - User's permissions
 * @returns {Object[]} Filtered navigation items
 */
export const getAccessibleNavItems = (userPermissions) => {
  return Object.entries(NAVIGATION_CONFIG)
    .filter(([key]) => canAccessNavItem(userPermissions, key))
    .map(([key, config]) => ({ key, ...config }));
};

/**
 * Get role hierarchy level
 * @param {string} role - User role
 * @returns {number} Hierarchy level (higher = more access)
 */
export const getRoleLevel = (role) => {
  const levels = {
    [ROLES.CONTRACTOR]: 1,
    [ROLES.STAFF]: 2,
    [ROLES.MANAGER]: 3,
    [ROLES.SUPPORT_L1]: 4,
    [ROLES.SUPPORT_L2]: 5,
    [ROLES.SUPPORT_L3]: 6,
    [ROLES.IT_ADMIN]: 7,
    [ROLES.SYSTEM_ADMIN]: 8
  };
  return levels[role] || 0;
};

/**
 * Check if user can manage another user based on role hierarchy
 * @param {string} currentUserRole - Current user's role
 * @param {string} targetUserRole - Target user's role
 * @returns {boolean}
 */
export const canManageUser = (currentUserRole, targetUserRole) => {
  return getRoleLevel(currentUserRole) > getRoleLevel(targetUserRole);
};

/**
 * Get role display information
 * @param {string} role - User role
 * @returns {Object} Role display info
 */
export const getRoleDisplayInfo = (role) => {
  const roleInfo = {
    [ROLES.STAFF]: { 
      label: 'Staff', 
      color: '#6c757d', 
      badge: 'secondary',
      description: 'Standard employee - can create and view own tickets'
    },
    [ROLES.CONTRACTOR]: { 
      label: 'Contractor', 
      color: '#17a2b8', 
      badge: 'info',
      description: 'External contractor - limited access to own tickets only'
    },
    [ROLES.MANAGER]: { 
      label: 'Manager', 
      color: '#ffc107', 
      badge: 'warning',
      description: 'Team manager - can view team tickets and reports'
    },
    [ROLES.SUPPORT_L1]: { 
      label: 'Support L1', 
      color: '#28a745', 
      badge: 'success',
      description: 'Level 1 Support - basic ticket handling and troubleshooting'
    },
    [ROLES.SUPPORT_L2]: { 
      label: 'Support L2', 
      color: '#20c997', 
      badge: 'success',
      description: 'Level 2 Support - advanced diagnostics and system monitoring'
    },
    [ROLES.SUPPORT_L3]: { 
      label: 'Support L3', 
      color: '#17a2b8', 
      badge: 'info',
      description: 'Level 3 Support - senior engineer with full troubleshooting access'
    },
    [ROLES.IT_ADMIN]: { 
      label: 'IT Admin', 
      color: '#fd7e14', 
      badge: 'danger',
      description: 'IT Administrator - full IT operations access'
    },
    [ROLES.SYSTEM_ADMIN]: { 
      label: 'System Admin', 
      color: '#dc3545', 
      badge: 'danger',
      description: 'System Administrator - complete system access'
    }
  };

  return roleInfo[role] || { 
    label: 'Unknown', 
    color: '#6c757d', 
    badge: 'secondary',
    description: 'Unknown role'
  };
};

export default {
  PERMISSIONS,
  ROLES,
  NAVIGATION_CONFIG,
  canAccessNavItem,
  getAccessibleNavItems,
  getRoleLevel,
  canManageUser,
  getRoleDisplayInfo
};
