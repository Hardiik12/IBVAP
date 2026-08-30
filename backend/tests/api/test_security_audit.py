"""
Automated Security Audit Test Suite for IBVAP Backend.

Tests:
1. Evidence path traversal & directory escape attempts (HTTP 400).
2. In-memory brute force login throttling (5 failed attempts -> HTTP 429).
3. Inactive user authentication denial (HTTP 401).
4. Invalid & malformed JWT Bearer token rejection (HTTP 401).
5. RBAC authorization matrix enforcement across roles.
6. Evidence integrity SHA-256 tamper detection (MISMATCH).
"""

import os
import tempfile
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core import security
from app.models.enums import UserRole
from app.services.evidence_integrity_service import EvidenceIntegrityService
from app.services.auth_service import _failed_login_attempts


def test_path_traversal_blocked(client: TestClient):
    """Verify path traversal patterns are rejected with HTTP 400."""
    with pytest.raises(Exception) as exc_info:
        EvidenceIntegrityService.resolve_path_safely("../../../etc/passwd")
    assert "400" in str(exc_info.value) or "Path traversal" in str(exc_info.value)

    with pytest.raises(Exception) as exc_info:
        EvidenceIntegrityService.resolve_path_safely("/etc/shadow")
    assert "400" in str(exc_info.value)

    with pytest.raises(Exception) as exc_info:
        EvidenceIntegrityService.resolve_path_safely("valid_dir/../../secret.key")
    assert "400" in str(exc_info.value)

    with pytest.raises(Exception) as exc_info:
        EvidenceIntegrityService.resolve_path_safely("nullbyte\0injection.jpg")
    assert "400" in str(exc_info.value)


def test_login_rate_limiting_brute_force_throttling(client: TestClient):
    """Verify after 5 failed login attempts, subsequent attempts return HTTP 429."""
    test_user = f"brute_user_{uuid.uuid4().hex[:6]}"
    _failed_login_attempts.pop(test_user, None)

    # 5 failed attempts -> HTTP 401
    for _ in range(5):
        resp = client.post(
            "/api/v1/auth/login",
            json={"username_or_email": test_user, "password": "WrongPassword123!"},
        )
        assert resp.status_code == 401

    # 6th attempt -> HTTP 429 Too Many Requests
    resp_blocked = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": test_user, "password": "WrongPassword123!"},
    )
    assert resp_blocked.status_code == 429
    assert "Too many failed login attempts" in resp_blocked.text

    # Cleanup
    _failed_login_attempts.pop(test_user, None)


def test_inactive_user_cannot_login(client: TestClient):
    """Verify inactive users receive HTTP 401 upon login attempt."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "inactive_user", "password": "InactiveSecret123!"},
    )
    assert resp.status_code == 401


def test_invalid_jwt_token_rejected(client: TestClient):
    """Verify malformed or invalid JWT tokens return HTTP 401 on protected endpoints."""
    bad_headers = {"Authorization": "Bearer invalid.jwt.token.string"}
    resp = client.get("/api/v1/auth/me", headers=bad_headers)
    assert resp.status_code == 401

    empty_bearer = {"Authorization": "Bearer "}
    resp_empty = client.get("/api/v1/auth/me", headers=empty_bearer)
    assert resp_empty.status_code == 401


def test_rbac_operator_cannot_manage_users(operator_client: TestClient):
    """Verify OPERATOR role is blocked from user administration (HTTP 403)."""
    resp = operator_client.get("/api/v1/users")
    assert resp.status_code == 403


def test_rbac_auditor_cannot_create_cameras(auditor_client: TestClient):
    """Verify AUDITOR role is blocked from mutating camera configurations (HTTP 403)."""
    resp = auditor_client.post(
        "/api/v1/cameras",
        json={
            "name": "Unauthorized Auditor Camera",
            "camera_identifier": f"cam-auditor-{uuid.uuid4().hex[:6]}",
        },
    )
    assert resp.status_code == 403


def test_evidence_tampering_detection(client: TestClient, admin_client: TestClient):
    """Verify modifying physical evidence file bytes produces MISMATCH verification result."""
    # 1. Create camera and event
    cam_resp = admin_client.post(
        "/api/v1/cameras",
        json={"name": "Tamper Test Camera", "camera_identifier": f"cam-tamper-{uuid.uuid4().hex[:6]}"},
    )
    cam_id = cam_resp.json()["id"]

    evt_resp = admin_client.post(
        "/api/v1/events",
        json={
            "event_identifier": f"EVT-TAMPER-{uuid.uuid4().hex[:8]}",
            "event_type": "INTRUSION",
            "camera_id": cam_id,
            "track_id": 1,
            "timestamp": "2026-08-30T00:00:00Z",
            "severity": "HIGH",
            "status": "NEW",
        },
    )
    evt_id = evt_resp.json()["id"]

    # 2. Create physical evidence file inside evidence root
    from pathlib import Path
    from app.core.config import settings
    
    os.makedirs(settings.EVIDENCE_ROOT, exist_ok=True)
    evidence_rel_path = f"tamper_test_{uuid.uuid4().hex[:8]}.jpg"
    target_file = Path(settings.EVIDENCE_ROOT) / evidence_rel_path
    target_file.write_bytes(b"original_authentic_surveillance_snapshot_bytes")

    # 3. Create evidence record
    evi_resp = admin_client.post(
        f"/api/v1/events/{evt_id}/evidence",
        json={
            "evidence_identifier": f"EVI-TAMPER-{uuid.uuid4().hex[:8]}",
            "file_path": evidence_rel_path,
            "captured_at": "2026-08-30T00:00:00Z",
        },
    )
    assert evi_resp.status_code == 201, f"Failed: {evi_resp.text}"
    evi_id = evi_resp.json()["id"]



    # 4. Generate SHA-256 hash
    hash_resp = admin_client.post(f"/api/v1/evidence/{evi_id}/hash")
    assert hash_resp.status_code == 200
    assert hash_resp.json()["status"] == "HASHED"
    original_hash = hash_resp.json()["sha256_hash"]

    # 5. Verify untampered file -> VERIFIED
    verify_resp1 = admin_client.get(f"/api/v1/evidence/{evi_id}/verify")
    assert verify_resp1.status_code == 200
    assert verify_resp1.json()["verified"] is True
    assert verify_resp1.json()["status"] == "VERIFIED"

    # 6. Tamper with file on disk
    target_file.write_bytes(b"tampered_manipulated_pixels_corrupted_data")

    # 7. Re-verify -> MISMATCH
    verify_resp2 = admin_client.get(f"/api/v1/evidence/{evi_id}/verify")
    assert verify_resp2.status_code == 200
    assert verify_resp2.json()["verified"] is False
    assert verify_resp2.json()["status"] == "MISMATCH"
    assert verify_resp2.json()["stored_hash"] == original_hash
    assert verify_resp2.json()["current_hash"] != original_hash

    # Clean up physical test file
    if target_file.exists():
        target_file.unlink()

