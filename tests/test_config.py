import pytest
from pydantic import ValidationError


def test_secret_key_required():
    """SECRET_KEY must be set"""
    from app.config import Settings
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(SECRET_KEY="")
    
    assert "SECRET_KEY" in str(exc_info.value)


def test_secret_key_min_length():
    """SECRET_KEY must be 32+ chars"""
    from app.config import Settings
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            SECRET_KEY="short",
            KEYCLOAK_ADMIN_PASSWORD="admin"
        )
    
    assert "at least 32 characters" in str(exc_info.value)


def test_log_level_validation():
    """LOG_LEVEL must be valid"""
    from app.config import Settings
    
    with pytest.raises(ValidationError):
        Settings(
            SECRET_KEY="a" * 32,
            KEYCLOAK_ADMIN_PASSWORD="admin",
            LOG_LEVEL="INVALID"
        )