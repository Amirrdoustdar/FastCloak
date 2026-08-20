import httpx
import jwt
from typing import Optional, Dict, Any, List
from app.config import settings
from python_keycloak import KeycloakOpenID
from python_keycloak.exceptions import KeycloakAuthenticationError
import logging

logger = logging.getLogger(__name__)


class KeycloakOIDCProvider:
    """Keycloak OpenID Connect Provider"""
    
    def __init__(self):
        self.keycloak_openid = KeycloakOpenID(
            server_url=settings.KEYCLOAK_SERVER_URL,
            realm_name=settings.KEYCLOAK_REALM,
            client_id=settings.KEYCLOAK_CLIENT_ID,
            client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
            verify=settings.KEYCLOAK_VERIFY_SSL,
        )
        self._public_key: Optional[str] = None
    
    def get_authorization_url(self, state: str) -> str:
        """Generate Keycloak login URL"""
        auth_url = self.keycloak_openid.auth_url(
            redirect_uri=settings.KEYCLOAK_REDIRECT_URI,
            scope="openid email profile roles",
            state=state,
        )
        return auth_url
    
    async def get_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        try:
            token = self.keycloak_openid.token(
                grant_type="authorization_code",
                code=code,
                redirect_uri=settings.KEYCLOAK_REDIRECT_URI,
            )
            return token
        except KeycloakAuthenticationError as e:
            logger.error(f"Token exchange failed: {e}")
            raise
    
    async def introspect_token(self, token: str) -> Dict[str, Any]:
        """Introspect token with Keycloak"""
        return self.keycloak_openid.introspect(token)
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Get new access token using refresh token"""
        try:
            return self.keycloak_openid.refresh_token(refresh_token)
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Keycloak userinfo endpoint"""
        user_info = self.keycloak_openid.userinfo(access_token)
        return {
            "id": user_info.get("sub"),
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "given_name": user_info.get("given_name"),
            "family_name": user_info.get("family_name"),
            "avatar_url": user_info.get("picture"),
            "username": user_info.get("preferred_username"),
            "email_verified": user_info.get("email_verified", False),
            "provider": "keycloak",
        }
    
    async def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate Keycloak JWT token"""
        public_key = await self._get_public_key()
        
        options = {
            "verify_signature": True,
            "verify_exp": True,
            "verify_aud": False,
        }
        
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options=options,
        )
        return decoded
    
    async def _get_public_key(self) -> str:
        """Get Keycloak realm public key (cached)"""
        if self._public_key:
            return self._public_key
        
        public_key = self.keycloak_openid.public_key()
        self._public_key = (
            f"-----BEGIN PUBLIC KEY-----\n"
            f"{public_key}\n"
            f"-----END PUBLIC KEY-----"
        )
        return self._public_key
    
    async def logout(self, refresh_token: str) -> None:
        """Logout from Keycloak"""
        try:
            self.keycloak_openid.logout(refresh_token)
        except Exception as e:
            logger.warning(f"Keycloak logout error: {e}")
    
    def extract_roles(self, decoded_token: Dict) -> List[str]:
        """Extract roles from Keycloak JWT"""
        roles = []
        
        # Realm roles
        realm_access = decoded_token.get("realm_access", {})
        roles.extend(realm_access.get("roles", []))
        
        # Client roles
        resource_access = decoded_token.get("resource_access", {})
        client_roles = resource_access.get(
            settings.KEYCLOAK_CLIENT_ID, {}
        ).get("roles", [])
        roles.extend(client_roles)
        
        return roles
    
    def extract_groups(self, decoded_token: Dict) -> List[str]:
        """Extract groups from Keycloak JWT"""
        return decoded_token.get("groups", [])
    
    def check_authorization(self, decoded_token: Dict) -> bool:
        """Check if user has required roles/groups"""
        if not settings.REQUIRED_ROLES and not settings.REQUIRED_GROUPS:
            return True
        
        user_roles = self.extract_roles(decoded_token)
        user_groups = self.extract_groups(decoded_token)
        
        if settings.REQUIRED_ROLES:
            if not any(role in user_roles for role in settings.REQUIRED_ROLES):
                return False
        
        if settings.REQUIRED_GROUPS:
            if not any(group in user_groups for group in settings.REQUIRED_GROUPS):
                return False
        
        return True