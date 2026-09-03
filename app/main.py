from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.config import settings
from app.routers import auth, proxy, admin, protected, health
from app.middleware.auth_middleware import AuthMiddleware
from app.services.session_service import SessionService
from app.database import init_db
import logging
import sys

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Application factory"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="High-Performance OAuth2/OIDC Reverse Proxy with Keycloak",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Auth Middleware
    session_service = SessionService()
    app.add_middleware(AuthMiddleware, session_service=session_service)
    
    # Include Routers
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(protected.router)
    app.include_router(proxy.router)
    
    @app.on_event("startup")
    async def startup_event():
        logger.info(f"🚀 Starting {settings.APP_NAME} v1.0.0")
        logger.info(f"🔐 OAuth2 Provider: {settings.OAUTH2_PROVIDER}")
        logger.info(f"🎯 Upstream: {settings.UPSTREAM_URL}")
        logger.info(f"🔑 Keycloak: {settings.KEYCLOAK_SERVER_URL}")
        
        try:
            init_db()
            logger.info("✅ Database initialized")
        except Exception as e:
            logger.error(f"❌ Database init failed: {e}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("👋 Shutting down")
    
    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs" if settings.DEBUG else "/health")
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )