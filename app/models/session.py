from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SessionData(BaseModel):
    """Session data stored in Redis"""
    
    user_id: str
    email: str
    name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: str
    
    access_token: str
    refresh_token: Optional[str] = None
    
    roles: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list)
    email_verified: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def has_role(self, role: str) -> bool:
        return role in self.roles
    
    def has_any_role(self, roles: List[str]) -> bool:
        return any(r in self.roles for r in roles)
    
    def in_group(self, group: str) -> bool:
        return group in self.groups
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }