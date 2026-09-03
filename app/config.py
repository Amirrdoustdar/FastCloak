from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
from typing import List, Optional
from functools import lru_cache
import secrets
import warnings


class Settings(BaseSettings):
    """Application Settings with Validation"""
    
    # App
    APP_NAME: str = "FastCloak"
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
    KEYCLOAK_ADMIN_PASSWORD: str
    
    # Access Control
    REQUIRED_ROLES: List[str] = ["app-user"]
    REQUIRED_GROUPS: List[str] = []
    
    # JWT
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    SESSION_EXPIRE_SECONDS: int = 3600
    
    # Database
    DATABASE_URL: str = "sqlite:///./oauth2_proxy.db"
    
    # Upstream
    UPSTREAM_URL: str = "http://localhost:9000"
    
    # Access Control
    ALLOWED_DOMAINS: List[str] = []
    ALLOWED_EMAILS: List[str] = []
    
    # Cookie
    COOKIE_NAME: str = "_fastcloak"
    COOKIE_SECURE: bool = False
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v:
            raise ValueError("SECRET_KEY is required")
        if len(v) < 32:
            raise ValueError(f"SECRET_KEY must be at least 32 characters (got {len(v)})")
        
        weak_keys = [
            "REPLACE_WITH_OUTPUT_FROM_GENERATE_SECRET_SCRIPT",
            "change-this",
            "changeme",
            "secret" * 6,
        ]
        
        if any(weak in v for weak in weak_keys):
            raise ValueError(
                "SECRET_KEY contains weak/default value. "
                "Generate a strong key with: python scripts/generate_secret.py"
            )
        
        return v
    
    @field_validator("KEYCLOAK_ADMIN_PASSWORD")
    @classmethod
    def validate_admin_password(cls, v: str) -> str:
        if not v:
            raise ValueError("KEYCLOAK_ADMIN_PASSWORD is required")
        
        if v in ["admin", "CHANGE_ME_IN_PRODUCTION"]:
            warnings.warn(
                f"⚠️  KEYCLOAK_ADMIN_PASSWORD is weak: '{v}'. Change it for production!",
                UserWarning,
                stacklevel=2
            )
        
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid:
            raise ValueError(f"LOG_LEVEL must be one of {valid}")
        return v.upper()
    
    @field_validator("OAUTH2_PROVIDER")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        valid = ["keycloak"]
        if v.lower() not in valid:
            raise ValueError(f"OAUTH2_PROVIDER must be one of {valid}")
        return v.lower()
    
    @model_validator(mode='after')
    def validate_production_security(self):
        if not self.DEBUG:
            warnings_list = []
            
            if not self.COOKIE_SECURE:
                warnings_list.append("COOKIE_SECURE is False (cookies sent over HTTP)")
            
            if not self.KEYCLOAK_VERIFY_SSL:
                warnings_list.append("KEYCLOAK_VERIFY_SSL is False (SSL not verified)")
            
            if "localhost" in self.KEYCLOAK_SERVER_URL:
                warnings_list.append("KEYCLOAK_SERVER_URL uses localhost")
            
            if warnings_list:
                msg = "\n🔒 PRODUCTION SECURITY WARNINGS:\n" + "\n".join(f"  ⚠️  {w}" for w in warnings_list)
                warnings.warn(msg, UserWarning, stacklevel=2)
        
        return self
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def generate_secret_key(length: int = 32) -> str:
    """Generate cryptographically secure secret key"""
    return secrets.token_urlsafe(length)