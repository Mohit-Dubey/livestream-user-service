import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

MOCK_USER = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "bio": None,
    "is_active": True,
    "is_verified": False,
    "created_at": "2024-01-01T00:00:00",
    "hashed_password": "$2b$12$placeholder",
}


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@patch("app.api.v1.auth.user_service.create_user")
@patch("app.api.v1.auth.publish_user_event")
def test_register(mock_publish, mock_create):
    from app.models.user import User
    from datetime import datetime
    import uuid

    user = MagicMock(spec=User)
    user.id = uuid.UUID(MOCK_USER["id"])
    user.email = MOCK_USER["email"]
    user.username = MOCK_USER["username"]
    user.full_name = MOCK_USER["full_name"]
    user.bio = None
    user.is_active = True
    user.is_verified = False
    user.created_at = datetime(2024, 1, 1)
    mock_create.return_value = user

    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "test@example.com"


@patch("app.api.v1.auth.user_service.authenticate_user")
def test_login(mock_auth):
    from app.models.user import User
    from datetime import datetime
    import uuid

    user = MagicMock(spec=User)
    user.id = uuid.UUID(MOCK_USER["id"])
    user.email = MOCK_USER["email"]
    user.username = MOCK_USER["username"]
    user.full_name = MOCK_USER["full_name"]
    user.bio = None
    user.is_active = True
    user.is_verified = False
    user.created_at = datetime(2024, 1, 1)
    mock_auth.return_value = user

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "securepassword123"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_invalid_body():
    resp = client.post("/api/v1/auth/login", json={"email": "notanemail"})
    assert resp.status_code == 422


def test_get_profile_unauthorized():
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 403
