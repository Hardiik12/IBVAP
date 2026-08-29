from datetime import timedelta
from fastapi.testclient import TestClient
from app.core import security


def test_login_with_username_success(unauthenticated_client: TestClient) -> None:
    """Test login with valid username credentials returns MFA challenge token."""
    response = unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "admin_user",
        "password": "AdminSecret123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["mfa_required"] is True
    assert "mfa_token" in data
    assert data["temp_token_expires_in"] == 300


def test_login_with_email_success(unauthenticated_client: TestClient) -> None:
    """Test login with valid email credentials returns MFA challenge token."""
    response = unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "admin@ibvap.test",
        "password": "AdminSecret123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["mfa_required"] is True
    assert "mfa_token" in data


def test_login_invalid_password(unauthenticated_client: TestClient) -> None:
    """Test login with incorrect password returns generic 401 error."""
    response = unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "admin_user",
        "password": "WrongPassword123!"
    })
    assert response.status_code == 401
    assert "Invalid operator credentials" in response.json()["error"]["message"]


def test_login_unknown_user(unauthenticated_client: TestClient) -> None:
    """Test login with non-existent username returns generic 401 error."""
    response = unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "nonexistent_user",
        "password": "SomePassword123!"
    })
    assert response.status_code == 401
    assert "Invalid operator credentials" in response.json()["error"]["message"]


def test_login_inactive_user(unauthenticated_client: TestClient) -> None:
    """Test login with inactive user returns generic 401 error."""
    response = unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "inactive_user",
        "password": "InactiveSecret123!"
    })
    assert response.status_code == 401
    assert "Invalid operator credentials" in response.json()["error"]["message"]


def test_get_current_user_profile(admin_client: TestClient) -> None:
    """Test GET /api/v1/auth/me returns current user without password hash."""
    response = admin_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin_user"
    assert data["role"] == "ADMINISTRATOR"
    assert "password_hash" not in data


def test_unauthenticated_request_rejected(unauthenticated_client: TestClient) -> None:
    """Test accessing protected route without token returns 401."""
    # Temporarily remove header
    unauthenticated_client.headers.pop("Authorization", None)
    response = unauthenticated_client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_expired_token_rejected(unauthenticated_client: TestClient) -> None:
    """Test accessing protected route with an expired token returns 401."""
    expired_token = security.create_access_token(
        {"sub": "admin-uuid-001", "username": "admin_user", "scope": "fully_authenticated"},
        expires_delta=timedelta(seconds=-10)
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = unauthenticated_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


def test_invalid_signature_token_rejected(unauthenticated_client: TestClient) -> None:
    """Test accessing protected route with invalid token signature returns 401."""
    invalid_token = security.create_access_token({"sub": "admin-uuid-001", "scope": "fully_authenticated"}) + "tampered"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = unauthenticated_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
