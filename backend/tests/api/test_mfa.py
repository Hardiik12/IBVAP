import pyotp
from fastapi.testclient import TestClient
from app.models.user import User


def test_mfa_full_flow(unauthenticated_client: TestClient) -> None:
    # 1. Step 1 Login with valid credentials
    resp1 = unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "admin",
        "password": "Admin@123",
    })
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["mfa_required"] is True
    assert "mfa_token" in data1
    mfa_token = data1["mfa_token"]

    # 2. Verify mfa_token cannot access protected endpoints
    prot_resp = unauthenticated_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {mfa_token}"})
    assert prot_resp.status_code == 401
    assert "MFA verification required" in prot_resp.json()["error"]["message"]

    # 3. Step 2 Setup: Request QR code and TOTP secret
    setup_resp = unauthenticated_client.get(f"/api/v1/auth/mfa/setup?mfa_token={mfa_token}")
    assert setup_resp.status_code == 200
    setup_data = setup_resp.json()
    assert "secret" in setup_data
    assert setup_data["qr_code_base64"].startswith("data:image/png;base64,")
    secret = setup_data["secret"]

    # 4. Step 2 Enable: Try with wrong code -> Should fail
    fail_enable = unauthenticated_client.post("/api/v1/auth/mfa/enable", json={
        "mfa_token": mfa_token,
        "secret": secret,
        "code": "000000",
    })
    assert fail_enable.status_code == 400

    # 5. Step 2 Enable: Generate valid TOTP code using pyotp
    valid_code = pyotp.TOTP(secret).now()
    success_enable = unauthenticated_client.post("/api/v1/auth/mfa/enable", json={
        "mfa_token": mfa_token,
        "secret": secret,
        "code": valid_code,
    })
    assert success_enable.status_code == 200
    session_data = success_enable.json()
    assert "access_token" in session_data
    access_token = session_data["access_token"]
    assert session_data["user"]["mfa_enabled"] is True

    # 6. Access protected endpoint with full session access_token
    me_resp = unauthenticated_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "admin"

    # 7. Next Login: MFA is now enabled -> Step 1 returns mfa_setup_required=False
    resp2 = unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "admin",
        "password": "Admin@123",
    })
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["mfa_setup_required"] is False
    mfa_token2 = data2["mfa_token"]

    # 8. Step 2 Verify: Wrong code
    wrong_verify = unauthenticated_client.post("/api/v1/auth/mfa/verify", json={
        "mfa_token": mfa_token2,
        "code": "999999",
    })
    assert wrong_verify.status_code == 401

    # 9. Step 2 Verify: Correct rotating TOTP code
    current_totp = pyotp.TOTP(secret).now()
    valid_verify = unauthenticated_client.post("/api/v1/auth/mfa/verify", json={
        "mfa_token": mfa_token2,
        "code": current_totp,
    })
    assert valid_verify.status_code == 200
    assert "access_token" in valid_verify.json()

    # 10. Logout
    logout_resp = unauthenticated_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {valid_verify.json()['access_token']}"},
    )
    assert logout_resp.status_code == 200
