/**
 * User Management Service
 * Handles user CRUD operations, role management, and permissions
 */
import { httpClient } from './httpClient';

const API_BASE = '/admin';

/**
 * Get all users with optional filtering
 */
export const getUsers = async (params = {}) => {
  const { skip = 0, limit = 100, role = null, is_active = null } = params;
  
  const queryParams = new URLSearchParams({ skip, limit });
  if (role) queryParams.append('role', role);
  if (is_active !== null) queryParams.append('is_active', is_active);
  
  const response = await httpClient.get(`${API_BASE}/users?${queryParams}`);
  return response;
};

/**
 * Get a specific user by ID
 */
export const getUserById = async (userId) => {
  const response = await httpClient.get(`${API_BASE}/users/${userId}`);
  return response;
};

/**
 * Update user role
 */
export const updateUserRole = async (userId, role) => {
  const response = await httpClient.put(`${API_BASE}/users/${userId}/role`, { role });
  return response;
};

/**
 * Update user status (activate/deactivate)
 */
export const updateUserStatus = async (userId, isActive) => {
  const response = await httpClient.put(`${API_BASE}/users/${userId}/status`, { 
    is_active: isActive 
  });
  return response;
};

/**
 * Get all available roles and their permissions
 */
export const getRoles = async () => {
  const response = await httpClient.get(`${API_BASE}/roles`);
  return response;
};

/**
 * Get users who can be assigned to tickets
 * Returns active users with admin and IT support roles
 */
export const getAssignableUsers = async () => {
  const response = await httpClient.get(`${API_BASE}/users/assignable`);
  return response;
};

/**
 * Get available managers for a user
 * Returns users who can be assigned as managers
 */
export const getAvailableManagers = async () => {
  const response = await httpClient.get(`${API_BASE}/users/available-managers`);
  return response;
};

/**
 * Assign a manager to a user
 */
export const assignManager = async (userId, managerId) => {
  const response = await httpClient.put(`${API_BASE}/users/${userId}/manager`, { 
    manager_id: managerId 
  });
  return response;
};

/**
 * Create a new user
 */
export const createUser = async (userData) => {
  const response = await httpClient.post(`${API_BASE}/users`, userData);
  return response;
};

/**
 * Update user details (email, name, password, role, department)
 */
export const updateUser = async (userId, userData) => {
  const response = await httpClient.put(`${API_BASE}/users/${userId}`, userData);
  return response;
};

/**
 * Delete a user
 */
export const deleteUser = async (userId) => {
  const response = await httpClient.delete(`${API_BASE}/users/${userId}`);
  return response;
};

export default {
  getUsers,
  getUserById,
  updateUserRole,
  updateUserStatus,
  getRoles,
  getAssignableUsers,
  getAvailableManagers,
  assignManager,
  createUser,
  updateUser,
  deleteUser
};
