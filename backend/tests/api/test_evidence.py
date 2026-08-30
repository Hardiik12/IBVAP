from fastapi.testclient import TestClient


def test_create_evidence_api(client: TestClient) -> None:
    """
    Test 1: POST /api/v1/events/{id}/evidence creates evidence successfully.
    """
    # Create camera
    cam_resp = client.post("/api/v1/cameras", json={
        "name": "Evidence Camera",
        "camera_identifier": "cam-evidence-01"
    })
    camera_id = cam_resp.json()["id"]

    # Create event
    event_resp = client.post("/api/v1/events", json={
        "event_identifier": "EV-EVI-001",
        "event_type": "INTRUSION",
        "camera_id": camera_id,
        "track_id": 40,
        "timestamp": "2026-08-29T17:20:00Z"
    })
    event_id = event_resp.json()["id"]

    payload = {
        "evidence_identifier": "EVD-2026-0001",
        "file_path": "evidence/events/EV-EVI-001/frame_001.jpg",
        "captured_at": "2026-08-29T17:20:05Z",
        "metadata": {"pipeline": "yolov8", "resolution": "1920x1080"}
    }
    response = client.post(f"/api/v1/events/{event_id}/evidence", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["evidence_identifier"] == "EVD-2026-0001"
    assert data["file_path"] == "evidence/events/EV-EVI-001/frame_001.jpg"
    assert data["sha256_hash"] is None  # Hash is None (NULL) initially in Phase 6
    assert "id" in data


def test_create_multiple_evidence_for_event_api(client: TestClient) -> None:
    """
    Test 2: Creating multiple evidence records for the same event succeeds.
    """
    # Find existing event_id
    events_resp = client.get("/api/v1/events?limit=1")
    event_id = events_resp.json()[0]["id"]

    # Create second evidence record
    payload = {
        "evidence_identifier": "EVD-2026-0002",
        "file_path": "evidence/events/EV-EVI-001/frame_002.jpg",
        "captured_at": "2026-08-29T17:20:10Z"
    }
    response = client.post(f"/api/v1/events/{event_id}/evidence", json=payload)
    assert response.status_code == 201
    assert response.json()["evidence_identifier"] == "EVD-2026-0002"


def test_create_evidence_missing_event_api(client: TestClient) -> None:
    """
    Test 3: Creating evidence for nonexistent event returns 404.
    """
    payload = {
        "evidence_identifier": "EVD-2026-0003",
        "file_path": "some/path.jpg",
        "captured_at": "2026-08-29T17:20:15Z"
    }
    response = client.post("/api/v1/events/00000000-0000-0000-0000-000000000000/evidence", json=payload)
    assert response.status_code == 404
    assert "event not found" in response.json()["error"]["message"].lower()


def test_create_evidence_duplicate_identifier_api(client: TestClient) -> None:
    """
    Test 4: Duplicate evidence_identifier returns 409 Conflict.
    """
    events_resp = client.get("/api/v1/events?limit=1")
    event_id = events_resp.json()[0]["id"]

    payload = {
        "evidence_identifier": "EVD-2026-0001",  # Duplicate
        "file_path": "other/path.jpg",
        "captured_at": "2026-08-29T17:20:20Z"
    }
    response = client.post(f"/api/v1/events/{event_id}/evidence", json=payload)
    assert response.status_code == 409
    assert "identifier already exists" in response.json()["error"]["message"].lower()


def test_get_evidence_by_id_api(client: TestClient) -> None:
    """
    Test 5-6: Get evidence, and missing ID returns 404.
    """
    # Get active event id
    events_resp = client.get("/api/v1/events?limit=1")
    event_id = events_resp.json()[0]["id"]

    list_resp = client.get(f"/api/v1/events/{event_id}/evidence")
    evidence_id = list_resp.json()[0]["id"]

    response = client.get(f"/api/v1/evidence/{evidence_id}")
    assert response.status_code == 200
    assert response.json()["id"] == evidence_id

    # Missing ID
    missing_response = client.get("/api/v1/evidence/missing-evidence-uuid")
    assert missing_response.status_code == 404


def test_list_evidence_for_event_api(client: TestClient) -> None:
    """
    Test 7-8: List evidence, and empty list works for new event.
    """
    # Create new camera
    cam_resp = client.post("/api/v1/cameras", json={
        "name": "Empty Evidence Camera",
        "camera_identifier": "cam-empty-evi"
    })
    camera_id = cam_resp.json()["id"]

    # Create new event with no evidence yet
    event_resp = client.post("/api/v1/events", json={
        "event_identifier": "EV-EMPTY-EVI",
        "event_type": "EXIT",
        "camera_id": camera_id,
        "track_id": 41,
        "timestamp": "2026-08-29T17:30:00Z"
    })
    event_id = event_resp.json()["id"]

    # Retrieve list
    response = client.get(f"/api/v1/events/{event_id}/evidence")
    assert response.status_code == 200
    assert response.json() == []  # Empty list


def test_update_evidence_metadata_api(client: TestClient) -> None:
    """
    Test 9: Update mutable metadata dictionary.
    """
    # Create isolated camera, event, and evidence
    cam = client.post("/api/v1/cameras", json={"name": "U-Cam", "camera_identifier": "cam-u-metadata"}).json()["id"]
    evt = client.post("/api/v1/events", json={"event_identifier": "EV-U-01", "event_type": "EXIT", "camera_id": cam, "track_id": 1, "timestamp": "2026-08-29T18:00:00Z"}).json()["id"]
    evidence_id = client.post(f"/api/v1/events/{evt}/evidence", json={"evidence_identifier": "EVD-U-01", "file_path": "a.jpg", "captured_at": "2026-08-29T18:00:01Z"}).json()["id"]

    payload = {
        "metadata": {"pipeline": "yolov8_updated", "notes": "annotated by operator"}
    }
    response = client.patch(f"/api/v1/evidence/{evidence_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["metadata"]["notes"] == "annotated by operator"


def test_update_evidence_immutable_fields_api(client: TestClient) -> None:
    """
    Test 10: Attempt to update immutable fields (event_id, sha256_hash) returns 422.
    """
    # Create isolated camera, event, and evidence
    cam = client.post("/api/v1/cameras", json={"name": "U-Cam-2", "camera_identifier": "cam-u-immutable"}).json()["id"]
    evt = client.post("/api/v1/events", json={"event_identifier": "EV-U-02", "event_type": "EXIT", "camera_id": cam, "track_id": 1, "timestamp": "2026-08-29T18:00:00Z"}).json()["id"]
    evidence_id = client.post(f"/api/v1/events/{evt}/evidence", json={"evidence_identifier": "EVD-U-02", "file_path": "a.jpg", "captured_at": "2026-08-29T18:00:01Z"}).json()["id"]

    payload = {
        "event_id": "00000000-0000-0000-0000-000000000000"
    }
    response = client.patch(f"/api/v1/evidence/{evidence_id}", json=payload)
    assert response.status_code == 422


def test_delete_evidence_not_allowed_api(client: TestClient) -> None:
    """
    Test 11: DELETE /api/v1/evidence/{id} is blocked (405 Method Not Allowed).
    """
    response = client.delete("/api/v1/evidence/some-evidence-uuid")
    assert response.status_code == 405


def test_event_evidence_lifecycle_integration_api(client: TestClient) -> None:
    """
    Test 12: Lifecycle integration (Create Event -> Create Evidence -> GET Event -> GET Evidence).
    """
    # Create camera
    cam_resp = client.post("/api/v1/cameras", json={
        "name": "Integration Camera",
        "camera_identifier": "cam-integration"
    })
    camera_id = cam_resp.json()["id"]

    # 1. Create Event
    event_resp = client.post("/api/v1/events", json={
        "event_identifier": "EV-INT-99",
        "event_type": "INTRUSION",
        "camera_id": camera_id,
        "track_id": 99,
        "timestamp": "2026-08-29T18:00:00Z"
    })
    event_id = event_resp.json()["id"]

    # 2. Create Evidence
    evi_resp = client.post(f"/api/v1/events/{event_id}/evidence", json={
        "evidence_identifier": "EVD-INT-99",
        "file_path": "data/frame_99.jpg",
        "captured_at": "2026-08-29T18:00:01Z"
    })
    evidence_id = evi_resp.json()["id"]

    # 3. GET Event
    get_evt = client.get(f"/api/v1/events/{event_id}")
    assert get_evt.status_code == 200
    assert get_evt.json()["event_identifier"] == "EV-INT-99"

    # 4. GET Evidence
    get_evi = client.get(f"/api/v1/evidence/{evidence_id}")
    assert get_evi.status_code == 200
    assert get_evi.json()["evidence_identifier"] == "EVD-INT-99"
    assert get_evi.json()["event_id"] == event_id


def test_clear_evidence_vault_bulk_api(client: TestClient, unauthenticated_client: TestClient) -> None:
    """Test DELETE /api/v1/evidence clears all evidence vault records and enforces RBAC."""
    # 1. Unauthenticated request is rejected
    unauth_resp = unauthenticated_client.delete("/api/v1/evidence")
    assert unauth_resp.status_code == 401

    # 2. Authenticated operator/admin clears evidence
    del_resp = client.delete("/api/v1/evidence")
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == "EVIDENCE VAULT CLEARED SUCCESSFULLY"

    # 3. Querying all evidence returns empty list
    list_resp = client.get("/api/v1/evidence")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 0

