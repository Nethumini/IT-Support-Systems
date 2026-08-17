/**
 * RoleHierarchy Component
 * Displays the organizational role hierarchy and permissions
 */
import { Shield, Users, ChevronDown, ChevronRight, Lock, Check } from 'lucide-react';
import { useState } from 'react';
import { getRoleDisplayInfo, PERMISSIONS } from '../utils/permissionUtils';
import '../styles/components/RoleHierarchy.css';

const ROLE_STRUCTURE = {
  'system_admin': {
    name: 'System Administrator',
    level: 8,
    reports_to: null,
    manages: ['it_admin', 'support_l3'],
    key_permissions: [
      PERMISSIONS.SYSTEM_ADMIN,
      PERMISSIONS.USER_MANAGE_ROLES,
      PERMISSIONS.USER_MANAGE,
      'All System Permissions'
    ]
  },
  'it_admin': {
    name: 'IT Administrator',
    level: 7,
    reports_to: 'system_admin',
    manages: ['support_l3', 'support_l2', 'manager'],
    key_permissions: [
      PERMISSIONS.USER_MANAGE_ROLES,
      PERMISSIONS.USER_MANAGE,
      PERMISSIONS.SYSTEM_DIAGNOSTICS,
      PERMISSIONS.TICKET_DELETE_ANY
    ]
  },
  'support_l3': {
    name: 'Level 3 Support',
    level: 6,
    reports_to: 'it_admin',
    manages: ['support_l2'],
    key_permissions: [
      PERMISSIONS.USER_MANAGE,
      PERMISSIONS.TROUBLESHOOT_AUTO_RESOLVE,
      PERMISSIONS.SYSTEM_DIAGNOSTICS,
      PERMISSIONS.TICKET_UPDATE_ANY
    ]
  },
  'support_l2': {
    name: 'Level 2 Support',
    level: 5,
    reports_to: 'support_l3',
    manages: ['support_l1'],
    key_permissions: [
      PERMISSIONS.TROUBLESHOOT_AUTO_RESOLVE,
      PERMISSIONS.SYSTEM_MONITOR,
      PERMISSIONS.REPORTS_EXPORT,
      PERMISSIONS.TICKET_DELETE_ANY
    ]
  },
  'support_l1': {
    name: 'Level 1 Support',
    level: 4,
    reports_to: 'support_l2',
    manages: [],
    key_permissions: [
      PERMISSIONS.TROUBLESHOOT_RUN,
      PERMISSIONS.TICKET_ASSIGN,
      PERMISSIONS.TICKET_VIEW_ALL,
      PERMISSIONS.KB_EDIT
    ]
  },
  'manager': {
    name: 'Manager',
    level: 3,
    reports_to: 'it_admin',
    manages: ['staff', 'contractor'],
    key_permissions: [
      PERMISSIONS.TICKET_VIEW_TEAM,
      PERMISSIONS.REPORTS_VIEW,
      PERMISSIONS.TICKET_ESCALATE,
      PERMISSIONS.DASHBOARD_VIEW
    ]
  },
  'staff': {
    name: 'Staff',
    level: 2,
    reports_to: 'manager',
    manages: [],
    key_permissions: [
      PERMISSIONS.TICKET_VIEW_OWN,
      PERMISSIONS.TICKET_CREATE,
      PERMISSIONS.TICKET_UPDATE_OWN,
      PERMISSIONS.KB_VIEW
    ]
  },
  'contractor': {
    name: 'Contractor',
    level: 1,
    reports_to: 'manager',
    manages: [],
    key_permissions: [
      PERMISSIONS.TICKET_VIEW_OWN,
      PERMISSIONS.TICKET_CREATE,
      PERMISSIONS.KB_VIEW
    ]
  }
};

const RoleCard = ({ roleKey, roleData, expanded, onToggle }) => {
  const displayInfo = getRoleDisplayInfo(roleKey);

  return (
    <div className={`role-card level-${roleData.level}`}>
      <div className="role-card-header" onClick={onToggle}>
        <div className="role-info">
          <Shield size={20} style={{ color: displayInfo.color }} />
          <div>
            <h3>{roleData.name}</h3>
            <span className="role-label" style={{ backgroundColor: displayInfo.color }}>
              {displayInfo.label}
            </span>
          </div>
        </div>
        <button className="expand-btn">
          {expanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
        </button>
      </div>

      {expanded && (
        <div className="role-card-body">
          <div className="role-section">
            <h4>
              <Users size={16} />
              Hierarchy
            </h4>
            <p>
              <strong>Level:</strong> {roleData.level}
            </p>
            {roleData.reports_to && (
              <p>
                <strong>Reports To:</strong> {ROLE_STRUCTURE[roleData.reports_to]?.name}
              </p>
            )}
            {roleData.manages.length > 0 && (
              <p>
                <strong>Manages:</strong> {roleData.manages.map(r => ROLE_STRUCTURE[r]?.name).join(', ')}
              </p>
            )}
          </div>

          <div className="role-section">
            <h4>
              <Lock size={16} />
              Key Permissions
            </h4>
            <ul className="permissions-list">
              {roleData.key_permissions.map((perm, idx) => (
                <li key={idx}>
                  <Check size={14} />
                  <span>{typeof perm === 'string' ? perm.replace(/:/g, ' › ') : perm}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="role-description">
            <p>{displayInfo.description}</p>
          </div>
        </div>
      )}
    </div>
  );
};

const RoleHierarchy = () => {
  const [expandedRoles, setExpandedRoles] = useState({});

  const toggleRole = (roleKey) => {
    setExpandedRoles(prev => ({
      ...prev,
      [roleKey]: !prev[roleKey]
    }));
  };

  const toggleAll = () => {
    const allExpanded = Object.keys(ROLE_STRUCTURE).every(key => expandedRoles[key]);
    if (allExpanded) {
      setExpandedRoles({});
    } else {
      const newExpanded = {};
      Object.keys(ROLE_STRUCTURE).forEach(key => {
        newExpanded[key] = true;
      });
      setExpandedRoles(newExpanded);
    }
  };

  return (
    <div className="role-hierarchy-container">
      <div className="hierarchy-header">
        <div>
          <h2>
            <Shield size={28} />
            Role Hierarchy & Permissions
          </h2>
          <p>Organizational structure and access control overview</p>
        </div>
        <button className="btn-toggle-all" onClick={toggleAll}>
          {Object.keys(expandedRoles).length === Object.keys(ROLE_STRUCTURE).length 
            ? 'Collapse All' 
            : 'Expand All'}
        </button>
      </div>

      <div className="hierarchy-diagram">
        <div className="hierarchy-column">
          <h3 className="column-title">Administrative</h3>
          <RoleCard
            roleKey="system_admin"
            roleData={ROLE_STRUCTURE.system_admin}
            expanded={expandedRoles.system_admin}
            onToggle={() => toggleRole('system_admin')}
          />
          <div className="hierarchy-connector"></div>
          <RoleCard
            roleKey="it_admin"
            roleData={ROLE_STRUCTURE.it_admin}
            expanded={expandedRoles.it_admin}
            onToggle={() => toggleRole('it_admin')}
          />
        </div>

        <div className="hierarchy-column">
          <h3 className="column-title">Support Team</h3>
          <RoleCard
            roleKey="support_l3"
            roleData={ROLE_STRUCTURE.support_l3}
            expanded={expandedRoles.support_l3}
            onToggle={() => toggleRole('support_l3')}
          />
          <div className="hierarchy-connector"></div>
          <RoleCard
            roleKey="support_l2"
            roleData={ROLE_STRUCTURE.support_l2}
            expanded={expandedRoles.support_l2}
            onToggle={() => toggleRole('support_l2')}
          />
          <div className="hierarchy-connector"></div>
          <RoleCard
            roleKey="support_l1"
            roleData={ROLE_STRUCTURE.support_l1}
            expanded={expandedRoles.support_l1}
            onToggle={() => toggleRole('support_l1')}
          />
        </div>

        <div className="hierarchy-column">
          <h3 className="column-title">End Users</h3>
          <RoleCard
            roleKey="manager"
            roleData={ROLE_STRUCTURE.manager}
            expanded={expandedRoles.manager}
            onToggle={() => toggleRole('manager')}
          />
          <div className="hierarchy-connector"></div>
          <RoleCard
            roleKey="staff"
            roleData={ROLE_STRUCTURE.staff}
            expanded={expandedRoles.staff}
            onToggle={() => toggleRole('staff')}
          />
          <div className="hierarchy-connector"></div>
          <RoleCard
            roleKey="contractor"
            roleData={ROLE_STRUCTURE.contractor}
            expanded={expandedRoles.contractor}
            onToggle={() => toggleRole('contractor')}
          />
        </div>
      </div>

      <div className="hierarchy-legend">
        <h3>Understanding the Hierarchy</h3>
        <div className="legend-items">
          <div className="legend-item">
            <Shield size={16} style={{ color: '#dc3545' }} />
            <span><strong>Higher Levels:</strong> Can manage users at lower levels</span>
          </div>
          <div className="legend-item">
            <Users size={16} />
            <span><strong>Reports To:</strong> Direct supervisor in the hierarchy</span>
          </div>
          <div className="legend-item">
            <Lock size={16} />
            <span><strong>Permissions:</strong> Access rights granted to the role</span>
          </div>
          <div className="legend-item">
            <Check size={16} style={{ color: '#28a745' }} />
            <span><strong>Key Permissions:</strong> Most important capabilities</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoleHierarchy;
