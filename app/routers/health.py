from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.config import settings
import redis.asyncio as aioredis
import httpx

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.APP_NAME,
        "version": "1.0.0",
    }


@router.get("/ready")
async def readiness_check():
    """✅ FIXED: Real dependency checks"""
    checks = {
        "redis": False,
        "keycloak": False,
    }
    
    # Check Redis
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await redis_client.ping()
        await redis_client.close()
        checks["redis"] = True
    except Exception:
        pass
    
    # Check Keycloak
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.KEYCLOAK_SERVER_URL}/health/ready",
                timeout=5.0,
            )
            if response.status_code == 200:
                checks["keycloak"] = True
    except Exception:
        pass
    
    if all(checks.values()):
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
        }
    else:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "checks": checks,
            }
        )