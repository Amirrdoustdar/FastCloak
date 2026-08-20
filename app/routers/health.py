from fastapi import APIRouter
from datetime import datetime
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.APP_NAME,
        "version": "1.0.0",
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Add DB/Redis checks here
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
    }