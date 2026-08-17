/**
 * PermissionGate Component
 * Conditionally renders children based on user permissions
 */
import PropTypes from 'prop-types';
import { usePermissions } from '../hooks/usePermissions';

/**
 * Gate component that shows/hides content based on permissions
 * @param {Object} props
 * @param {string|string[]} props.permissions - Required permission(s)
 * @param {string|string[]} props.roles - Required role(s)
 * @param {boolean} props.requireAll - If true, requires all permissions (default: false)
 * @param {React.ReactNode} props.children - Content to render if authorized
 * @param {React.ReactNode} props.fallback - Content to render if not authorized
 */
const PermissionGate = ({ 
  permissions, 
  roles, 
  requireAll = false, 
  children, 
  fallback = null 
}) => {
  const { hasPermission, hasAnyPermission, hasAllPermissions, hasRole } = usePermissions();

  // Check role-based access
  if (roles) {
    if (!hasRole(roles)) {
      return fallback;
    }
  }

  // Check permission-based access
  if (permissions) {
    const permArray = Array.isArray(permissions) ? permissions : [permissions];
    
    if (requireAll) {
      if (!hasAllPermissions(permArray)) {
        return fallback;
      }
    } else {
      if (!hasAnyPermission(permArray)) {
        return fallback;
      }
    }
  }

  return <>{children}</>;
};

PermissionGate.propTypes = {
  permissions: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string)
  ]),
  roles: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string)
  ]),
  requireAll: PropTypes.bool,
  children: PropTypes.node.isRequired,
  fallback: PropTypes.node
};

export default PermissionGate;
