// API Configuration
export const API_CONFIG = {
  // VITE_API_BASE_URL should include /api/v1 if needed (handled in .env files)
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3
}

// API Endpoints
export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: '/login',
    REGISTER: '/register',
    LOGOUT: '/logout',
    REFRESH: '/refresh'
  },
  
  // Chat endpoints
  CHAT: {
    SEND_MESSAGE: '/chat',
    GET_HISTORY: '/chat/history',
    RESET: '/chat/reset',
    GET_SESSIONS: '/chat/sessions',
    RESUME: '/chat/resume',
    IMAGE: '/chat/image'
  },
  
  // Ticket endpoints
  TICKETS: {
    GET_ALL: '/tickets',
    GET_BY_ID: (id) => `/tickets/${id}`,
    CREATE: '/tickets',
    UPDATE: (id) => `/tickets/${id}`,
    DELETE: (id) => `/tickets/${id}`
  },
  
  // Dashboard endpoints
  DASHBOARD: {
    OVERVIEW: '/dashboard/overview',
    STATS: '/dashboard/overview',
    TRENDS: '/dashboard/trends',
    RECENT_ISSUES: '/dashboard/recent-tickets',
    CATEGORY_BREAKDOWN: '/dashboard/category-breakdown',
    PRIORITY_DISTRIBUTION: '/dashboard/priority-distribution',
    RESPONSE_TIME: '/dashboard/response-time'
  },
  
  // Monitoring endpoints
  MONITORING: {
    CHECK_HEALTH: '/monitoring/check-systems',
    SYSTEM_METRICS: '/monitoring/metrics',
    STATS: '/monitoring/stats',
    SERVICES: '/monitoring/system-status',
    LOGS: '/monitoring/sample-logs',
    METRICS: '/monitoring/metrics',
    SIMULATE_CRASH: '/monitoring/simulate-crash'
  },
  
  // Reports endpoints (not yet implemented in backend)
  REPORTS: {
    GENERATE: '/reports',
    EXPORT: '/reports/export'
  },
  
  // Status endpoint
  STATUS: '/status',
  
  // Actions endpoints
  ACTIONS: {
    AVAILABLE: '/available',
    GET_BY_ID: (id) => `/action/${id}`,
    SUGGEST: '/suggest',
    PROACTIVE: '/proactive',
    REQUEST: '/request',
    APPROVE: '/approve',
    EXECUTE: (id) => `/execute/${id}`,
    PENDING: '/pending',
    HISTORY: '/history',
    DIAGNOSE_PROCESSES: '/diagnose/processes',
    DIAGNOSE_SYSTEM: '/diagnose/system',
    DIAGNOSE_NETWORK: '/diagnose/network',
    DIAGNOSE_DISK: '/diagnose/disk',
    ANALYZE: '/analyze',
    QUICK_FIX: (issueType) => `/quick-fix/${issueType}`
  },
  
  // Static data endpoints
  STATIC_DATA: {
    QUICK_ACTIONS: '/quick-actions',
    ERROR_CODES: '/error-codes',
    ERROR_CODES_BY_PLATFORM: (platform) => `/error-codes/${platform}`
  }
}

// Route Paths
export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  QUICK_ACTIONS: '/quick-actions',
  CHAT: '/chat',
  TICKETS: '/tickets',
  MONITORING: '/monitoring',
  REPORTS: '/reports',
  AUTOMATION: '/automation',
  ERROR_CODES: '/error-codes',
  KNOWLEDGE_BASE: '/knowledge-base',
  USER_MANAGEMENT: '/users',
  AUDIT_LOGS: '/audit-logs',
  SETTINGS: '/settings',
  ROOT: '/'
}

// Theme Colors (used as fallback)
export const COLORS = {
  // Primary colors
  primary: {
    50: '#f0fdfa',
    100: '#ccfbf1',
    200: '#99f6e4',
    300: '#5eead4',
    400: '#2dd4bf',
    500: '#14b8a6',
    600: '#0d9488',
    700: '#0f766e',
    800: '#115e59',
    900: '#134e4a'
  },
  
  // Status colors
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',
  
  // Neutral colors (dark theme)
  dark: {
    bg: '#0f0f1a',
    bgSecondary: '#1a1a2e',
    bgTertiary: '#16213e',
    border: 'rgba(20, 184, 166, 0.2)',
    text: '#e5e7eb',
    textSecondary: '#9ca3af',
    textMuted: '#6b7280'
  },
  
  // Light colors (light theme)
  light: {
    bg: '#ffffff',
    bgSecondary: '#f9fafb',
    bgTertiary: '#f3f4f6',
    border: 'rgba(107, 114, 128, 0.2)',
    text: '#111827',
    textSecondary: '#4b5563',
    textMuted: '#9ca3af'
  }
}

