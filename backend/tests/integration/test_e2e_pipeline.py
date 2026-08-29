import os
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy.orm import Session
from app.main import app
from app.core import security
from app.core.config import settings


def test_e2e_full_intrusion_workflow(admin_client: TestClient) -> None:
    """
    Complete end-to-end integration test proving cross-component interaction:
    User Authentication -> Camera Setup -> Zone Setup -> WS Connect -> Event Ingestion ->
    Alert Generation -> WS Notification -> Evidence Snapshot -> SHA-256 Hashing ->
    Verification (VERIFIED) -> Physical File Modification -> Tamper Detection (MISMATCH) ->
    File Restoration -> Re-Verification (VERIFIED) -> Audit Log Verification.
    """
    token = security.create_access_token({"sub": "admin-uuid-001", "username": "admin_user", "role": "ADMINISTRATOR"})

    # 1. Create Camera
    cam_resp = admin_client.post("/api/v1/cameras", json={
        "name": "E2E Integration Camera",
        "camera_identifier": "cam-e2e-pipeline-01",
        "source_type": "RTSP",
        "location": "North Perimeter Gate"
    })
    assert cam_resp.status_code == 201
    camera_id = cam_resp.json()["id"]

    # 2. Create Restricted Zone
    zone_resp = admin_client.post(f"/api/v1/cameras/{camera_id}/zones", json={
        "name": "E2E Restricted Fence",
        "zone_type": "RESTRICTED",
        "polygon": [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]]
    })
    assert zone_resp.status_code == 201
    zone_id = zone_resp.json()["id"]

    # 3. Connect Real-Time WebSocket Client
    with admin_client.websocket_connect(f"/api/v1/ws/events?token={token}") as websocket:

        # 4. Ingest Normalized AI Intrusion Event
        event_payload = {
            "event_identifier": "EV-E2E-FULL-01",
            "event_type": "INTRUSION",
            "camera_id": camera_id,
            "zone_id": zone_id,
            "track_id": 42,
            "timestamp": "2026-08-29T21:00:00Z",
            "severity": "HIGH",
            "status": "NEW",
            "bounding_box": {"x1": 100, "y1": 150, "x2": 200, "y2": 350},
            "position": {"x": 150, "y": 350},
            "metadata": {"pipeline": "e2e_integration_suite", "confidence": 0.98}
        }
        event_resp = admin_client.post("/api/v1/events", json=event_payload)
        assert event_resp.status_code == 201
        event_data = event_resp.json()
        event_id = event_data["id"]
        alert_id = event_data["alert_id"]
        assert alert_id is not None

        # 5. Receive Real-Time WebSocket Notification
        ws_msg = websocket.receive_json()
        assert ws_msg["type"] == "INTRUSION_ALERT"
        assert ws_msg["event"]["event_identifier"] == "EV-E2E-FULL-01"
        assert ws_msg["alert"]["id"] == alert_id
        assert ws_msg["alert"]["status"] == "ACTIVE"

        # 6. Create Digital Evidence Record & Physical Test File
        os.makedirs(settings.EVIDENCE_ROOT, exist_ok=True)
        rel_path = "e2e_test_snapshot_01.jpg"
        full_path = os.path.join(settings.EVIDENCE_ROOT, rel_path)
        original_bytes = b"E2E_BINARY_SNAPSHOT_TEST_PAYLOAD_ORIGINAL"

        with open(full_path, "wb") as f:
            f.write(original_bytes)

        evidence_resp = admin_client.post(f"/api/v1/events/{event_id}/evidence", json={
            "evidence_identifier": "EVD-E2E-01",
            "file_path": rel_path,
            "captured_at": "2026-08-29T21:00:00Z"
        })
        assert evidence_resp.status_code == 201
        evidence_id = evidence_resp.json()["id"]

        # 7. Generate Server-Side Cryptographic SHA-256 Hash
        hash_resp = admin_client.post(f"/api/v1/evidence/{evidence_id}/hash")
        assert hash_resp.status_code == 200
        stored_hash = hash_resp.json()["sha256_hash"]
        assert len(stored_hash) == 64

        # 8. Verify Original Evidence Integrity
        v1_resp = admin_client.get(f"/api/v1/evidence/{evidence_id}/verify")
        assert v1_resp.status_code == 200
        assert v1_resp.json()["status"] == "VERIFIED"
        assert v1_resp.json()["verified"] is True

        # 9. Modify Physical File -> Verify MISMATCH (Tamper Detection)
        with open(full_path, "wb") as f:
            f.write(b"E2E_BINARY_SNAPSHOT_TEST_PAYLOAD_MUTATED_TAMPERED")

        v2_resp = admin_client.get(f"/api/v1/evidence/{evidence_id}/verify")
        assert v2_resp.status_code == 200
        assert v2_resp.json()["status"] == "MISMATCH"
        assert v2_resp.json()["verified"] is False

        # 10. Restore Original File -> Verify VERIFIED
        with open(full_path, "wb") as f:
            f.write(original_bytes)

        v3_resp = admin_client.get(f"/api/v1/evidence/{evidence_id}/verify")
        assert v3_resp.status_code == 200
        assert v3_resp.json()["status"] == "VERIFIED"
        assert v3_resp.json()["verified"] is True

        # 11. Verify Audit Logs
        audit_resp = admin_client.get("/api/v1/audit-logs")
        assert audit_resp.status_code == 200
        actions = [log["action"] for log in audit_resp.json()]
        assert "CAMERA_CREATED" in actions
        assert "ZONE_CREATED" in actions
        assert "EVIDENCE_VERIFIED" in actions

        # Cleanup physical file
        if os.path.exists(full_path):
            os.remove(full_path)


