from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy.orm import Session
from app.core import security
from app.services.event_service import EventService
from app.schemas.event import EventCreate
from app.models.enums import EventType, EventSeverity, EventStatus


def test_websocket_authenticated_connection_success(unauthenticated_client: TestClient) -> None:
    """Test connection with valid token parameter succeeds."""
    token = security.create_access_token({"sub": "admin-uuid-001", "username": "admin_user", "role": "ADMINISTRATOR"})
    with unauthenticated_client.websocket_connect(f"/api/v1/ws/events?token={token}") as websocket:
        assert websocket is not None


def test_websocket_missing_token_rejected(unauthenticated_client: TestClient) -> None:
    """Test connection without token is rejected with 1008 close code."""
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with unauthenticated_client.websocket_connect("/api/v1/ws/events"):
            pass
    assert exc_info.value.code == 1008


def test_websocket_invalid_token_rejected(unauthenticated_client: TestClient) -> None:
    """Test connection with invalid token is rejected with 1008 close code."""
    invalid_token = "invalid.jwt.token"
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with unauthenticated_client.websocket_connect(f"/api/v1/ws/events?token={invalid_token}"):
            pass
    assert exc_info.value.code == 1008


def test_websocket_expired_token_rejected(unauthenticated_client: TestClient) -> None:
    """Test connection with expired token is rejected with 1008 close code."""
    expired_token = security.create_access_token(
        {"sub": "admin-uuid-001", "username": "admin_user"},
        expires_delta=timedelta(seconds=-10)
    )
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with unauthenticated_client.websocket_connect(f"/api/v1/ws/events?token={expired_token}"):
            pass
    assert exc_info.value.code == 1008


def test_websocket_inactive_user_rejected(unauthenticated_client: TestClient) -> None:
    """Test connection for an inactive user is rejected with 1008 close code."""
    inactive_token = security.create_access_token(
        {"sub": "inactive-uuid-001", "username": "inactive_user", "role": "OPERATOR"}
    )
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with unauthenticated_client.websocket_connect(f"/api/v1/ws/events?token={inactive_token}"):
            pass
    assert exc_info.value.code == 1008


def test_websocket_intrusion_broadcast(admin_client: TestClient) -> None:
    """
    Test creating an INTRUSION event via REST API broadcasts a coherent real-time JSON payload
    containing both event and alert parameters to a connected WebSocket client.
    """
    token = security.create_access_token({"sub": "operator-uuid-001", "username": "operator_user", "role": "OPERATOR"})
    
    # 1. Create a camera feed for testing
    cam_resp = admin_client.post("/api/v1/cameras", json={
        "name": "WS Test Camera",
        "camera_identifier": "cam-ws-test-01"
    })
    cam_id = cam_resp.json()["id"]

    # 2. Connect WebSocket client
    with admin_client.websocket_connect(f"/api/v1/ws/events?token={token}") as websocket:
        # 3. Ingest INTRUSION event via REST API
        event_payload = {
            "event_identifier": "EV-WS-INTRUSION-01",
            "event_type": "INTRUSION",
            "camera_id": cam_id,
            "track_id": 99,
            "timestamp": "2026-08-29T20:00:00Z",
            "severity": "HIGH",
            "status": "NEW"
        }
        create_resp = admin_client.post("/api/v1/events", json=event_payload)
        assert create_resp.status_code == 201

        # 4. Receive real-time WebSocket notification message
        msg = websocket.receive_json()
        assert msg["type"] == "INTRUSION_ALERT"
        assert msg["event"]["event_identifier"] == "EV-WS-INTRUSION-01"
        assert msg["event"]["event_type"] == "INTRUSION"
        assert msg["alert"] is not None
        assert msg["alert"]["status"] == "ACTIVE"


def test_websocket_multi_client_broadcast(admin_client: TestClient) -> None:
    """Test broadcasting sends real-time notifications to multiple connected clients."""
    token1 = security.create_access_token({"sub": "admin-uuid-001", "username": "admin_user", "role": "ADMINISTRATOR"})
    token2 = security.create_access_token({"sub": "operator-uuid-001", "username": "operator_user", "role": "OPERATOR"})

    cam_resp = admin_client.post("/api/v1/cameras", json={
        "name": "WS Multi Camera",
        "camera_identifier": "cam-ws-multi-01"
    })
    cam_id = cam_resp.json()["id"]

    with admin_client.websocket_connect(f"/api/v1/ws/events?token={token1}") as ws1:
        with admin_client.websocket_connect(f"/api/v1/ws/events?token={token2}") as ws2:
            event_payload = {
                "event_identifier": "EV-WS-MULTI-01",
                "event_type": "INTRUSION",
                "camera_id": cam_id,
                "track_id": 101,
                "timestamp": "2026-08-29T20:05:00Z"
            }
            create_resp = admin_client.post("/api/v1/events", json=event_payload)
            assert create_resp.status_code == 201

            msg1 = ws1.receive_json()
            msg2 = ws2.receive_json()

            assert msg1["event"]["event_identifier"] == "EV-WS-MULTI-01"
            assert msg2["event"]["event_identifier"] == "EV-WS-MULTI-01"


def test_websocket_uncommitted_transaction_no_broadcast(admin_client: TestClient) -> None:
    """
    Test that if an event transaction fails or rolls back, no WebSocket message is dispatched.
    """
    token = security.create_access_token({"sub": "admin-uuid-001", "username": "admin_user", "role": "ADMINISTRATOR"})

    # Create invalid event request (non-existent 36-char camera UUID)
    event_payload = {
        "event_identifier": "EV-FAILED-01",
        "event_type": "INTRUSION",
        "camera_id": "00000000-0000-0000-0000-000000000000",
        "track_id": 12,
        "timestamp": "2026-08-29T20:10:00Z"
    }

    with admin_client.websocket_connect(f"/api/v1/ws/events?token={token}") as websocket:
        # Post invalid event
        response = admin_client.post("/api/v1/events", json=event_payload)
        assert response.status_code == 404

        # Verify that creating a subsequent valid event arrives cleanly as the next message
        cam_resp = admin_client.post("/api/v1/cameras", json={
            "name": "WS Recovery Camera",
            "camera_identifier": "cam-ws-rec-01"
        })
        cam_id = cam_resp.json()["id"]

        valid_payload = {
            "event_identifier": "EV-VALID-AFTER-FAILURE",
            "event_type": "INTRUSION",
            "camera_id": cam_id,
            "track_id": 13,
            "timestamp": "2026-08-29T20:11:00Z"
        }
        valid_resp = admin_client.post("/api/v1/events", json=valid_payload)
        assert valid_resp.status_code == 201

        msg = websocket.receive_json()
        assert msg["event"]["event_identifier"] == "EV-VALID-AFTER-FAILURE"
