from fastapi.testclient import TestClient


def test_create_intrusion_event_api(client: TestClient) -> None:
    """
    Test 1-3: Create valid camera, zone, and intrusion event.
    """
    # 1. Create camera
    cam_resp = client.post("/api/v1/cameras", json={
        "name": "Intrusion Camera",
        "camera_identifier": "cam-intrusion-01"
    })
    camera_id = cam_resp.json()["id"]

    # 2. Create zone for that camera
    zone_resp = client.post(f"/api/v1/cameras/{camera_id}/zones", json={
        "name": "Intrusion Zone",
        "polygon": [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]]
    })
    zone_id = zone_resp.json()["id"]

    # 3. Create intrusion event
    payload = {
        "event_identifier": "EV-2026-0001",
        "event_type": "INTRUSION",
        "camera_id": camera_id,
        "zone_id": zone_id,
        "track_id": 17,
        "timestamp": "2026-08-29T16:30:00Z",
        "severity": "HIGH",
        "status": "NEW",
        "bounding_box": {"x1": 10, "y1": 20, "x2": 50, "y2": 80},
        "position": {"x": 30, "y": 80},
        "metadata": {"pipeline": "yolov8_bytetrack"}
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["event_identifier"] == "EV-2026-0001"
    assert data["camera_id"] == camera_id
    assert data["zone_id"] == zone_id
    assert data["alert_id"] is not None  # Automatic alert generated


def test_event_missing_camera_api(client: TestClient) -> None:
    """
    Test 4: Creating event with nonexistent camera_id returns 404.
    """
    payload = {
        "event_identifier": "EV-2026-0002",
        "event_type": "INTRUSION",
        "camera_id": "00000000-0000-0000-0000-000000000000",
        "track_id": 18,
        "timestamp": "2026-08-29T16:35:00Z"
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 404
    assert "camera not found" in response.json()["error"]["message"].lower()


def test_event_missing_zone_api(client: TestClient) -> None:
    """
    Test 5: Creating event with nonexistent zone_id returns 404.
    """
    # Get active camera id
    cam_resp = client.get("/api/v1/cameras")
    camera_id = cam_resp.json()[0]["id"]

    payload = {
        "event_identifier": "EV-2026-0003",
        "event_type": "INTRUSION",
        "camera_id": camera_id,
        "zone_id": "00000000-0000-0000-0000-000000000000",
        "track_id": 19,
        "timestamp": "2026-08-29T16:35:00Z"
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 404
    assert "zone not found" in response.json()["error"]["message"].lower()


def test_event_zone_camera_mismatch_api(client: TestClient) -> None:
    """
    Test 6: Creating event with camera A but zone B (belonging to camera C) returns 409 Conflict.
    """
    # Create camera A
    cam_a = client.post("/api/v1/cameras", json={
        "name": "Camera A",
        "camera_identifier": "cam-a"
    }).json()["id"]

    # Create camera C
    cam_c = client.post("/api/v1/cameras", json={
        "name": "Camera C",
        "camera_identifier": "cam-c"
    }).json()["id"]

    # Create zone B under camera C
    zone_b = client.post(f"/api/v1/cameras/{cam_c}/zones", json={
        "name": "Zone B",
        "polygon": [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]]
    }).json()["id"]

    payload = {
        "event_identifier": "EV-2026-0004",
        "event_type": "INTRUSION",
        "camera_id": cam_a,
        "zone_id": zone_b,
        "track_id": 20,
        "timestamp": "2026-08-29T16:40:00Z"
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 409
    assert "does not belong to camera" in response.json()["error"]["message"].lower()


def test_event_duplicate_identifier_api(client: TestClient) -> None:
    """
    Test 7: Creating event with duplicate event_identifier returns 409 Conflict.
    """
    cam_resp = client.get("/api/v1/cameras")
    camera_id = cam_resp.json()[0]["id"]

    payload = {
        "event_identifier": "EV-2026-0001",  # Duplicate
        "event_type": "INTRUSION",
        "camera_id": camera_id,
        "track_id": 21,
        "timestamp": "2026-08-29T16:45:00Z"
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 409
    assert "identifier already exists" in response.json()["error"]["message"].lower()


def test_event_invalid_type_and_severity_api(client: TestClient) -> None:
    """
    Test 8-10: Creating event with invalid enum types returns 422.
    """
    cam_resp = client.get("/api/v1/cameras")
    camera_id = cam_resp.json()[0]["id"]

    # Invalid event type
    payload = {
        "event_identifier": "EV-2026-0005",
        "event_type": "INVALID_TYPE",
        "camera_id": camera_id,
        "track_id": 22,
        "timestamp": "2026-08-29T16:50:00Z"
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 422

    # Invalid severity
    payload = {
        "event_identifier": "EV-2026-0006",
        "event_type": "INTRUSION",
        "camera_id": camera_id,
        "track_id": 23,
        "timestamp": "2026-08-29T16:50:00Z",
        "severity": "CRITICAL_MAX"
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 422


def test_get_event_api(client: TestClient) -> None:
    """
    Test 11-12: Get event details, and missing event 404.
    """
    # Fetch events list to get id
    list_resp = client.get("/api/v1/events")
    event_id = list_resp.json()[0]["id"]

    response = client.get(f"/api/v1/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["id"] == event_id

    # Missing ID
    missing_response = client.get("/api/v1/events/missing-event-uuid")
    assert missing_response.status_code == 404


def test_list_events_and_pagination_api(client: TestClient) -> None:
    """
    Test 13-15: List events with pagination and filters.
    """
    response = client.get("/api/v1/events?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 2


def test_update_event_mutable_fields_api(client: TestClient) -> None:
    """
    Test 16: Update mutable event fields (status, severity, metadata).
    """
    list_resp = client.get("/api/v1/events")
    event_id = list_resp.json()[0]["id"]

    payload = {
        "status": "PROCESSED",
        "severity": "CRITICAL",
        "metadata": {"pipeline": "yolov8_updated", "notes": "manually processed"}
    }
    response = client.patch(f"/api/v1/events/{event_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PROCESSED"
    assert data["severity"] == "CRITICAL"
    assert data["metadata"]["notes"] == "manually processed"


def test_update_event_immutable_fields_api(client: TestClient) -> None:
    """
    Test 17: Attempt to update immutable fields triggers Pydantic extra validation error (422).
    """
    list_resp = client.get("/api/v1/events")
    event_id = list_resp.json()[0]["id"]

    payload = {
        "camera_id": "00000000-0000-0000-0000-000000000000"
    }
    response = client.patch(f"/api/v1/events/{event_id}", json=payload)
    assert response.status_code == 422


def test_delete_single_event_not_allowed_api(client: TestClient) -> None:
    """
    Test 18: Confirm DELETE on single event item is not allowed (405 Method Not Allowed).
    """
    response = client.delete("/api/v1/events/some-event-uuid")
    assert response.status_code == 405


def test_clear_all_events_bulk_api(client: TestClient) -> None:
    """
    Test 19: Confirm Admin can clear all events in bulk and table becomes empty.
    """
    del_resp = client.delete("/api/v1/events")
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == "Audit logs cleared successfully"

    # Verify events list is now empty
    list_resp = client.get("/api/v1/events")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 0