def test_e2e_failure_invalid_camera(admin_client: TestClient) -> None:
    """Test creating an event with non-existent camera ID fails with 404."""
    payload = {
        "event_identifier": "EV-INVALID-CAM",
        "event_type": "INTRUSION",
        "camera_id": "00000000-0000-0000-0000-000000000000",
        "track_id": 1,
        "timestamp": "2026-08-29T21:10:00Z"
    }
    response = admin_client.post("/api/v1/events", json=payload)
    assert response.status_code == 404


def test_e2e_failure_invalid_zone(admin_client: TestClient) -> None:
    """Test creating an event with non-existent zone ID fails with 404."""
    cam_resp = admin_client.post("/api/v1/cameras", json={
        "name": "E2E Cam 2",
        "camera_identifier": "cam-e2e-02"
    })
    cam_id = cam_resp.json()["id"]

    payload = {
        "event_identifier": "EV-INVALID-ZONE",
        "event_type": "INTRUSION",
        "camera_id": cam_id,
        "zone_id": "00000000-0000-0000-0000-000000000000",
        "track_id": 2,
        "timestamp": "2026-08-29T21:15:00Z"
    }
    response = admin_client.post("/api/v1/events", json=payload)
    assert response.status_code == 404


def test_e2e_failure_camera_zone_mismatch(admin_client: TestClient) -> None:
    """Test creating an event with a zone that belongs to a different camera fails with 409 Conflict."""
    cam1_resp = admin_client.post("/api/v1/cameras", json={"name": "Cam A", "camera_identifier": "cam-mismatch-a"})
    cam2_resp = admin_client.post("/api/v1/cameras", json={"name": "Cam B", "camera_identifier": "cam-mismatch-b"})
    cam1_id = cam1_resp.json()["id"]
    cam2_id = cam2_resp.json()["id"]

    zone_resp = admin_client.post(f"/api/v1/cameras/{cam2_id}/zones", json={
        "name": "Zone on Cam B",
        "polygon": [[0.1, 0.1], [0.5, 0.1], [0.5, 0.5], [0.1, 0.5]]
    })
    zone_id = zone_resp.json()["id"]

    # Attempt to pair Cam A with Zone B (belongs to Cam B)
    payload = {
        "event_identifier": "EV-MISMATCH-01",
        "event_type": "INTRUSION",
        "camera_id": cam1_id,
        "zone_id": zone_id,
        "track_id": 3,
        "timestamp": "2026-08-29T21:20:00Z"
    }
    response = admin_client.post("/api/v1/events", json=payload)
    assert response.status_code == 409
    assert "Zone does not belong to camera" in response.json()["error"]["message"]


def test_e2e_failure_duplicate_event_identifier(admin_client: TestClient) -> None:
    """Test submitting duplicate event_identifier fails on second attempt with 409 Conflict."""
    cam_resp = admin_client.post("/api/v1/cameras", json={"name": "Cam Dup", "camera_identifier": "cam-dup-01"})
    cam_id = cam_resp.json()["id"]

    payload = {
        "event_identifier": "EV-DUP-UNIQUE-01",
        "event_type": "INTRUSION",
        "camera_id": cam_id,
        "track_id": 4,
        "timestamp": "2026-08-29T21:25:00Z"
    }

    # First attempt succeeds
    resp1 = admin_client.post("/api/v1/events", json=payload)
    assert resp1.status_code == 201

    # Second attempt fails
    resp2 = admin_client.post("/api/v1/events", json=payload)
    assert resp2.status_code == 409
    assert "already exists" in resp2.json()["error"]["message"]


def test_e2e_failure_unauthorized_client() -> None:
    """Test accessing protected REST event creation endpoint without JWT returns 401 Unauthorized."""
    clean_client = TestClient(app)
    payload = {
        "event_identifier": "EV-UNAUTH-01",
        "event_type": "INTRUSION",
        "camera_id": "00000000-0000-0000-0000-000000000000",
        "track_id": 5,
        "timestamp": "2026-08-29T21:30:00Z"
    }
    response = clean_client.post("/api/v1/events", json=payload)
    assert response.status_code == 401


def test_e2e_rest_and_websocket_consistency(admin_client: TestClient) -> None:
    """Test that REST API query responses match real-time WebSocket broadcast contents."""
    token = security.create_access_token({"sub": "admin-uuid-001", "username": "admin_user", "role": "ADMINISTRATOR"})

    cam_resp = admin_client.post("/api/v1/cameras", json={"name": "Cam Cons", "camera_identifier": "cam-cons-01"})
    cam_id = cam_resp.json()["id"]

    with admin_client.websocket_connect(f"/api/v1/ws/events?token={token}") as websocket:
        event_payload = {
            "event_identifier": "EV-CONSISTENCY-01",
            "event_type": "INTRUSION",
            "camera_id": cam_id,
            "track_id": 88,
            "timestamp": "2026-08-29T21:35:00Z"
        }
        create_resp = admin_client.post("/api/v1/events", json=event_payload)
        assert create_resp.status_code == 201
        event_id = create_resp.json()["id"]
        alert_id = create_resp.json()["alert_id"]

        ws_msg = websocket.receive_json()

        # Fetch via REST
        get_event_resp = admin_client.get(f"/api/v1/events/{event_id}")
        assert get_event_resp.status_code == 200

        get_alert_resp = admin_client.get(f"/api/v1/alerts/{alert_id}")
        assert get_alert_resp.status_code == 200

        # Verify consistency across REST and WebSocket
        assert get_event_resp.json()["event_identifier"] == ws_msg["event"]["event_identifier"]
        assert get_alert_resp.json()["id"] == ws_msg["alert"]["id"]
        assert get_alert_resp.json()["status"] == ws_msg["alert"]["status"]
