from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.session_service import SessionService
from app.config import settings
import re
import logging

logger = logging.getLogger(__name__)

PUBLIC_PATHS = [
    r"^/auth/login$",
    r"^/auth/callback$",
    r"^/auth/logout$",
    r"^/health$",
    r"^/ready$",
    r"^/docs$",
    r"^/openapi.json$",
    r"^/redoc$",
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
            # Check Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                # Validate token (implement if needed)
                pass
            
            # Redirect to login or return 401
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
        
        # Attach user to request state
        request.state.user = session
        request.state.session_id = session_id
        
        # Refresh session TTL
        await self.session_service.refresh_session(session_id)
        
        return await call_next(request)