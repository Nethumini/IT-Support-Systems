/**
 * Audit Logs Service
 * Handles audit log retrieval and filtering
 */
import { httpClient } from './httpClient';

const API_BASE = '/admin';

/**
 * Get audit logs with optional filtering (Admin only)
 */
export const getAuditLogs = async (params = {}) => {
  const { 
    skip = 0, 
    limit = 100, 
    user_email = null, 
    action = null,
    resource_type = null,
    success = null
  } = params;
  
  const queryParams = new URLSearchParams({ skip, limit });
  if (user_email) queryParams.append('user_email', user_email);
  if (action) queryParams.append('action', action);
  if (resource_type) queryParams.append('resource_type', resource_type);
  if (success) queryParams.append('success', success);
  
  const response = await httpClient.get(`${API_BASE}/audit-logs?${queryParams}`);
  return response;
};

/**
 * Get current user's audit logs
 */
export const getMyAuditLogs = async (limit = 50) => {
  const response = await httpClient.get(`${API_BASE}/audit-logs/me?limit=${limit}`);
  return response;
};

/**
 * Get failed access attempts (Admin only)
 */
export const getFailedAccessAttempts = async (hours = 24) => {
  const response = await httpClient.get(`${API_BASE}/audit-logs/failed-access?hours=${hours}`);
  return response;
};

export default {
  getAuditLogs,
  getMyAuditLogs,
  getFailedAccessAttempts
};
