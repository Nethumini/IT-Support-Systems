/**
 * Custom hook for managing user permissions
 * Provides utilities to check user permissions and role-based access
 */
import { useState, useEffect, useMemo } from 'react';

/**
 * Hook to access and check user permissions
 * @returns {Object} Permission utilities
 */
export const usePermissions = () => {
  const [user, setUser] = useState(null);
  const [permissions, setPermissions] = useState([]);
  const [role, setRole] = useState(null);

  useEffect(() => {
    // Load user from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        setPermissions(parsedUser.permissions || []);
        setRole(parsedUser.role);
      } catch (error) {
        console.error('Error parsing user data:', error);
      }
    }
  }, []);

  /**
   * Check if user has a specific permission
   * @param {string} permission - Permission to check
   * @returns {boolean}
   */
  const hasPermission = (permission) => {
    // System Admin has all permissions
    if (role === 'system_admin') return true;
    if (!permissions) return false;
    return permissions.includes(permission);
  };

  /**
   * Check if user has any of the specified permissions
   * @param {string[]} requiredPermissions - Array of permissions
   * @returns {boolean}
   */
  const hasAnyPermission = (requiredPermissions) => {
    // System Admin has all permissions
    if (role === 'system_admin') return true;
    if (!permissions || !Array.isArray(requiredPermissions)) return false;
    return requiredPermissions.some(perm => permissions.includes(perm));
  };

  /**
   * Check if user has all of the specified permissions
   * @param {string[]} requiredPermissions - Array of permissions
   * @returns {boolean}
   */
  const hasAllPermissions = (requiredPermissions) => {
    // System Admin has all permissions
    if (role === 'system_admin') return true;
    if (!permissions || !Array.isArray(requiredPermissions)) return false;
    return requiredPermissions.every(perm => permissions.includes(perm));
  };

  /**
   * Check if user has a specific role
   * @param {string|string[]} roles - Role(s) to check
   * @returns {boolean}
   */
  const hasRole = (roles) => {
    if (!role) return false;
    if (Array.isArray(roles)) {
      return roles.includes(role);
    }
    return role === roles;
  };

  /**
   * Check if user is admin (IT Admin or System Admin)
   * @returns {boolean}
   */
  const isAdmin = useMemo(() => {
    return role === 'it_admin' || role === 'system_admin';
  }, [role]);

  /**
   * Check if user is support staff
   * @returns {boolean}
   */
  const isSupport = useMemo(() => {
    return role === 'support_l1' || role === 'support_l2' || role === 'support_l3';
  }, [role]);

  /**
   * Check if user is manager or above
   * @returns {boolean}
   */
  const isManagerOrAbove = useMemo(() => {
    return role === 'manager' || isAdmin || isSupport;
  }, [role, isAdmin, isSupport]);

  /**
   * Get role display information
   * @returns {Object}
   */
  const getRoleInfo = () => {
    const roleMap = {
      'staff': { label: 'Staff', color: '#6c757d', level: 1 },
      'contractor': { label: 'Contractor', color: '#17a2b8', level: 1 },
      'manager': { label: 'Manager', color: '#ffc107', level: 2 },
      'support_l1': { label: 'Support L1', color: '#28a745', level: 3 },
      'support_l2': { label: 'Support L2', color: '#20c997', level: 4 },
      'support_l3': { label: 'Support L3', color: '#17a2b8', level: 5 },
      'it_admin': { label: 'IT Admin', color: '#fd7e14', level: 6 },
      'system_admin': { label: 'System Admin', color: '#dc3545', level: 7 }
    };
    return roleMap[role] || { label: 'Unknown', color: '#6c757d', level: 0 };
  };

  return {
    user,
    permissions,
    role,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    isAdmin,
    isSupport,
    isManagerOrAbove,
    getRoleInfo
  };
};

export default usePermissions;
