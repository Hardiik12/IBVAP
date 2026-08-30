import base64
import numpy as np
import cv2
import pyotp
from fastapi.testclient import TestClient
from app.models.user import User


def generate_test_face_b64() -> str:
    img = np.full((320, 320, 3), 220, dtype=np.uint8)
    cv2.ellipse(img, (160, 160), (70, 95), 0, 0, 360, (180, 150, 130), -1)
    cv2.circle(img, (135, 140), 12, (255, 255, 255), -1)
    cv2.circle(img, (135, 140), 6, (40, 30, 20), -1)
    cv2.circle(img, (185, 140), 12, (255, 255, 255), -1)
    cv2.circle(img, (185, 140), 6, (40, 30, 20), -1)
    cv2.line(img, (160, 150), (160, 175), (140, 110, 90), 3)
    cv2.line(img, (155, 175), (165, 175), (140, 110, 90), 3)
    cv2.ellipse(img, (160, 200), (25, 10), 0, 0, 180, (120, 60, 60), 3)
    _, encoded = cv2.imencode(".jpg", img)
    return "data:image/jpeg;base64," + base64.b64encode(encoded.tobytes()).decode("utf-8")


def test_mfa_full_flow(unauthenticated_client: TestClient) -> None:
    # 1. Step 1 Login with valid credentials
    resp1 = unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "admin",
        "password": "Admin@123",
    })
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["face_verification_required"] is True
    temp_token = data1["temp_token"]

    # 2. Step 2 Face Verification
    face_resp1 = unauthenticated_client.post("/api/v1/auth/face/verify", json={
        "temp_token": temp_token,
        "image": generate_test_face_b64(),
    })
    assert face_resp1.status_code == 200
    mfa_token = face_resp1.json()["mfa_token"]

    # 3. Verify mfa_token cannot access protected endpoints
    prot_resp = unauthenticated_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {mfa_token}"})
    assert prot_resp.status_code == 401

    # 4. Step 3 Setup: Request QR code and TOTP secret
    setup_resp = unauthenticated_client.get(f"/api/v1/auth/mfa/setup?mfa_token={mfa_token}")
    assert setup_resp.status_code == 200
    setup_data = setup_resp.json()
    assert "secret" in setup_data
    assert setup_data["qr_code_base64"].startswith("data:image/png;base64,")
    secret = setup_data["secret"]

    # 5. Step 3 Enable: Try with wrong code -> Should fail
    fail_enable = unauthenticated_client.post("/api/v1/auth/mfa/enable", json={
        "mfa_token": mfa_token,
        "secret": secret,
        "code": "000000",
    })
    assert fail_enable.status_code == 400

    # 6. Step 3 Enable: Generate valid TOTP code using pyotp
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

    # 7. Access protected endpoint with full session access_token
    me_resp = unauthenticated_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "admin"

    # 8. Next Login: Step 1 -> Step 2 Face -> Step 3 MFA Verify
    resp2 = unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "admin",
        "password": "Admin@123",
    })
    assert resp2.status_code == 200
    temp_token2 = resp2.json()["temp_token"]

    face_resp2 = unauthenticated_client.post("/api/v1/auth/face/verify", json={
        "temp_token": temp_token2,
        "image": generate_test_face_b64(),
    })
    assert face_resp2.status_code == 200
    mfa_token2 = face_resp2.json()["mfa_token"]

    # 9. Step 3 Verify: Wrong code
    wrong_verify = unauthenticated_client.post("/api/v1/auth/mfa/verify", json={
        "mfa_token": mfa_token2,
        "code": "999999",
    })
    assert wrong_verify.status_code == 401

    # 10. Step 3 Verify: Correct rotating TOTP code
    current_totp = pyotp.TOTP(secret).now()
    valid_verify = unauthenticated_client.post("/api/v1/auth/mfa/verify", json={
        "mfa_token": mfa_token2,
        "code": current_totp,
    })
    assert valid_verify.status_code == 200
    assert "access_token" in valid_verify.json()

    # 11. Logout
    logout_resp = unauthenticated_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {valid_verify.json()['access_token']}"},
    )
    assert logout_resp.status_code == 200
