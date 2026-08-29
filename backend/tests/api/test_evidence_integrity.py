import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.core.config import settings
from app.services.evidence_integrity_service import EvidenceIntegrityService


@pytest.fixture(autouse=True)
def configure_test_evidence_root(tmp_path):
    """
    Override the configured EVIDENCE_ROOT settings to point to a temporary test directory
    to ensure isolation and prevent path traversal outside of the test sandbox.
    """
    old_root = settings.EVIDENCE_ROOT
    settings.EVIDENCE_ROOT = str(tmp_path)
    yield
    settings.EVIDENCE_ROOT = old_root


# ==============================================================================
# UNIT TESTS FOR INTEGRITY SERVICE
# ==============================================================================

def test_calculate_sha256_known_vector():
    """Unit Test 1: Calculate SHA-256 against a known test vector."""
    test_file = Path(settings.EVIDENCE_ROOT) / "vector.txt"
    test_file.write_bytes(b"hello world")
    
    expected_hash = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    computed_hash = EvidenceIntegrityService.calculate_sha256(test_file)
    assert computed_hash == expected_hash


def test_calculate_sha256_empty_file():
    """Unit Test 2: Calculate SHA-256 for an empty file."""
    test_file = Path(settings.EVIDENCE_ROOT) / "empty.txt"
    test_file.touch()
    
    expected_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    computed_hash = EvidenceIntegrityService.calculate_sha256(test_file)
    assert computed_hash == expected_hash


def test_calculate_sha256_large_chunked():
    """Unit Test 3: Hashing works correctly on larger inputs using chunked reading."""
    test_file = Path(settings.EVIDENCE_ROOT) / "large.bin"
    # Write exactly 128KB of mock binary data
    large_data = b"\x00\xff" * 65536
    test_file.write_bytes(large_data)
    
    import hashlib
    ref_hash = hashlib.sha256(large_data).hexdigest().lower()
    computed_hash = EvidenceIntegrityService.calculate_sha256(test_file)
    assert computed_hash == ref_hash


def test_path_traversal_detection():
    """Unit Test 4: Path traversal attempts outside EVIDENCE_ROOT are rejected."""
    # Attempt absolute path outside the root
    with pytest.raises(Exception) as excinfo:
        EvidenceIntegrityService.resolve_path_safely("/etc/passwd")
    assert "Path traversal attempt detected" in str(excinfo.value.detail)

    # Attempt relative path climbing outside the root
    with pytest.raises(Exception) as excinfo2:
        EvidenceIntegrityService.resolve_path_safely("../outside.txt")
    assert "Path traversal attempt detected" in str(excinfo2.value.detail)


# ==============================================================================
# API TESTS FOR HASH & VERIFICATION ENDPOINTS
# ==============================================================================

