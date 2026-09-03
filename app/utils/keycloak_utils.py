from fastapi import Request, HTTPException, Depends
from typing import List
from app.models.session import SessionData


def get_current_session(request: Request) -> SessionData:
    """Get current user session"""
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.state.user


def require_roles(roles: List[str]):
    """Require specific roles"""
    def check_roles(session: SessionData = Depends(get_current_session)):
        if not session.has_any_role(roles):
            raise HTTPException(
                status_code=403,
                detail=f"Required roles: {roles}. Your roles: {session.roles}",
            )
        return session
    return check_roles


def require_group(group: str):
    """Require specific group"""
    def check_group(session: SessionData = Depends(get_current_session)):
        if not session.in_group(group):
            raise HTTPException(
                status_code=403,
                detail=f"Required group: {group}",
            )
        return session
    return check_group


class RoleChecker:
    """Class-based role checker"""
    
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles
    
    def __call__(self, session: SessionData = Depends(get_current_session)):
        if not session.has_any_role(self.required_roles):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions",
            )
        return session