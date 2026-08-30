"""Unit tests for M1 Backend EventDispatcher."""

from unittest.mock import MagicMock, patch
import httpx
import pytest

from ai.events.dispatcher import EventDispatcher, DispatchResult
from ai.events.schemas import EventPayload, EventType, Severity


def create_sample_payload() -> EventPayload:
    return EventPayload(
        camera_id="cam-01",
        zone_id="zone-01",
        track_id=42,
        class_name="person",
        confidence=0.92,
        bbox=[100.0, 150.0, 200.0, 350.0],
        event_type=EventType.INTRUSION.value,
        severity=Severity.HIGH.value,
        timestamp="2026-08-30T00:00:00Z",
    )


def test_map_payload_to_event_create():
    dispatcher = EventDispatcher()
    payload = create_sample_payload()

    mapped = dispatcher.map_payload_to_event_create(
        payload=payload,
        camera_id="11111111-1111-1111-1111-111111111111",
        zone_id="22222222-2222-2222-2222-222222222222",
        event_identifier="evt-test-12345",
    )

    assert mapped["event_identifier"] == "evt-test-12345"
    assert mapped["event_type"] == "INTRUSION"
    assert mapped["camera_id"] == "11111111-1111-1111-1111-111111111111"
    assert mapped["zone_id"] == "22222222-2222-2222-2222-222222222222"
    assert mapped["track_id"] == 42
    assert mapped["severity"] == "HIGH"
    assert mapped["status"] == "NEW"
    assert mapped["bounding_box"] == {"x1": 100.0, "y1": 150.0, "x2": 200.0, "y2": 350.0}
    assert mapped["position"] == {"x": 150.0, "y": 350.0}
    assert mapped["metadata"] == {"class_name": "person", "confidence": 0.92}


def test_dispatcher_login_success():
    dispatcher = EventDispatcher(backend_url="http://localhost:8000")
    mock_client = MagicMock(spec=httpx.Client)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "mock-jwt-token-xyz"}
    mock_client.post.return_value = mock_response

    token = dispatcher.login(client=mock_client)
    assert token == "mock-jwt-token-xyz"
    assert dispatcher.is_authenticated() is True
    mock_client.post.assert_called_once_with(
        "http://localhost:8000/api/v1/auth/login",
        json={"username_or_email": dispatcher.username, "password": dispatcher.password},
    )



def test_dispatcher_token_caching():
    dispatcher = EventDispatcher()
    dispatcher._access_token = "existing-cached-token"
    mock_client = MagicMock(spec=httpx.Client)

    headers = dispatcher.get_auth_headers(client=mock_client)
    assert headers["Authorization"] == "Bearer existing-cached-token"
    mock_client.post.assert_not_called()


def test_dispatch_event_success_201():
    dispatcher = EventDispatcher()
    dispatcher._access_token = "valid-token"
    payload = create_sample_payload()

    mock_client = MagicMock(spec=httpx.Client)
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "event-uuid-001", "alert_id": "alert-uuid-001"}
    mock_client.post.return_value = mock_response

    result = dispatcher.dispatch_event(
        payload=payload,
        camera_id="11111111-1111-1111-1111-111111111111",
        client=mock_client,
    )

    assert result.success is True
    assert result.status_code == 201
    assert result.response_data["id"] == "event-uuid-001"
    assert result.attempts == 1


def test_dispatch_event_idempotency_409():
    dispatcher = EventDispatcher()
    dispatcher._access_token = "valid-token"
    payload = create_sample_payload()

    mock_client = MagicMock(spec=httpx.Client)
    mock_response = MagicMock()
    mock_response.status_code = 409
    mock_response.json.return_value = {"detail": "Event identifier already exists"}
    mock_client.post.return_value = mock_response

    result = dispatcher.dispatch_event(
        payload=payload,
        camera_id="11111111-1111-1111-1111-111111111111",
        client=mock_client,
    )

    # 409 is treated as successful idempotency (already recorded)
    assert result.success is True
    assert result.status_code == 409
    assert result.attempts == 1


def test_dispatch_event_reauth_on_401():
    dispatcher = EventDispatcher(max_retries=2)
    dispatcher._access_token = "expired-token"
    payload = create_sample_payload()

    mock_client = MagicMock(spec=httpx.Client)

    # Response 1: 401 Unauthorized
    resp_401 = MagicMock()
    resp_401.status_code = 401

    # Response 2 (login): 200 with new token
    resp_login = MagicMock()
    resp_login.status_code = 200
    resp_login.json.return_value = {"access_token": "fresh-token-456"}

    # Response 3: 201 Created
    resp_201 = MagicMock()
    resp_201.status_code = 201
    resp_201.json.return_value = {"id": "event-uuid-reauth"}

    mock_client.post.side_effect = [resp_401, resp_login, resp_201]

    result = dispatcher.dispatch_event(
        payload=payload,
        camera_id="11111111-1111-1111-1111-111111111111",
        client=mock_client,
    )

    assert result.success is True
    assert result.status_code == 201
    assert dispatcher._access_token == "fresh-token-456"


def test_dispatch_event_bounded_retry_failure():
    dispatcher = EventDispatcher(max_retries=2)
    dispatcher._access_token = "valid-token"
    payload = create_sample_payload()

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.side_effect = httpx.ConnectError("Connection refused")

    result = dispatcher.dispatch_event(
        payload=payload,
        camera_id="11111111-1111-1111-1111-111111111111",
        client=mock_client,
    )

    assert result.success is False
    assert result.attempts == 2
    assert "Connection refused" in (result.error_message or "")


def test_validate_camera_and_zone():
    dispatcher = EventDispatcher()
    dispatcher._access_token = "valid-token"
    mock_client = MagicMock(spec=httpx.Client)

    # Mock camera GET response
    cam_resp = MagicMock()
    cam_resp.status_code = 200
    cam_resp.json.return_value = {"id": "cam-uuid-1", "name": "Camera 1"}

    # Mock zone GET response
    zone_resp = MagicMock()
    zone_resp.status_code = 200
    zone_resp.json.return_value = {
        "id": "zone-uuid-1",
        "name": "Zone A",
        "camera_id": "cam-uuid-1",
        "polygon_coordinates": [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]],
    }

    mock_client.get.side_effect = [cam_resp, zone_resp]

    valid, cam_data, zone_data = dispatcher.validate_camera_and_zone(
        camera_id="cam-uuid-1",
        zone_id="zone-uuid-1",
        client=mock_client,
    )

    assert valid is True
    assert cam_data["id"] == "cam-uuid-1"
    assert zone_data["id"] == "zone-uuid-1"
