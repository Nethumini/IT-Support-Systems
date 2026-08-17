import { useState, useEffect } from 'react';
import { 
  Users, 
  Shield, 
  UserCheck, 
  UserX, 
  Edit2, 
  Trash2,
  Search,
  Filter,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Lock,
  Plus
} from 'lucide-react';
import userService from '../services/userService';
import { usePermissions } from '../hooks/usePermissions';
import PermissionGate from './PermissionGate';
import { PERMISSIONS, getRoleDisplayInfo, canManageUser } from '../utils/permissionUtils';
import { AGENT_SPECIALIZATIONS } from '../config/constants';
import '../styles/components/UserManagement.css';

const ROLES = [
  { value: 'staff', label: 'Staff', color: '#6c757d' },
  { value: 'contractor', label: 'Contractor', color: '#17a2b8' },
  { value: 'manager', label: 'Manager', color: '#ffc107' },
  { value: 'support_l1', label: 'Support L1', color: '#28a745' },
  { value: 'support_l2', label: 'Support L2', color: '#20c997' },
  { value: 'support_l3', label: 'Support L3', color: '#17a2b8' },
  { value: 'it_admin', label: 'IT Admin', color: '#fd7e14' },
  { value: 'system_admin', label: 'System Admin', color: '#dc3545' }
];

