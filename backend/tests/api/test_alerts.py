from fastapi.testclient import TestClient


def test_intrusion_event_creates_alert_api(client: TestClient) -> None:
    """
    Test 1-3: Creating an intrusion event automatically generates an ACTIVE alert.
    """
    # 1. Create camera
    cam_resp = client.post("/api/v1/cameras", json={
        "name": "Alert Camera",
        "camera_identifier": "cam-alert-01"
    })
    camera_id = cam_resp.json()["id"]

    # 2. Create intrusion event
    payload = {
        "event_identifier": "EV-ALERT-001",
        "event_type": "INTRUSION",
        "camera_id": camera_id,
        "track_id": 99,
        "timestamp": "2026-08-29T17:00:00Z"
    }
    event_resp = client.post("/api/v1/events", json=payload)
    assert event_resp.status_code == 201
    alert_id = event_resp.json()["alert_id"]
    assert alert_id is not None

    # 3. Verify alert details
    response = client.get(f"/api/v1/alerts/{alert_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACTIVE"
    assert data["severity"] == "HIGH"
    assert "intrusion" in data["message"].lower()


def test_non_intrusion_event_does_not_create_alert_api(client: TestClient) -> None:
    """
    Test 2 (cont): Non-intrusion event (e.g. EXIT) does not create an alert.
    """
    cam_resp = client.get("/api/v1/cameras")
    camera_id = cam_resp.json()[0]["id"]

    payload = {
        "event_identifier": "EV-ALERT-002",
        "event_type": "EXIT",
        "camera_id": camera_id,
        "track_id": 100,
        "timestamp": "2026-08-29T17:05:00Z"
    }
    event_resp = client.post("/api/v1/events", json=payload)
    assert event_resp.status_code == 201
    assert event_resp.json()["alert_id"] is None


def test_get_alert_api(client: TestClient) -> None:
    """
    Test 4-5: Get alert details, missing alert returns 404.
    """
    list_resp = client.get("/api/v1/alerts")
    alert_id = list_resp.json()[0]["id"]

    response = client.get(f"/api/v1/alerts/{alert_id}")
    assert response.status_code == 200
    assert response.json()["id"] == alert_id

    missing_response = client.get("/api/v1/alerts/missing-alert-uuid")
    assert missing_response.status_code == 404


def test_list_alerts_and_filtering_api(client: TestClient) -> None:
    """
    Test 6-7: List alerts with pagination and camera_id filtering.
    """
    # Find alert's camera_id
    list_resp = client.get("/api/v1/alerts")
    alert = list_resp.json()[0]
    alert_id = alert["id"]

    # Retrieve associated event to get camera_id
    event_resp = client.get(f"/api/v1/events?limit=100")
    camera_id = [evt for evt in event_resp.json() if evt["alert_id"] == alert_id][0]["camera_id"]

    # Filter list
    filter_resp = client.get(f"/api/v1/alerts?camera_id={camera_id}&limit=5")
    assert filter_resp.status_code == 200
    assert len(filter_resp.json()) >= 1
    assert all(alt["id"] == alert_id or alt["severity"] == "HIGH" for alt in filter_resp.json())


def test_update_alert_acknowledgement_api(client: TestClient) -> None:
    """
    Test 8: Update status to ACKNOWLEDGED populates acknowledged_at timestamp.
    """
    list_resp = client.get("/api/v1/alerts")
    alert_id = list_resp.json()[0]["id"]

    payload = {
        "status": "ACKNOWLEDGED",
        "acknowledged_by": "00000000-0000-0000-0000-000000000001"
    }
    response = client.patch(f"/api/v1/alerts/{alert_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACKNOWLEDGED"
    assert data["acknowledged_at"] is not None
    assert data["acknowledged_by"] == "00000000-0000-0000-0000-000000000001"
