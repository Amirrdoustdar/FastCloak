from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application Settings"""
    
    # App
    APP_NAME: str = "OAuth2 Proxy"
    DEBUG: bool = False
    SECRET_KEY: str
    LOG_LEVEL: str = "INFO"
    
    # OAuth2 Provider
    OAUTH2_PROVIDER: str = "keycloak"
    
    # Keycloak
    KEYCLOAK_SERVER_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "my-realm"
    KEYCLOAK_CLIENT_ID: str = "oauth2-proxy"
    KEYCLOAK_CLIENT_SECRET: str = ""
    KEYCLOAK_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    KEYCLOAK_VERIFY_SSL: bool = True
    
    # Keycloak Admin
    KEYCLOAK_ADMIN_USERNAME: str = "admin"
    KEYCLOAK_ADMIN_PASSWORD: str = "admin"
    
    # Access Control
    REQUIRED_ROLES: List[str] = []
    REQUIRED_GROUPS: List[str] = []
    
    # Google OAuth2
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    
    # GitHub OAuth2
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    
    # JWT
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    SESSION_EXPIRE_SECONDS: int = 3600
    
    # Database
    DATABASE_URL: str = "sqlite:///./oauth2_proxy.db"
    
    # Upstream
    UPSTREAM_URL: str = "http://localhost:9000"
    
    # Access Control
    ALLOWED_DOMAINS: List[str] = []
    ALLOWED_EMAILS: List[str] = []
    
    # Cookie
    COOKIE_NAME: str = "_oauth2_proxy"
    COOKIE_SECURE: bool = False
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()