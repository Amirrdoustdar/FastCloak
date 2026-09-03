import redis.asyncio as aioredis
from typing import Optional
from datetime import datetime, timedelta
from app.config import settings
from app.models.session import SessionData
import uuid
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """Redis session management"""
    
    def __init__(self):
        self.redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    
    async def create_session(self, user_info: dict, token_data: dict) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())
        
        session_data = SessionData(
            user_id=user_info["id"],
            email=user_info["email"],
            name=user_info.get("name"),
            username=user_info.get("username"),
            avatar_url=user_info.get("avatar_url"),
            provider=user_info["provider"],
            access_token=token_data.get("access_token", ""),
            refresh_token=token_data.get("refresh_token"),
            roles=user_info.get("roles", []),
            groups=user_info.get("groups", []),
            email_verified=user_info.get("email_verified", False),
            expires_at=datetime.utcnow() + timedelta(
                seconds=settings.SESSION_EXPIRE_SECONDS
            ),
        )
        
        await self.redis.setex(
            f"session:{session_id}",
            settings.SESSION_EXPIRE_SECONDS,
            session_data.model_dump_json(),
        )
        
        logger.info(f"Created session for: {user_info['email']}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session"""
        data = await self.redis.get(f"session:{session_id}")
        if not data:
            return None
        return SessionData.model_validate_json(data)
    
    async def update_session(self, session_id: str, session_data: SessionData) -> bool:
        """Update session"""
        result = await self.redis.setex(
            f"session:{session_id}",
            settings.SESSION_EXPIRE_SECONDS,
            session_data.model_dump_json(),
        )
        return result
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        result = await self.redis.delete(f"session:{session_id}")
        return result > 0
    
    async def refresh_session(self, session_id: str) -> bool:
        """Refresh session TTL"""
        result = await self.redis.expire(
            f"session:{session_id}",
            settings.SESSION_EXPIRE_SECONDS,
        )
        return result