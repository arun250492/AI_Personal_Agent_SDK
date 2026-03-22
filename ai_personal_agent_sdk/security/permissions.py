"""
Permission management system for secure access control
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Permission:
    action: str
    resource: str
    granted_at: float
    expires_at: float
    approved: bool = False


class PermissionManager:
    """
    Manages permissions for various actions and resources
    """

    def __init__(self):
        self.permissions: Dict[str, Permission] = {}
        self.pending_permissions: Dict[str, Permission] = {}

    def request_permission(self, action: str, resource: str, duration_minutes: int = 60) -> bool:
        """
        Request permission for an action on a resource

        Returns True if permission is granted, False if denied or pending
        """
        permission_id = f"{action}:{resource}"

        # Check if permission already exists and is valid
        if permission_id in self.permissions:
            perm = self.permissions[permission_id]
            if time.time() < perm.expires_at and perm.approved:
                return True
            elif time.time() >= perm.expires_at:
                # Expired, remove it
                del self.permissions[permission_id]

        # Create new permission request
        expires_at = time.time() + (duration_minutes * 60)
        permission = Permission(
            action=action,
            resource=resource,
            granted_at=time.time(),
            expires_at=expires_at,
            approved=False
        )

        self.pending_permissions[permission_id] = permission

        # For now, auto-approve common safe actions
        safe_actions = ["read_calendar", "read_email", "send_notification"]
        if action in safe_actions:
            return self.approve_permission(permission_id)

        # For sensitive actions, require manual approval
        print(f"Permission requested: {action} on {resource}")
        print(f"Duration: {duration_minutes} minutes")
        print("Approve? (y/n): ", end="")
        response = input().strip().lower()
        if response == 'y':
            return self.approve_permission(permission_id)
        else:
            return False

    def approve_permission(self, permission_id: str) -> bool:
        """Approve a pending permission"""
        if permission_id in self.pending_permissions:
            permission = self.pending_permissions[permission_id]
            permission.approved = True
            self.permissions[permission_id] = permission
            del self.pending_permissions[permission_id]
            return True
        return False

    def deny_permission(self, permission_id: str) -> bool:
        """Deny a pending permission"""
        if permission_id in self.pending_permissions:
            del self.pending_permissions[permission_id]
            return True
        return False

    def revoke_permission(self, permission_id: str) -> bool:
        """Revoke an active permission"""
        if permission_id in self.permissions:
            del self.permissions[permission_id]
            return True
        return False

    def get_pending_permissions(self) -> List[Permission]:
        """Get list of pending permissions"""
        return list(self.pending_permissions.values())

    def get_active_permissions(self) -> List[Permission]:
        """Get list of active permissions"""
        current_time = time.time()
        return [p for p in self.permissions.values() if p.expires_at > current_time]

    def is_permission_valid(self, action: str, resource: str) -> bool:
        """Check if permission is valid for action and resource"""
        permission_id = f"{action}:{resource}"
        if permission_id in self.permissions:
            perm = self.permissions[permission_id]
            return time.time() < perm.expires_at and perm.approved
        return False