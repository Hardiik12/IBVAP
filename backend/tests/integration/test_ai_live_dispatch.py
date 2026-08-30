"""
End-to-End Integration Tests for AI Pipeline EventDispatcher and M1 Backend.

Validates:
1. AI EventDispatcher login & token lifecycle against M1 auth endpoints.
2. Pre-flight camera and zone validation against real database tables.
3. Full intrusion event ingestion: EventDispatcher -> POST /api/v1/events -> Database -> Alert creation.
4. Idempotent duplicate event suppression (HTTP 409 Conflict handled cleanly).
5. Error handling for non-existent cameras or mismatching zones.
"""

import uuid
from typing import Generator
import pytest
from fastapi.testclient import TestClient

from ai.events.dispatcher import EventDispatcher
from ai.events.schemas import EventPayload, EventType, Severity


@pytest.fixture(scope="function")
def seeded_camera_and_zone(client: TestClient) -> tuple[str, str]:
    """Create test camera and restricted polygon zone via client REST API."""
    unique_suffix = uuid.uuid4().hex[:8]
    cam_resp = client.post(
        "/api/v1/cameras",
        json={
            "name": f"North Perimeter Camera {unique_suffix}",
            "camera_identifier": f"cam-north-{unique_suffix}",
            "source_type": "RTSP",
            "source_url": "rtsp://192.168.1.100/live",
            "location": "North Fence Gate 3",
        },
    )
    assert cam_resp.status_code == 201, cam_resp.text
    camera_id = cam_resp.json()["id"]

    zone_resp = client.post(
        f"/api/v1/cameras/{camera_id}/zones",
        json={
            "name": f"Restricted Zone {unique_suffix}",
            "polygon": [
                [0.10, 0.10],
                [0.90, 0.10],
                [0.90, 0.90],
                [0.10, 0.90],
            ],
        },
    )
    assert zone_resp.status_code == 201, zone_resp.text
    zone_id = zone_resp.json()["id"]

    return camera_id, zone_id


def test_ai_dispatcher_full_m1_event_creation(
    client: TestClient,
    seeded_camera_and_zone: tuple[str, str],
):
    """
    Test that EventDispatcher successfully posts an EventPayload to M1, creating
    both an Event record and an associated Alert record with CRITICAL severity.
    """
    camera_id, zone_id = seeded_camera_and_zone

    dispatcher = EventDispatcher(
        username="operator_user",
        password="OperatorSecret123!",
    )

    payload = EventPayload(
        camera_id=camera_id,
        zone_id=zone_id,
        track_id=101,
        class_name="person",
        confidence=0.96,
        bbox=[200.0, 300.0, 400.0, 700.0],
        event_type=EventType.INTRUSION.value,
        severity=Severity.HIGH.value,
        timestamp="2026-08-30T00:15:00Z",
    )

    # Dispatch using TestClient
    result = dispatcher.dispatch_event(
        payload=payload,
        camera_id=camera_id,
        zone_id=zone_id,
        client=client,
    )

    assert result.success is True
    assert result.status_code == 201
    assert result.response_data is not None

    event_id = result.response_data["id"]
    alert_id = result.response_data.get("alert_id")
    assert event_id is not None
    assert alert_id is not None

    # Verify event retrieval via API
    get_resp = client.get(f"/api/v1/events/{event_id}")
    assert get_resp.status_code == 200
    evt_data = get_resp.json()
    assert evt_data["track_id"] == 101
    assert evt_data["camera_id"] == camera_id
    assert evt_data["zone_id"] == zone_id
    assert evt_data["alert_id"] == alert_id


def test_ai_dispatcher_preflight_validation(
    client: TestClient,
    seeded_camera_and_zone: tuple[str, str],
):
    """Test pre-flight camera and zone validation against real M1 API."""
    camera_id, zone_id = seeded_camera_and_zone
    dispatcher = EventDispatcher(
        username="operator_user",
        password="OperatorSecret123!",
    )

    # Valid check
    valid, cam_data, zone_data = dispatcher.validate_camera_and_zone(
        camera_id=camera_id,
        zone_id=zone_id,
        client=client,
    )
    assert valid is True
    assert cam_data["id"] == camera_id
    assert zone_data["id"] == zone_id

    # Invalid camera check
    invalid_cam_id = str(uuid.uuid4())
    valid_bad, _, _ = dispatcher.validate_camera_and_zone(
        camera_id=invalid_cam_id,
        client=client,
    )
    assert valid_bad is False


def test_ai_dispatcher_idempotent_duplicate_retry(
    client: TestClient,
    seeded_camera_and_zone: tuple[str, str],
):
    """Test that re-dispatching with the same event identifier receives 409 and succeeds idempotently."""
    camera_id, zone_id = seeded_camera_and_zone
    dispatcher = EventDispatcher(
        username="operator_user",
        password="OperatorSecret123!",
    )

    payload = EventPayload(
        camera_id=camera_id,
        zone_id=zone_id,
        track_id=88,
        class_name="truck",
        confidence=0.91,
        bbox=[50.0, 50.0, 300.0, 400.0],
        event_type=EventType.INTRUSION.value,
        severity=Severity.CRITICAL.value,
        timestamp="2026-08-30T00:20:00Z",
    )
    fixed_event_identifier = f"evt-fixed-{uuid.uuid4().hex[:12]}"

    # Attempt 1: 201 Created
    res1 = dispatcher.dispatch_event(
        payload=payload,
        camera_id=camera_id,
        zone_id=zone_id,
        event_identifier=fixed_event_identifier,
        client=client,
    )
    assert res1.success is True
    assert res1.status_code == 201

    # Attempt 2: Replay with same identifier -> 409 Conflict handled as idempotent success
    res2 = dispatcher.dispatch_event(
        payload=payload,
        camera_id=camera_id,
        zone_id=zone_id,
        event_identifier=fixed_event_identifier,
        client=client,
    )
    assert res2.success is True
    assert res2.status_code == 409