// Application Settings
export const APP_SETTINGS = {
  APP_NAME: 'IT Support Systems',
  APP_TAGLINE: 'AI-powered IT Support Assistant',
  VERSION: '1.0.0',
  DEFAULT_THEME: 'light',
  
  // Pagination
  ITEMS_PER_PAGE: 20,
  
  // Chat settings
  MAX_MESSAGE_LENGTH: 2000,
  TYPING_INDICATOR_DELAY: 1000,
  
  // Notification settings
  NOTIFICATION_DURATION: 5000,
  
  // File upload
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_FILE_TYPES: ['image/png', 'image/jpeg', 'application/pdf']
}

// Ticket Status
export const TICKET_STATUS = {
  OPEN: 'open',
  IN_PROGRESS: 'in_progress',
  ASSIGNED_TO_HUMAN: 'assigned_to_human',
  RESOLVED: 'resolved',
  CLOSED: 'closed'
}

// Ticket Status Labels
export const TICKET_STATUS_LABELS = {
  open: 'Open',
  in_progress: 'In Progress',
  assigned_to_human: 'Assigned to Human',
  resolved: 'Resolved',
  closed: 'Closed'
}

// Ticket Priority
export const TICKET_PRIORITY = {
  LOW: 4,
  MEDIUM: 3,
  HIGH: 2,
  CRITICAL: 1
}

// Ticket Priority to API mapping
export const TICKET_PRIORITY_TO_API = {
  1: 'critical',
  2: 'high',
  3: 'medium',
  4: 'low'
}

// API Priority to number mapping
export const API_PRIORITY_TO_NUMBER = {
  'critical': 1,
  'high': 2,
  'medium': 3,
  'low': 4
}

// Ticket Priority Labels
export const TICKET_PRIORITY_LABELS = {
  1: 'Critical',
  2: 'High',
  3: 'Medium',
  4: 'Low'
}

// Ticket Category
export const TICKET_CATEGORY = {
  HARDWARE: 'hardware',
  SOFTWARE: 'software',
  NETWORK: 'network',
  ACCOUNT: 'account',
  PERFORMANCE: 'performance',
  SECURITY: 'security',
  OTHER: 'other'
}

// Ticket Category Labels
export const TICKET_CATEGORY_LABELS = {
  hardware: 'Hardware',
  software: 'Software',
  network: 'Network',
  account: 'Account',
  performance: 'Performance',
  security: 'Security',
  other: 'Other'
}

// Specialization options for support agents
export const AGENT_SPECIALIZATIONS = [
  { value: 'hardware', label: 'Hardware', description: 'Physical devices, BSOD, repairs' },
  { value: 'software', label: 'Software', description: 'Applications, performance, crashes' },
  { value: 'network', label: 'Network', description: 'VPN, connectivity, routing' },
  { value: 'account', label: 'Account', description: 'Login, permissions, access' },
  { value: 'security', label: 'Security', description: 'Authentication, malware, policies' },
  { value: 'critical', label: 'Critical Issues', description: 'High-priority escalations' },
  { value: 'vpn', label: 'VPN', description: 'VPN-specific issues' },
  { value: 'performance', label: 'Performance', description: 'Optimization, speed issues' }
]

// User Roles
export const USER_ROLES = {
  ADMIN: 'admin',
  TECHNICIAN: 'technician',
  USER: 'user',
  GUEST: 'guest'
}

// Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'token',
  USER_DATA: 'user',
  THEME: 'theme',
  LANGUAGE: 'language'
}

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  AUTH_ERROR: 'Authentication failed. Please login again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  NOT_FOUND: 'Resource not found.',
  VALIDATION_ERROR: 'Please check your input and try again.'
}

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Successfully logged in!',
  LOGOUT_SUCCESS: 'Successfully logged out!',
  TICKET_CREATED: 'Ticket created successfully!',
  TICKET_UPDATED: 'Ticket updated successfully!',
  SETTINGS_SAVED: 'Settings saved successfully!'
}
