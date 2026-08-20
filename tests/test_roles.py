import pytest
from app.models.session import SessionData


def test_session_has_role():
    session = SessionData(
        user_id="123",
        email="test@example.com",
        provider="keycloak",
        access_token="token",
        roles=["admin", "user"],
    )
    assert session.has_role("admin") == True
    assert session.has_role("manager") == False


def test_session_has_any_role():
    session = SessionData(
        user_id="123",
        email="test@example.com",
        provider="keycloak",
        access_token="token",
        roles=["admin"],
    )
    assert session.has_any_role(["admin", "manager"]) == True
    assert session.has_any_role(["manager", "developer"]) == False