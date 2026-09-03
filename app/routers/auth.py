from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from app.services.oauth2_service import OAuth2Service
from app.services.session_service import SessionService
from app.config import settings
import logging

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

oauth2_service = OAuth2Service()
session_service = SessionService()


@router.get("/login")
async def login(request: Request, redirect_to: str = "/"):
    """Initiate login"""
    state = oauth2_service.generate_state()
    auth_url = oauth2_service.get_authorization_url(state)
    
    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        max_age=300,
        httponly=True,
        secure=settings.COOKIE_SECURE,
    )
    response.set_cookie(
        key="redirect_to",
        value=redirect_to,
        max_age=300,
        httponly=True,
    )
    return response


@router.get("/callback")
async def callback(request: Request, code: str, state: str):
    """Handle callback"""
    stored_state = request.cookies.get("oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(status_code=400, detail="Invalid state")
    
    try:
        user_info = await oauth2_service.authenticate(code)
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        raise HTTPException(status_code=400, detail="Authentication failed")
    
    if not oauth2_service.is_allowed(user_info):
        raise HTTPException(
            status_code=403,
            detail=f"Access denied for {user_info.get('email')}",
        )
    
    session_id = await session_service.create_session(
        user_info,
        user_info.get("raw_token", {}),
    )
    
    redirect_to = request.cookies.get("redirect_to", "/")
    response = RedirectResponse(url=redirect_to)
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=session_id,
        max_age=settings.SESSION_EXPIRE_SECONDS,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
    )
    response.delete_cookie("oauth_state")
    response.delete_cookie("redirect_to")
    return response


@router.get("/logout")
async def logout(request: Request):
    """Logout"""
    session_id = request.cookies.get(settings.COOKIE_NAME)
    
    if session_id:
        session = await session_service.get_session(session_id)
        
        if session and session.refresh_token:
            await oauth2_service.logout(session.refresh_token)
        
        await session_service.delete_session(session_id)
    
    response = RedirectResponse(url="/auth/login")
    response.delete_cookie(settings.COOKIE_NAME)
    return response


@router.get("/me")
async def get_current_user(request: Request):
    """Get current user"""
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = request.state.user
    return {
        "email": user.email,
        "name": user.name,
        "username": user.username,
        "avatar_url": user.avatar_url,
        "provider": user.provider,
        "roles": user.roles,
        "groups": user.groups,
        "email_verified": user.email_verified,
    }