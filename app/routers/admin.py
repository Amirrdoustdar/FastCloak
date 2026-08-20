from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.keycloak_admin_service import KeycloakAdminService
from app.utils.keycloak_utils import RoleChecker
import logging

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)

admin_required = RoleChecker(["admin", "realm-admin"])
keycloak_admin = KeycloakAdminService()


class CreateUserRequest(BaseModel):
    email: str
    username: str
    password: str
    first_name: str = ""
    last_name: str = ""
    roles: List[str] = []


@router.get("/users", dependencies=[Depends(admin_required)])
async def list_users(search: str = ""):
    """List all users in Keycloak realm"""
    return await keycloak_admin.get_users(search)


@router.post("/users", dependencies=[Depends(admin_required)])
async def create_user(data: CreateUserRequest):
    """Create new user in Keycloak"""
    try:
        user_id = await keycloak_admin.create_user(
            email=data.email,
            username=data.username,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            roles=data.roles,
        )
        return {"user_id": user_id, "message": "User created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{user_id}", dependencies=[Depends(admin_required)])
async def get_user(user_id: str):
    """Get user by ID"""
    return await keycloak_admin.get_user(user_id)


@router.delete("/users/{user_id}", dependencies=[Depends(admin_required)])
async def delete_user(user_id: str):
    """Delete user"""
    await keycloak_admin.delete_user(user_id)
    return {"message": "User deleted"}


@router.get("/roles", dependencies=[Depends(admin_required)])
async def list_roles():
    """List all realm roles"""
    return await keycloak_admin.get_realm_roles()


@router.post("/users/{user_id}/logout", dependencies=[Depends(admin_required)])
async def force_logout_user(user_id: str):
    """Force logout a user from all sessions"""
    await keycloak_admin.logout_user(user_id)
    return {"message": "User logged out"}