from fastapi.testclient import TestClient


def test_admin_create_user(admin_client: TestClient) -> None:
    """Test administrator can create a new user."""
    payload = {
        "username": "new_operator",
        "email": "new_operator@ibvap.test",
        "password": "Password123!",
        "role": "OPERATOR"
    }
    response = admin_client.post("/api/v1/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "new_operator"
    assert data["role"] == "OPERATOR"
    assert "password_hash" not in data
    assert "password" not in data


def test_create_user_duplicate_username_fails(admin_client: TestClient) -> None:
    """Test creating user with duplicate username returns 409 Conflict."""
    payload = {
        "username": "admin_user",
        "email": "another_admin@ibvap.test",
        "password": "Password123!",
        "role": "ADMINISTRATOR"
    }
    response = admin_client.post("/api/v1/users", json=payload)
    assert response.status_code == 409


def test_operator_cannot_manage_users(operator_client: TestClient) -> None:
    """Test non-admin (Operator) receives 403 Forbidden when creating or listing users."""
    # List users attempt
    list_resp = operator_client.get("/api/v1/users")
    assert list_resp.status_code == 403

    # Create user attempt
    create_resp = operator_client.post("/api/v1/users", json={
        "username": "forbidden_user",
        "email": "forbidden@ibvap.test",
        "password": "Password123!",
        "role": "OPERATOR"
    })
    assert create_resp.status_code == 403


def test_admin_self_deactivation_protection(admin_client: TestClient) -> None:
    """Test attempting to deactivate the last active administrator returns 400 Bad Request."""
    # admin-uuid-001 is the sole active admin in setup
    payload = {
        "is_active": False
    }
    response = admin_client.patch("/api/v1/users/admin-uuid-001", json=payload)
    assert response.status_code == 400
    assert "last active administrator" in response.json()["error"]["message"].lower()


def test_admin_self_demotion_protection(admin_client: TestClient) -> None:
    """Test attempting to demote the last active administrator returns 400 Bad Request."""
    payload = {
        "role": "OPERATOR"
    }
    response = admin_client.patch("/api/v1/users/admin-uuid-001", json=payload)
    assert response.status_code == 400
    assert "last active administrator" in response.json()["error"]["message"].lower()
