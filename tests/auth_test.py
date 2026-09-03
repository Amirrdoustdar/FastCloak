import pytest


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login_redirects(client):
    response = client.get("/auth/login", follow_redirects=False)
    assert response.status_code in [302, 307]


def test_me_unauthenticated(client):
    response = client.get("/auth/me")
    assert response.status_code in [401, 302, 307]