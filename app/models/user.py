from sqlalchemy import Column, String, Boolean, DateTime, Integer
from datetime import datetime
from app.database import Base
import uuid


class User(Base):
    """User model for local storage"""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=True)
    given_name = Column(String(100), nullable=True)
    family_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    provider = Column(String(50), nullable=False)  # keycloak, google, github
    provider_id = Column(String(255), nullable=False)
    
    is_active = Column(Boolean, default=True)
    is_allowed = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "name": self.name,
            "provider": self.provider,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }