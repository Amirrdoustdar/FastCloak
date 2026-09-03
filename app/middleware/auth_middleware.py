from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.session_service import SessionService
from app.config import settings
import re
import logging

logger = logging.getLogger(__name__)

# ✅ FIXED: Docs not public in production
PUBLIC_PATHS = [
    r"^/auth/login$",
    r"^/auth/callback$",
    r"^/auth/logout$",
    r"^/health$",
    r"^/ready$",
    r"^/$",
]


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication Middleware"""
    
    def __init__(self, app, session_service: SessionService):
        super().__init__(app)
        self.session_service = session_service
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Check if path is public
        for pattern in PUBLIC_PATHS:
            if re.match(pattern, path):
                return await call_next(request)
        
        # Get session from cookie
        session_id = request.cookies.get(settings.COOKIE_NAME)
        
        if not session_id:
            # ✅ FIXED: Actually validate Bearer token
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                
                bearer_auth_result = await self._validate_bearer_token(token)
                if bearer_auth_result:
                    request.state.user = bearer_auth_result
                    request.state.session_id = None
                    return await call_next(request)
                else:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Invalid or expired token"},
                    )
            
            # No auth
            if request.headers.get("Accept", "").startswith("application/json"):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Not authenticated"},
                )
            return RedirectResponse(url="/auth/login")
        
        # Validate session
        session = await self.session_service.get_session(session_id)
        
        if not session:
            response = RedirectResponse(url="/auth/login")
            response.delete_cookie(settings.COOKIE_NAME)
            return response
        
        # Attach user to request
        request.state.user = session
        request.state.session_id = session_id
        
        # Refresh session TTL
        await self.session_service.refresh_session(session_id)
        
        return await call_next(request)
    
    async def _validate_bearer_token(self, token: str):
        """✅ FIXED: Actually validates Bearer tokens"""
        try:
            from app.services.keycloak_service import KeycloakOIDCProvider
            from app.models.session import SessionData
            
            keycloak = KeycloakOIDCProvider()
            
            # Decode JWT
            decoded = await keycloak.decode_token(token)
            
            # Check authorization
            if not keycloak.check_authorization(decoded):
                logger.warning(f"Bearer auth failed for: {decoded.get('email')}")
                return None
            
            # Create session data
            session_data = SessionData(
                user_id=decoded.get("sub"),
                email=decoded.get("email", ""),
                name=decoded.get("name"),
                username=decoded.get("preferred_username"),
                provider="keycloak",
                access_token=token,
                roles=keycloak.extract_roles(decoded),
                groups=keycloak.extract_groups(decoded),
                email_verified=decoded.get("email_verified", False),
            )
            
            logger.info(f"Bearer token validated: {session_data.email}")
            return session_data
            
        except Exception as e:
            logger.error(f"Bearer token validation failed: {e}")
            return None