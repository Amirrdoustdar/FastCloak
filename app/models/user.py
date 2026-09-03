from sqlalchemy import Column, String, Boolean, DateTime, Integer
from datetime import datetime
from app.database import Base
import uuid


class User(Base):
    """User model"""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    provider = Column(String(50), nullable=False)
    provider_id = Column(String(255), nullable=False)
    
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<User {self.email}>"