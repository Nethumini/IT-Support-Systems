"""
Role and Permission models for Role-Based Access Control (RBAC).
"""
from enum import Enum
from typing import List, Set
from pydantic import BaseModel


class Permission(str, Enum):
    """System permissions."""
    # Ticket permissions
    TICKET_VIEW_OWN = "ticket:view:own"
    TICKET_VIEW_TEAM = "ticket:view:team"
    TICKET_VIEW_ALL = "ticket:view:all"
    TICKET_CREATE = "ticket:create"
    TICKET_UPDATE_OWN = "ticket:update:own"
    TICKET_UPDATE_ANY = "ticket:update:any"
    TICKET_DELETE_OWN = "ticket:delete:own"
    TICKET_DELETE_ANY = "ticket:delete:any"
    TICKET_ASSIGN = "ticket:assign"
    TICKET_ESCALATE = "ticket:escalate"
    
    # Troubleshooting permissions
    TROUBLESHOOT_RUN = "troubleshoot:run"
    TROUBLESHOOT_AUTO_RESOLVE = "troubleshoot:auto_resolve"
    TROUBLESHOOT_VIEW_LOGS = "troubleshoot:view_logs"
    
    # System permissions
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_DIAGNOSTICS = "system:diagnostics"
    SYSTEM_ADMIN = "system:admin"
    
    # User management permissions
    USER_VIEW = "user:view"
    USER_MANAGE = "user:manage"
    USER_MANAGE_ROLES = "user:manage_roles"
    
    # Dashboard & Reports
    DASHBOARD_VIEW = "dashboard:view"
    REPORTS_VIEW = "reports:view"
    REPORTS_EXPORT = "reports:export"
    
    # Knowledge Base
    KB_VIEW = "kb:view"
    KB_EDIT = "kb:edit"


class Role(str, Enum):
    """User roles with hierarchical permissions."""
    # End users
    STAFF = "staff"
    CONTRACTOR = "contractor"
    MANAGER = "manager"
    
    # IT Support roles
    SUPPORT_L1 = "support_l1"  # Level 1 Support
    SUPPORT_L2 = "support_l2"  # Level 2 Support
    SUPPORT_L3 = "support_l3"  # Level 3 Support
    
    # Admin roles
    IT_ADMIN = "it_admin"
    SYSTEM_ADMIN = "system_admin"


# Role to Permissions Mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    # STAFF: Basic users - can only manage their own tickets
    Role.STAFF: {
        Permission.TICKET_VIEW_OWN,
        Permission.TICKET_CREATE,
        Permission.TICKET_UPDATE_OWN,
        Permission.DASHBOARD_VIEW,
        Permission.KB_VIEW,
    },
    
    # CONTRACTOR: Limited access, cannot see sensitive data
    Role.CONTRACTOR: {
        Permission.TICKET_VIEW_OWN,
        Permission.TICKET_CREATE,
        Permission.KB_VIEW,
    },
    
    # MANAGER: Can view team tickets and reports
    Role.MANAGER: {
        Permission.TICKET_VIEW_OWN,
        Permission.TICKET_VIEW_TEAM,
        Permission.TICKET_CREATE,
        Permission.TICKET_UPDATE_OWN,
        Permission.TICKET_ESCALATE,
        Permission.DASHBOARD_VIEW,
        Permission.REPORTS_VIEW,
        Permission.KB_VIEW,
    },
    
    # SUPPORT_L1: Basic support staff - can view and work on assigned tickets
    Role.SUPPORT_L1: {
        Permission.TICKET_VIEW_ALL,
        Permission.TICKET_CREATE,
        Permission.TICKET_UPDATE_ANY,
        Permission.TICKET_ASSIGN,
        Permission.TICKET_ESCALATE,
        Permission.TROUBLESHOOT_RUN,
        Permission.TROUBLESHOOT_VIEW_LOGS,
        Permission.DASHBOARD_VIEW,
        Permission.REPORTS_VIEW,
        Permission.KB_VIEW,
        Permission.KB_EDIT,
        Permission.USER_VIEW,
    },
    
    # SUPPORT_L2: Advanced support - can run diagnostics and auto-resolve
    Role.SUPPORT_L2: {
        Permission.TICKET_VIEW_ALL,
        Permission.TICKET_CREATE,
        Permission.TICKET_UPDATE_ANY,
        Permission.TICKET_DELETE_ANY,
        Permission.TICKET_ASSIGN,
        Permission.TICKET_ESCALATE,
        Permission.TROUBLESHOOT_RUN,
        Permission.TROUBLESHOOT_AUTO_RESOLVE,
        Permission.TROUBLESHOOT_VIEW_LOGS,
        Permission.SYSTEM_MONITOR,
        Permission.SYSTEM_DIAGNOSTICS,
        Permission.DASHBOARD_VIEW,
        Permission.REPORTS_VIEW,
        Permission.REPORTS_EXPORT,
        Permission.KB_VIEW,
        Permission.KB_EDIT,
        Permission.USER_VIEW,
    },
    
    # SUPPORT_L3: Senior support - full troubleshooting and system access
    Role.SUPPORT_L3: {
        Permission.TICKET_VIEW_ALL,
        Permission.TICKET_CREATE,
        Permission.TICKET_UPDATE_ANY,
        Permission.TICKET_DELETE_ANY,
        Permission.TICKET_ASSIGN,
        Permission.TICKET_ESCALATE,
        Permission.TROUBLESHOOT_RUN,
        Permission.TROUBLESHOOT_AUTO_RESOLVE,
        Permission.TROUBLESHOOT_VIEW_LOGS,
        Permission.SYSTEM_MONITOR,
        Permission.SYSTEM_DIAGNOSTICS,
        Permission.DASHBOARD_VIEW,
        Permission.REPORTS_VIEW,
        Permission.REPORTS_EXPORT,
        Permission.KB_VIEW,
        Permission.KB_EDIT,
        Permission.USER_VIEW,
        Permission.USER_MANAGE,
    },
    
    # IT_ADMIN: IT department admin - full access except system config
    Role.IT_ADMIN: {
        Permission.TICKET_VIEW_ALL,
        Permission.TICKET_CREATE,
        Permission.TICKET_UPDATE_ANY,
        Permission.TICKET_DELETE_ANY,
        Permission.TICKET_ASSIGN,
        Permission.TICKET_ESCALATE,
        Permission.TROUBLESHOOT_RUN,
        Permission.TROUBLESHOOT_AUTO_RESOLVE,
        Permission.TROUBLESHOOT_VIEW_LOGS,
        Permission.SYSTEM_MONITOR,
        Permission.SYSTEM_DIAGNOSTICS,
        Permission.SYSTEM_ADMIN,
        Permission.DASHBOARD_VIEW,
        Permission.REPORTS_VIEW,
        Permission.REPORTS_EXPORT,
        Permission.KB_VIEW,
        Permission.KB_EDIT,
        Permission.USER_VIEW,
        Permission.USER_MANAGE,
        Permission.USER_MANAGE_ROLES,
    },
    
    # SYSTEM_ADMIN: Full system access
    Role.SYSTEM_ADMIN: set(Permission),  # All permissions
}


class RoleInfo(BaseModel):
    """Role information model."""
    role: Role
    permissions: List[Permission]
    description: str


def get_role_permissions(role: Role) -> Set[Permission]:
    """Get permissions for a given role."""
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: Role, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    return permission in get_role_permissions(role)


def can_view_ticket(user_role: Role, ticket_user_email: str, current_user_email: str, 
                    ticket_assigned_to: str = None, team_member_emails: List[str] = None) -> bool:
    """
    Determine if a user can view a specific ticket based on their role.
    
    Args:
        user_role: The role of the user trying to view the ticket
        ticket_user_email: Email of the user who created the ticket
        current_user_email: Email of the current user
        ticket_assigned_to: Who the ticket is assigned to
        team_member_emails: List of team member emails for managers
    
    Returns:
        True if the user can view the ticket, False otherwise
    """
    role_perms = get_role_permissions(user_role)
    
    # Admins and support can view all tickets
    if Permission.TICKET_VIEW_ALL in role_perms:
        return True
    
    # Can view own tickets
    if Permission.TICKET_VIEW_OWN in role_perms and ticket_user_email == current_user_email:
        return True
    
    # Support staff can view assigned tickets
    if ticket_assigned_to and ticket_assigned_to == current_user_email:
        return True
    
    # Managers can view team tickets (team member tickets)
    if Permission.TICKET_VIEW_TEAM in role_perms:
        if team_member_emails and ticket_user_email in team_member_emails:
            return True
    
    return False


def can_update_ticket(user_role: Role, ticket_user_email: str, current_user_email: str, 
                      ticket_assigned_to: str = None, team_member_emails: List[str] = None) -> bool:
    """
    Check if user can update a ticket.
    
    Args:
        user_role: The role of the user trying to update the ticket
        ticket_user_email: Email of the user who created the ticket
        current_user_email: Email of the current user
        ticket_assigned_to: Who the ticket is assigned to
        team_member_emails: List of team member emails for managers
    
    Returns:
        True if the user can update the ticket, False otherwise
    """
    role_perms = get_role_permissions(user_role)
    
    if Permission.TICKET_UPDATE_ANY in role_perms:
        return True
    
    if Permission.TICKET_UPDATE_OWN in role_perms and ticket_user_email == current_user_email:
        return True
    
    # Support staff can update assigned tickets
    if ticket_assigned_to and ticket_assigned_to == current_user_email:
        if Permission.TICKET_UPDATE_ANY in role_perms or Permission.TICKET_UPDATE_OWN in role_perms:
            return True
    
    # Managers can update team member tickets
    if Permission.TICKET_UPDATE_OWN in role_perms and team_member_emails and ticket_user_email in team_member_emails:
        return True
    
    return False


# Role descriptions for UI display
ROLE_DESCRIPTIONS = {
    Role.STAFF: "Standard employee - can create and view own tickets",
    Role.CONTRACTOR: "External contractor - limited access to own tickets only",
    Role.MANAGER: "Team manager - can view team tickets and reports",
    Role.SUPPORT_L1: "Level 1 Support - basic ticket handling and troubleshooting",
    Role.SUPPORT_L2: "Level 2 Support - advanced diagnostics and system monitoring",
    Role.SUPPORT_L3: "Level 3 Support - senior engineer with full troubleshooting access",
    Role.IT_ADMIN: "IT Administrator - full IT operations access",
    Role.SYSTEM_ADMIN: "System Administrator - complete system access",
}
