import io
import json
import base64
import numpy as np
import cv2
from PIL import Image
import pyotp
from fastapi.testclient import TestClient
from app.core import security


def generate_synthetic_face_jpeg_base64() -> str:
    """
    Generates a realistic synthetic test face image in memory using OpenCV drawing primitives.
    """
    img = np.full((320, 320, 3), 220, dtype=np.uint8)
    # Head contour
    cv2.ellipse(img, (160, 160), (70, 95), 0, 0, 360, (180, 150, 130), -1)
    # Left eye
    cv2.circle(img, (135, 140), 12, (255, 255, 255), -1)
    cv2.circle(img, (135, 140), 6, (40, 30, 20), -1)
    # Right eye
    cv2.circle(img, (185, 140), 12, (255, 255, 255), -1)
    cv2.circle(img, (185, 140), 6, (40, 30, 20), -1)
    # Nose
    cv2.line(img, (160, 150), (160, 175), (140, 110, 90), 3)
    cv2.line(img, (155, 175), (165, 175), (140, 110, 90), 3)
    # Mouth
    cv2.ellipse(img, (160, 200), (25, 10), 0, 0, 180, (120, 60, 60), 3)

    _, encoded = cv2.imencode(".jpg", img)
    return "data:image/jpeg;base64," + base64.b64encode(encoded.tobytes()).decode("utf-8")


def test_face_auth_full_4step_flow(unauthenticated_client: TestClient) -> None:
    # 1. Step 1: Login with credentials
    login_resp = unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "admin",
        "password": "Admin@123",
    })
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["face_verification_required"] is True
    assert "temp_token" in login_data
    temp_token = login_data["temp_token"]

    # 2. Scope Guard: Verify invalid token returns 401
    invalid_token_resp = unauthenticated_client.post("/api/v1/auth/mfa/verify", json={
        "mfa_token": "invalid.jwt.token",
        "code": "123456",
    })
    assert invalid_token_resp.status_code == 401

    # 3. Step 2: MFA Setup / Verification
    setup_resp = unauthenticated_client.get(f"/api/v1/auth/mfa/setup?mfa_token={temp_token}")
    assert setup_resp.status_code == 200
    secret = setup_resp.json()["secret"]

    # Activate MFA
    valid_totp = pyotp.TOTP(secret).now()
    enable_resp = unauthenticated_client.post("/api/v1/auth/mfa/enable", json={
        "mfa_token": temp_token,
        "secret": secret,
        "code": valid_totp,
    })
    assert enable_resp.status_code == 200
    mfa_result = enable_resp.json()
    face_token = mfa_result.get("face_token") or mfa_result.get("access_token")

    # 4. Step 3: Face Verification
    test_face_b64 = generate_synthetic_face_jpeg_base64()
    face_resp = unauthenticated_client.post("/api/v1/auth/face/verify", json={
        "temp_token": face_token,
        "image": test_face_b64,
        "liveness_completed": True,
    })
    assert face_resp.status_code == 200
    face_data = face_resp.json()
    assert face_data["verified"] is True
    assert "access_token" in face_data
    access_token = face_data["access_token"]

    # 5. Step 4: Access Protected Route
    me_resp = unauthenticated_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "admin"


def test_face_enrollment_endpoint(unauthenticated_client: TestClient) -> None:
    # Login
    login_resp = unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "admin",
        "password": "Admin@123",
    })
    temp_token = login_resp.json()["temp_token"]

    # Enroll with 3 synthetic samples
    samples = [generate_synthetic_face_jpeg_base64() for _ in range(3)]
    enroll_resp = unauthenticated_client.post("/api/v1/auth/face/enroll", json={
        "temp_token": temp_token,
        "images": samples,
    })
    assert enroll_resp.status_code == 200
    enroll_data = enroll_resp.json()
    assert enroll_data["enrolled"] is True
    assert enroll_data["samples_processed"] >= 1