def test_hash_lifecycle_endpoints(client: TestClient) -> None:
    """
    API Tests: Covers hashing, verification, missing file errors, and modification checks.
    """
    # 1. Create camera and event
    cam = client.post("/api/v1/cameras", json={"name": "Int Camera", "camera_identifier": "cam-int-hash"}).json()["id"]
    evt = client.post("/api/v1/events", json={
        "event_identifier": "EV-INT-HASH",
        "event_type": "INTRUSION",
        "camera_id": cam,
        "track_id": 5,
        "timestamp": "2026-08-29T18:00:00Z"
    }).json()["id"]

    # 2. Create Evidence (Metadata only)
    evi = client.post(f"/api/v1/events/{evt}/evidence", json={
        "evidence_identifier": "EVD-INT-HASH",
        "file_path": "int_frame.jpg",
        "captured_at": "2026-08-29T18:00:05Z"
    }).json()
    evidence_id = evi["id"]

    # 3. Verify NOT_HASHED status initially
    verify_resp = client.get(f"/api/v1/evidence/{evidence_id}/verify")
    assert verify_resp.status_code == 200
    assert verify_resp.json()["status"] == "NOT_HASHED"
    assert verify_resp.json()["verified"] is False

    # 4. Generate hash before file is written on disk (returns 404 Missing File)
    hash_resp_fail = client.post(f"/api/v1/evidence/{evidence_id}/hash")
    assert hash_resp_fail.status_code == 404
    assert "file not found" in hash_resp_fail.json()["error"]["message"].lower()

    # 5. Write the physical file
    target_file = Path(settings.EVIDENCE_ROOT) / "int_frame.jpg"
    original_content = b"intrusion_snapshot_data_binary"
    target_file.write_bytes(original_content)

    # 6. Generate SHA-256 successfully (returns 200 Hashed)
    hash_resp = client.post(f"/api/v1/evidence/{evidence_id}/hash")
    assert hash_resp.status_code == 200
    data = hash_resp.json()
    assert data["status"] == "HASHED"
    stored_hash = data["sha256_hash"]
    assert len(stored_hash) == 64

    # 7. Check Hash Idempotency (does not overwrite existing hash)
    hash_resp_dup = client.post(f"/api/v1/evidence/{evidence_id}/hash")
    assert hash_resp_dup.status_code == 200
    assert hash_resp_dup.json()["status"] == "ALREADY_HASHED"
    assert hash_resp_dup.json()["sha256_hash"] == stored_hash

    # 8. Verify the evidence (returns VERIFIED)
    verify_resp_2 = client.get(f"/api/v1/evidence/{evidence_id}/verify")
    assert verify_resp_2.status_code == 200
    assert verify_resp_2.json()["status"] == "VERIFIED"
    assert verify_resp_2.json()["verified"] is True
    assert verify_resp_2.json()["stored_hash"] == stored_hash
    assert verify_resp_2.json()["current_hash"] == stored_hash

    # 9. Modify the physical file
    target_file.write_bytes(b"tampered_snapshot_data_binary")

    # 10. Verify again (returns MISMATCH)
    verify_resp_3 = client.get(f"/api/v1/evidence/{evidence_id}/verify")
    assert verify_resp_3.status_code == 200
    assert verify_resp_3.json()["status"] == "MISMATCH"
    assert verify_resp_3.json()["verified"] is False
    assert verify_resp_3.json()["stored_hash"] == stored_hash
    assert verify_resp_3.json()["current_hash"] != stored_hash

    # 11. Restore the original content
    target_file.write_bytes(original_content)

    # 12. Verify again (returns VERIFIED)
    verify_resp_4 = client.get(f"/api/v1/evidence/{evidence_id}/verify")
    assert verify_resp_4.status_code == 200
    assert verify_resp_4.json()["status"] == "VERIFIED"
    assert verify_resp_4.json()["verified"] is True

    # 13. Delete physical file and verify (returns 404 File Not Found)
    target_file.unlink()
    verify_resp_fail = client.get(f"/api/v1/evidence/{evidence_id}/verify")
    assert verify_resp_fail.status_code == 404


def test_hash_missing_evidence_raises_404(client: TestClient) -> None:
    """API Test: Generating hash or verifying for nonexistent evidence ID raises 404."""
    response = client.post("/api/v1/evidence/00000000-0000-0000-0000-000000000000/hash")
    assert response.status_code == 404

    response_v = client.get("/api/v1/evidence/00000000-0000-0000-0000-000000000000/verify")
    assert response_v.status_code == 404


def test_hash_cannot_be_client_controlled(client: TestClient) -> None:
    """API Test: Client cannot submit sha256_hash on creation or update."""
    cam = client.post("/api/v1/cameras", json={"name": "Int Cam 3", "camera_identifier": "cam-lock"}).json()["id"]
    evt = client.post("/api/v1/events", json={
        "event_identifier": "EV-LOCK",
        "event_type": "EXIT",
        "camera_id": cam,
        "track_id": 10,
        "timestamp": "2026-08-29T18:00:00Z"
    }).json()["id"]

    # Try creating with sha256_hash payload parameter (ignored/rejected)
    payload = {
        "evidence_identifier": "EVD-LOCK",
        "file_path": "frame_lock.jpg",
        "captured_at": "2026-08-29T18:00:05Z",
        "sha256_hash": "a"*64  # Client attempt
    }
    response = client.post(f"/api/v1/events/{evt}/evidence", json=payload)
    # The client-submitted hash is ignored/not saved
    assert response.status_code == 201
    assert response.json()["sha256_hash"] is None  # Saved as NULL

    evidence_id = response.json()["id"]

    # Try updating sha256_hash (rejected with 422)
    update_payload = {
        "sha256_hash": "b"*64
    }
    response_update = client.patch(f"/api/v1/evidence/{evidence_id}", json=update_payload)
    assert response_update.status_code == 422
