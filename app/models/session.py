from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SessionData(BaseModel):
    """Session data model stored in Redis"""
    
    user_id: str
    email: str
    name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: str
    
    access_token: str
    refresh_token: Optional[str] = None
    
    # Keycloak specific
    roles: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list)
    email_verified: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return role in self.roles
    
    def has_any_role(self, roles: List[str]) -> bool:
        """Check if user has any of the specified roles"""
        return any(r in self.roles for r in roles)
    
    def in_group(self, group: str) -> bool:
        """Check if user is in specific group"""
        return group in self.groups
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TokenResponse(BaseModel):
    """OAuth2 token response"""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None