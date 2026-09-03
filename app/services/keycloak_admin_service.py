from keycloak import KeycloakAdmin  # ✅ FIXED: was python_keycloak
from app.config import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class KeycloakAdminService:
    """Keycloak Admin Service"""
    
    def __init__(self):
        self.admin = KeycloakAdmin(
            server_url=settings.KEYCLOAK_SERVER_URL,
            username=settings.KEYCLOAK_ADMIN_USERNAME,
            password=settings.KEYCLOAK_ADMIN_PASSWORD,
            realm_name=settings.KEYCLOAK_REALM,
            verify=settings.KEYCLOAK_VERIFY_SSL,
        )
    
    async def get_users(self, search: str = "") -> List[Dict]:
        """Get all users"""
        return self.admin.get_users({"search": search})
    
    async def get_user(self, user_id: str) -> Dict:
        """Get user by ID"""
        return self.admin.get_user(user_id)
    
    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        roles: List[str] = None,
        email_verified: bool = False,  # ✅ FIXED: Don't auto-verify
    ) -> str:
        """Create new user"""
        user_data = {
            "email": email,
            "username": username,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": True,
            "emailVerified": email_verified,  # ✅ FIXED: Configurable
            "credentials": [{
                "type": "password",
                "value": password,
                "temporary": False,
            }],
        }
        
        user_id = self.admin.create_user(user_data)
        
        if roles:
            await self.assign_realm_roles(user_id, roles)
        
        logger.info(f"Created user: {email} (ID: {user_id})")
        return user_id
    
    async def delete_user(self, user_id: str) -> None:
        """Delete user"""
        self.admin.delete_user(user_id)
        logger.info(f"Deleted user: {user_id}")
    
    async def get_realm_roles(self) -> List[Dict]:
        """Get all realm roles"""
        return self.admin.get_realm_roles()
    
    async def assign_realm_roles(self, user_id: str, roles: List[str]) -> None:
        """Assign roles to user"""
        realm_roles = self.admin.get_realm_roles()
        roles_to_assign = [r for r in realm_roles if r["name"] in roles]
        self.admin.assign_realm_roles(user_id, roles_to_assign)
    
    async def logout_user(self, user_id: str) -> None:
        """Force logout user"""
        self.admin.user_logout(user_id)