function UserManagement() {
  const { hasPermission, role: currentUserRole, user: currentUser } = usePermissions();
  
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [editingUser, setEditingUser] = useState(null);
  const [selectedRole, setSelectedRole] = useState('');
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Create user state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newUserData, setNewUserData] = useState({
    email: '',
    name: '',
    password: '',
    role: 'staff',
    specialization: [] // For support agents
  });
  const [creatingUser, setCreatingUser] = useState(false);
  
  // Manager assignment state
  const [showManagerModal, setShowManagerModal] = useState(false);
  const [managerUser, setManagerUser] = useState(null);
  const [availableManagers, setAvailableManagers] = useState([]);
  const [selectedManager, setSelectedManager] = useState(null);
  const [loadingManagers, setLoadingManagers] = useState(false);
  
  // Edit user state
  const [showEditModal, setShowEditModal] = useState(false);
  const [editUserData, setEditUserData] = useState({
    email: '',
    name: '',
    password: '',
    role: 'staff',
    specialization: [] // For support agents
  });
  const [editingUserId, setEditingUserId] = useState(null);
  const [editingUserLoading, setEditingUserLoading] = useState(false);
  
  // Delete confirmation state
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);
  const [deletingUser, setDeletingUser] = useState(false);
  
  // Permission checks
  const canViewUsers = hasPermission(PERMISSIONS.USER_VIEW);
  const canManageUsers = hasPermission(PERMISSIONS.USER_MANAGE);
  const canManageRoles = hasPermission(PERMISSIONS.USER_MANAGE_ROLES);

  useEffect(() => {
    fetchUsers();
    fetchRoles();
    loadAvailableManagers();
  }, [filterRole, filterStatus]);

  const loadAvailableManagers = async () => {
    try {
      const managers = await userService.getAvailableManagers();
      setAvailableManagers(managers);
    } catch (err) {
      console.error('Error loading available managers:', err);
    }
  };

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {};
      if (filterRole) params.role = filterRole;
      if (filterStatus !== '') params.is_active = filterStatus === 'active';
      
      const data = await userService.getUsers(params);
      setUsers(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const data = await userService.getRoles();
      setRoles(data);
    } catch (err) {
      console.error('Error fetching roles:', err);
    }
  };

  const handleUpdateRole = async () => {
    if (!editingUser || !selectedRole) return;

    try {
      await userService.updateUserRole(editingUser.id, selectedRole);
      setSuccessMessage(`Successfully updated role for ${editingUser.email}`);
      setShowRoleModal(false);
      setEditingUser(null);
      setSelectedRole('');
      fetchUsers();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update role');
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    if (!newUserData.email || !newUserData.name || !newUserData.password) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setCreatingUser(true);
      await userService.createUser(newUserData);
      setSuccessMessage(`Successfully created user ${newUserData.email}`);
      setShowCreateModal(false);
      setNewUserData({
        email: '',
        name: '',
        password: '',
        role: 'staff',
        specialization: []
      });
      fetchUsers();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setCreatingUser(false);
    }
  };

  const handleToggleStatus = async (user) => {
    try {
      await userService.updateUserStatus(user.id, !user.is_active);
      setSuccessMessage(`Successfully ${user.is_active ? 'deactivated' : 'activated'} ${user.email}`);
      fetchUsers();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update user status');
    }
  };

  const openEditModal = (user) => {
    if (!canPerformAction(user)) {
      setError('You do not have permission to edit this user');
      return;
    }
    setEditingUserId(user.id);
    setEditUserData({
      email: user.email,
      name: user.name,
      password: '', // Password optional for edits
      role: user.role,
      specialization: user.specialization || []
    });
    setShowEditModal(true);
  };

  const handleUpdateUser = async (e) => {
    e.preventDefault();
    if (!editUserData.email || !editUserData.name) {
      setError('Email and name are required');
      return;
    }

    try {
      setEditingUserLoading(true);
      await userService.updateUser(editingUserId, editUserData);
      setSuccessMessage(`Successfully updated user ${editUserData.email}`);
      setShowEditModal(false);
      setEditingUserId(null);
      setEditUserData({ email: '', name: '', password: '', role: 'staff', specialization: [] });
      fetchUsers();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update user');
    } finally {
      setEditingUserLoading(false);
    }
  };

  const openDeleteConfirm = (user) => {
    if (!canPerformAction(user)) {
      setError('You do not have permission to delete this user');
      return;
    }
    setUserToDelete(user);
    setShowDeleteConfirm(true);
  };

  const handleDeleteUser = async () => {
    if (!userToDelete) return;

    try {
      setDeletingUser(true);
      await userService.deleteUser(userToDelete.id);
      setSuccessMessage(`Successfully deleted user ${userToDelete.email}`);
      setShowDeleteConfirm(false);
      setUserToDelete(null);
      fetchUsers();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete user');
    } finally {
      setDeletingUser(false);
    }
  };

  const openRoleModal = (user) => {
    // Check if current user can manage this user based on hierarchy
    if (!canManageUser(currentUserRole, user.role)) {
      setError('You do not have permission to manage users with this role');
      return;
    }
    setEditingUser(user);
    setSelectedRole(user.role);
    setShowRoleModal(true);
  };

  const openManagerModal = (user) => {
    if (!canManageUsers) {
      setError('You do not have permission to manage users');
      return;
    }
    setManagerUser(user);
    setSelectedManager(user.manager_id || null);
    setShowManagerModal(true);
  };

  const handleAssignManager = async () => {
    if (!managerUser) return;

    try {
      await userService.assignManager(managerUser.id, selectedManager);
      setSuccessMessage(`Successfully assigned manager to ${managerUser.email}`);
      setShowManagerModal(false);
      setManagerUser(null);
      setSelectedManager(null);
      fetchUsers();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to assign manager');
    }
  };
  
  // Check if current user can perform actions on a specific user
  const canPerformAction = (targetUser) => {
    // Can't modify yourself
    if (currentUser?.id === targetUser.id) return false;
    // Must have permission and higher role level
    return canManageUsers && canManageUser(currentUserRole, targetUser.role);
  };

  const filteredUsers = (users || []).filter(user => {
    const matchesSearch = 
      user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.full_name?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const getRoleLabel = (roleValue) => {
    const role = ROLES.find(r => r.value === roleValue);
    return role ? role.label : roleValue;
  };

  const getRoleColor = (roleValue) => {
    const role = ROLES.find(r => r.value === roleValue);
    return role ? role.color : '#6c757d';
  };

  // Redirect if no view permission
  if (!canViewUsers) {
    return (
      <div className="user-management">
        <div className="access-denied">
          <Lock size={48} />
          <h2>Access Denied</h2>
          <p>You do not have permission to view user management.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="user-management jira-style">
      <div className="jira-header">
        <div className="jira-header-left">
          <h1>User Management</h1>
          <div className="header-stats">
            <span className="stat-item">
              {filteredUsers.length} users
            </span>
          </div>
        </div>
        <div className="jira-header-right">
          <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
            <Plus size={18} />
            Create User
          </button>
          <button className="btn-refresh" onClick={fetchUsers} disabled={loading}>
            <RefreshCw size={18} className={loading ? 'spinning' : ''} />
            Refresh
          </button>
        </div>
      </div>

      <div className="jira-toolbar">
        <div className="toolbar-left">
          <div className="search-box">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search by email or name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="filter-group">
            <Filter size={18} />
            <select
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value)}
            >
              <option value="">All Roles</option>
              {ROLES.map(role => (
                <option key={role.value} value={role.value}>{role.label}</option>
              ))}
            </select>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          <CheckCircle size={18} />
          {successMessage}
        </div>
      )}

      <div className="users-table-container">
        {loading ? (
          <div className="loading-state">
            <RefreshCw className="spinning" size={32} />
            <p>Loading users...</p>
          </div>
        ) : (
          <table className="users-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Role</th>
                <th>Manager</th>
                <th>Status</th>
                <th>Permissions</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map(user => (
                <tr key={user.id}>
                  <td>
                    <div className="user-info">
                      <span>{user.name || 'N/A'}</span>
                    </div>
                  </td>
                  <td>{user.email}</td>
                  <td>
                    <span 
                      className="role-badge"
                      style={{ backgroundColor: getRoleColor(user.role) }}
                    >
                      <Shield size={14} />
                      {getRoleLabel(user.role)}
                    </span>
                  </td>
                  <td>
                    <span className="manager-info">
                      {user.manager_id ? (
                        <>
                          <Shield size={12} />
                          {availableManagers.find(m => m.id == user.manager_id)?.name || `Manager ${user.manager_id}`}
                        </>
                      ) : (
                        <span className="no-manager">No Manager</span>
                      )}
                    </span>
                  </td>
                  <td>
                    <div className="status-column">
                      <PermissionGate permissions={[PERMISSIONS.USER_MANAGE]}>
                        <button
                          className={`toggle-btn ${user.is_active ? 'active' : 'inactive'}`}
                          onClick={() => handleToggleStatus(user)}
                          title={user.is_active ? 'Deactivate User' : 'Activate User'}
                        >
                          {user.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </PermissionGate>
                    </div>
                  </td>
                  <td>
                    <div className="permissions-list">
                      {user.permissions && user.permissions.length > 0 ? (
                        <span className="permission-count">
                          {user.permissions.length} permissions
                        </span>
                      ) : (
                        <span className="no-permissions">No permissions</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <div className="action-buttons">
                      {canPerformAction(user) ? (
                        <>
                          <PermissionGate permissions={[PERMISSIONS.USER_MANAGE_ROLES]}>
                            <button
                              className="icon-btn role"
                              onClick={() => openRoleModal(user)}
                              title="Change Role"
                            >
                              <Shield size={16} />
                            </button>
                          </PermissionGate>
                          <PermissionGate permissions={[PERMISSIONS.USER_MANAGE]}>
                            <button
                              className="icon-btn edit"
                              onClick={() => openEditModal(user)}
                              title="Edit User Details"
                            >
                              <Edit2 size={16} />
                            </button>
                          </PermissionGate>
                          <PermissionGate permissions={[PERMISSIONS.USER_MANAGE]}>
                            <button
                              className="icon-btn manager"
                              onClick={() => openManagerModal(user)}
                              title="Assign Manager"
                            >
                              <Users size={16} />
                            </button>
                          </PermissionGate>
                          <PermissionGate permissions={[PERMISSIONS.USER_MANAGE]}>
                            <button
                              className="icon-btn delete"
                              onClick={() => openDeleteConfirm(user)}
                              title="Delete User"
                            >
                              <Trash2 size={16} />
                            </button>
                          </PermissionGate>
                        </>
                      ) : (
                        <span className="no-permission-badge" title="No permission to manage this user">
                          <Lock size={14} />
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {!loading && filteredUsers.length === 0 && (
          <div className="empty-state">
            <Users size={48} />
            <p>No users found</p>
          </div>
        )}
      </div>

      {showRoleModal && (
        <div className="modal-overlay" onClick={() => setShowRoleModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Change User Role</h2>
            <p className="modal-description">
              Update role for <strong>{editingUser?.email}</strong>
            </p>

            <div className="form-group">
              <label>Select New Role</label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="role-select"
              >
                {ROLES.map(role => (
                  <option key={role.value} value={role.value}>
                    {role.label}
                  </option>
                ))}
              </select>
            </div>

            {selectedRole && roles.find(r => r.role === selectedRole) && (
              <div className="role-permissions">
                <h4>Permissions for {getRoleLabel(selectedRole)}</h4>
                <ul>
                  {roles.find(r => r.role === selectedRole)?.permissions.map(perm => (
                    <li key={perm}>
                      <CheckCircle size={14} />
                      {perm.replace(/_/g, ' ')}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => setShowRoleModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn-confirm"
                onClick={handleUpdateRole}
                disabled={!selectedRole || selectedRole === editingUser?.role}
              >
                Update Role
              </button>
            </div>
          </div>
        </div>
      )}

      {showManagerModal && (
        <div className="modal-overlay" onClick={() => setShowManagerModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Assign Manager</h2>
            <p className="modal-description">
              Select a manager for <strong>{managerUser?.email}</strong>
            </p>

            <div className="form-group">
              <label>Select Manager</label>
              <select
                value={selectedManager || ''}
                onChange={(e) => setSelectedManager(e.target.value ? parseInt(e.target.value) : null)}
                className="role-select"
              >
                <option value="">No Manager</option>
                {availableManagers && availableManagers.map(manager => (
                  <option key={manager.id} value={manager.id}>
                    {manager.name} ({getRoleLabel(manager.role)})
                  </option>
                ))}
              </select>
            </div>

            {selectedManager && availableManagers.find(m => m.id === selectedManager) && (
              <div className="selected-manager-info">
                <h4>Selected Manager</h4>
                {(() => {
                  const mgr = availableManagers.find(m => m.id === selectedManager);
                  return (
                    <div>
                      <p><strong>Name:</strong> {mgr.name}</p>
                      <p><strong>Role:</strong> {getRoleLabel(mgr.role)}</p>
                    </div>
                  );
                })()}
              </div>
            )}

            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => setShowManagerModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn-confirm"
                onClick={handleAssignManager}
              >
                Assign Manager
              </button>
            </div>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New User</h2>
            <form onSubmit={handleCreateUser}>
              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  value={newUserData.email}
                  onChange={(e) => setNewUserData({ ...newUserData, email: e.target.value })}
                  placeholder="user@example.com"
                  required
                />
              </div>

              <div className="form-group">
                <label>Full Name *</label>
                <input
                  type="text"
                  value={newUserData.name}
                  onChange={(e) => setNewUserData({ ...newUserData, name: e.target.value })}
                  placeholder="John Doe"
                  required
                />
              </div>

              <div className="form-group">
                <label>Password *</label>
                <input
                  type="password"
                  value={newUserData.password}
                  onChange={(e) => setNewUserData({ ...newUserData, password: e.target.value })}
                  placeholder="••••••••"
                  required
                />
              </div>

              <div className="form-group">
                <label>Role</label>
                <select
                  value={newUserData.role}
                  onChange={(e) => setNewUserData({ ...newUserData, role: e.target.value })}
                  className="role-select"
                >
                  {ROLES.map(role => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </select>
              </div>

              {(newUserData.role === 'support_l1' || newUserData.role === 'support_l2' || newUserData.role === 'support_l3') && (
                <div className="form-group">
                  <label>🎯 Specializations (for smart ticket assignment)</label>
                  <p className="form-hint">Select areas of expertise for this support agent</p>
                  <div className="specialization-checkboxes">
                    {AGENT_SPECIALIZATIONS.map(spec => (
                      <label key={spec.value} className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={newUserData.specialization?.includes(spec.value) || false}
                          onChange={(e) => {
                            const current = newUserData.specialization || [];
                            const updated = e.target.checked
                              ? [...current, spec.value]
                              : current.filter(s => s !== spec.value);
                            setNewUserData({ ...newUserData, specialization: updated });
                          }}
                        />
                        <span className="checkbox-text">
                          <strong>{spec.label}</strong>
                          <small>{spec.description}</small>
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn-cancel"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-confirm"
                  disabled={creatingUser}
                >
                  {creatingUser ? 'Creating...' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showEditModal && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Edit User</h2>
            <form onSubmit={handleUpdateUser}>
              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  value={editUserData.email}
                  onChange={(e) => setEditUserData({ ...editUserData, email: e.target.value })}
                  placeholder="user@example.com"
                  required
                />
              </div>

              <div className="form-group">
                <label>Full Name *</label>
                <input
                  type="text"
                  value={editUserData.name}
                  onChange={(e) => setEditUserData({ ...editUserData, name: e.target.value })}
                  placeholder="John Doe"
                  required
                />
              </div>

              <div className="form-group">
                <label>Password (leave empty to keep current)</label>
                <input
                  type="password"
                  value={editUserData.password}
                  onChange={(e) => setEditUserData({ ...editUserData, password: e.target.value })}
                  placeholder="••••••••"
                />
              </div>

              <div className="form-group">
                <label>Role</label>
                <select
                  value={editUserData.role}
                  onChange={(e) => setEditUserData({ ...editUserData, role: e.target.value })}
                  className="role-select"
                >
                  {ROLES.map(role => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </select>
              </div>

              {(editUserData.role === 'support_l1' || editUserData.role === 'support_l2' || editUserData.role === 'support_l3') && (
                <div className="form-group">
                  <label>🎯 Specializations (for smart ticket assignment)</label>
                  <p className="form-hint">Select areas of expertise for this support agent</p>
                  <div className="specialization-checkboxes">
                    {AGENT_SPECIALIZATIONS.map(spec => (
                      <label key={spec.value} className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={editUserData.specialization?.includes(spec.value) || false}
                          onChange={(e) => {
                            const current = editUserData.specialization || [];
                            const updated = e.target.checked
                              ? [...current, spec.value]
                              : current.filter(s => s !== spec.value);
                            setEditUserData({ ...editUserData, specialization: updated });
                          }}
                        />
                        <span className="checkbox-text">
                          <strong>{spec.label}</strong>
                          <small>{spec.description}</small>
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn-cancel"
                  onClick={() => setShowEditModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-confirm"
                  disabled={editingUserLoading}
                >
                  {editingUserLoading ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showDeleteConfirm && (
        <div className="modal-overlay" onClick={() => setShowDeleteConfirm(false)}>
          <div className="modal-content danger" onClick={(e) => e.stopPropagation()}>
            <h2>Delete User</h2>
            <p className="modal-description">
              Are you sure you want to delete <strong>{userToDelete?.email}</strong>? This action cannot be undone.
            </p>

            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancel
              </button>
              <button
                className="btn-danger"
                onClick={handleDeleteUser}
                disabled={deletingUser}
              >
                {deletingUser ? 'Deleting...' : 'Delete User'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserManagement;
