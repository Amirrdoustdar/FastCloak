from fastapi import APIRouter, Depends
from app.utils.keycloak_utils import (
    require_roles,
    RoleChecker,
    get_current_session,
)
from app.models.session import SessionData

router = APIRouter(prefix="/api", tags=["Protected Routes"])

admin_only = RoleChecker(["admin"])
manager_only = RoleChecker(["admin", "manager"])


@router.get("/dashboard")
async def dashboard(session: SessionData = Depends(get_current_session)):
    """Any authenticated user"""
    return {
        "message": f"Welcome {session.name}!",
        "roles": session.roles,
        "groups": session.groups,
    }


@router.get("/admin/panel", dependencies=[Depends(admin_only)])
async def admin_panel():
    """Admin only"""
    return {"message": "Admin panel"}


@router.get("/manager/reports", dependencies=[Depends(manager_only)])
async def manager_reports():
    """Admin or Manager"""
    return {"message": "Manager reports"}


@router.get("/profile")
async def profile(session: SessionData = Depends(get_current_session)):
    """User profile"""
    return {
        "email": session.email,
        "name": session.name,
        "is_admin": session.has_role("admin"),
        "roles": session.roles,
    }