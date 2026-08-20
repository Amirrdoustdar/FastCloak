from python_keycloak import KeycloakAdmin
from app.config import settings
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class KeycloakAdminService:
    """Keycloak Admin Service for user management"""
    
    def __init__(self):
        self.admin = KeycloakAdmin(
            server_url=settings.KEYCLOAK_SERVER_URL,
            username=settings.KEYCLOAK_ADMIN_USERNAME,
            password=settings.KEYCLOAK_ADMIN_PASSWORD,
            realm_name=settings.KEYCLOAK_REALM,
            verify=settings.KEYCLOAK_VERIFY_SSL,
        )
    
    # User Management
    async def get_users(self, search: str = "") -> List[Dict]:
        """Get all users in realm"""
        return self.admin.get_users({"search": search})
    
    async def get_user(self, user_id: str) -> Dict:
        """Get user by ID"""
        return self.admin.get_user(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        users = self.admin.get_users({"email": email})
        return users[0] if users else None
    
    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        roles: List[str] = None,
    ) -> str:
        """Create new user in Keycloak"""
        user_data = {
            "email": email,
            "username": username,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": True,
            "emailVerified": True,
            "credentials": [
                {
                    "type": "password",
                    "value": password,
                    "temporary": False,
                }
            ],
        }
        
        user_id = self.admin.create_user(user_data)
        
        if roles:
            await self.assign_realm_roles(user_id, roles)
        
        logger.info(f"Created user: {email} (ID: {user_id})")
        return user_id
    
    async def update_user(self, user_id: str, data: Dict) -> None:
        """Update user attributes"""
        self.admin.update_user(user_id, data)
    
    async def delete_user(self, user_id: str) -> None:
        """Delete user from Keycloak"""
        self.admin.delete_user(user_id)
        logger.info(f"Deleted user: {user_id}")
    
    async def reset_password(self, user_id: str, new_password: str) -> None:
        """Reset user password"""
        self.admin.set_user_password(user_id, new_password, temporary=False)
    
    # Role Management
    async def get_realm_roles(self) -> List[Dict]:
        """Get all realm roles"""
        return self.admin.get_realm_roles()
    
    async def assign_realm_roles(self, user_id: str, roles: List[str]) -> None:
        """Assign roles to user"""
        realm_roles = self.admin.get_realm_roles()
        roles_to_assign = [r for r in realm_roles if r["name"] in roles]
        self.admin.assign_realm_roles(user_id, roles_to_assign)
    
    async def get_user_roles(self, user_id: str) -> List[Dict]:
        """Get roles assigned to user"""
        return self.admin.get_realm_roles_of_user(user_id)
    
    # Group Management
    async def get_groups(self) -> List[Dict]:
        """Get all groups"""
        return self.admin.get_groups()
    
    async def add_user_to_group(self, user_id: str, group_id: str) -> None:
        """Add user to group"""
        self.admin.group_user_add(user_id, group_id)
    
    # Session Management
    async def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get active sessions for user"""
        return self.admin.get_sessions(user_id)
    
    async def logout_user(self, user_id: str) -> None:
        """Force logout user from all sessions"""
        self.admin.user_logout(user_id)