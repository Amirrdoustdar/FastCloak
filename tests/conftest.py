import pytest
from fastapi.testclient import TestClient
from app.main import create_app  # ✅ FIXED: create_app exists now


@pytest.fixture
def app():
    """Create app"""
    return create_app()


@pytest.fixture
def client(app):
    """Test client"""
    return TestClient(app)


@pytest.fixture
def mock_session():
    """Mock session data"""
    from app.models.session import SessionData
    return SessionData(
        user_id="test-user-id",
        email="test@example.com",
        name="Test User",
        username="testuser",
        provider="keycloak",
        access_token="mock-token",
        roles=["app-user"],
        groups=["/users"],
    )