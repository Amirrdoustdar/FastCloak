from typing import Dict, Any
from app.config import settings
from app.services.keycloak_service import KeycloakOIDCProvider
import secrets
import logging

logger = logging.getLogger(__name__)


class OAuth2Service:
    """Unified OAuth2 Service"""
    
    def __init__(self):
        self.provider_name = settings.OAUTH2_PROVIDER
        self.provider = self._init_provider()
    
    def _init_provider(self):
        if settings.OAUTH2_PROVIDER == "keycloak":
            return KeycloakOIDCProvider()
        else:
            raise ValueError(f"Unsupported provider: {settings.OAUTH2_PROVIDER}")
    
    def generate_state(self) -> str:
        return secrets.token_urlsafe(32)
    
    def get_authorization_url(self, state: str) -> str:
        return self.provider.get_authorization_url(state)
    
    async def authenticate(self, code: str) -> Dict[str, Any]:
        """Full authentication flow"""
        token_data = await self.provider.get_token(code)
        access_token = token_data.get("access_token")
        
        user_info = await self.provider.get_user_info(access_token)
        user_info["raw_token"] = token_data
        
        if self.provider_name == "keycloak":
            decoded = await self.provider.decode_token(access_token)
            user_info["roles"] = self.provider.extract_roles(decoded)
            user_info["groups"] = self.provider.extract_groups(decoded)
            user_info["decoded_token"] = decoded
        
        return user_info
    
    def is_allowed(self, user_info: Dict) -> bool:
        """Check if user is allowed"""
        email = user_info.get("email", "")
        
        if settings.ALLOWED_EMAILS or settings.ALLOWED_DOMAINS:
            if email in settings.ALLOWED_EMAILS:
                return True
            domain = email.split("@")[-1]
            if domain in settings.ALLOWED_DOMAINS:
                return True
            return False
        
        if self.provider_name == "keycloak":
            decoded = user_info.get("decoded_token", {})
            return self.provider.check_authorization(decoded)
        
        return True
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        if self.provider_name == "keycloak":
            return await self.provider.refresh_token(refresh_token)
        raise NotImplementedError("Token refresh not implemented for this provider")
    
    async def logout(self, refresh_token: str) -> None:
        """Provider-side logout"""
        if self.provider_name == "keycloak":
            await self.provider.logout(refresh_token)