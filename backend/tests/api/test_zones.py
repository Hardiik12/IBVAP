from fastapi.testclient import TestClient


def test_create_zone_api(client: TestClient) -> None:
    """
    Test 1: POST /api/v1/cameras/{id}/zones creates zone successfully.
    """
    # Create camera first
    cam_resp = client.post("/api/v1/cameras", json={
        "name": "Zone Anchor Camera",
        "camera_identifier": "cam-zone-anchor"
    })
    camera_id = cam_resp.json()["id"]

    polygon = [
        [0.2, 0.2],
        [0.8, 0.2],
        [0.8, 0.8],
        [0.2, 0.8]
    ]
    payload = {
        "name": "Perimeter Restricted Area A",
        "zone_type": "RESTRICTED",
        "polygon": polygon,
        "is_active": True
    }
    response = client.post(f"/api/v1/cameras/{camera_id}/zones", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Perimeter Restricted Area A"
    assert data["polygon"] == polygon
    assert data["camera_id"] == camera_id
    assert "id" in data


def test_create_zone_missing_camera_api(client: TestClient) -> None:
    """
    Test 2: POST /api/v1/cameras/missing-id/zones returns 404.
    """
    payload = {
        "name": "Restricted Area",
        "polygon": [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]]
    }
    response = client.post("/api/v1/cameras/missing-camera-uuid/zones", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["error"]["message"].lower()


def test_polygon_too_few_points_api(client: TestClient) -> None:
    """
    Test 3: Polygon with fewer than 3 points returns 422 Unprocessable Entity.
    """
    cam_resp = client.post("/api/v1/cameras", json={
        "name": "Test Polygon Points Camera",
        "camera_identifier": "cam-poly-pts"
    })
    camera_id = cam_resp.json()["id"]

    # Only 2 points
    payload = {
        "name": "Invalid Triangle",
        "polygon": [[0.1, 0.1], [0.9, 0.9]]
    }
    response = client.post(f"/api/v1/cameras/{camera_id}/zones", json=payload)
    assert response.status_code == 422
    assert "at least 3 points" in response.json()["detail"][0]["msg"].lower()


def test_polygon_coordinates_outside_bounds_api(client: TestClient) -> None:
    """
    Test 4: Polygon coordinates outside [0.0, 1.0] returns 422.
    """
    list_resp = client.get("/api/v1/cameras")
    camera_id = list_resp.json()[0]["id"]

    # Coordinates outside 0.0 - 1.0 (e.g. 1.5)
    payload = {
        "name": "Out of Bounds Zone",
        "polygon": [[0.1, 0.1], [1.5, 0.1], [0.9, 0.9], [0.1, 0.9]]
    }
    response = client.post(f"/api/v1/cameras/{camera_id}/zones", json=payload)
    assert response.status_code == 422
    assert "normalized between 0.0 and 1.0" in response.json()["detail"][0]["msg"].lower()


def test_list_zones_api(client: TestClient) -> None:
    """
    Test 5: GET /api/v1/cameras/{id}/zones returns camera's zones.
    """
    # Create camera
    cam_resp = client.post("/api/v1/cameras", json={
        "name": "Zone List Camera",
        "camera_identifier": "cam-zone-list"
    })
    camera_id = cam_resp.json()["id"]

    # Create zone
    client.post(f"/api/v1/cameras/{camera_id}/zones", json={
        "name": "Monitored Zone A",
        "zone_type": "MONITORED",
        "polygon": [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]]
    })

    response = client.get(f"/api/v1/cameras/{camera_id}/zones")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Monitored Zone A"


def test_get_zone_by_id_api(client: TestClient) -> None:
    """
    Test 6: GET /api/v1/zones/{id} returns requested zone.
    """
    list_resp = client.get("/api/v1/cameras")
    camera_id = list_resp.json()[0]["id"]

    zones_resp = client.get(f"/api/v1/cameras/{camera_id}/zones")
    zone_id = zones_resp.json()[0]["id"]

    response = client.get(f"/api/v1/zones/{zone_id}")
    assert response.status_code == 200
    assert response.json()["id"] == zone_id


def test_update_zone_api(client: TestClient) -> None:
    """
    Test 7: PATCH /api/v1/zones/{id} updates details successfully.
    """
    list_resp = client.get("/api/v1/cameras")
    camera_id = list_resp.json()[0]["id"]

    zones_resp = client.get(f"/api/v1/cameras/{camera_id}/zones")
    zone_id = zones_resp.json()[0]["id"]

    new_polygon = [[0.3, 0.3], [0.7, 0.3], [0.7, 0.7], [0.3, 0.7]]
    payload = {
        "name": "Rescaled Zone",
        "polygon": new_polygon
    }
    response = client.patch(f"/api/v1/zones/{zone_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Rescaled Zone"
    assert data["polygon"] == new_polygon


def test_soft_delete_zone_api(client: TestClient) -> None:
    """
    Test 8: DELETE /api/v1/zones/{id} soft deactivates zone.
    """
    list_resp = client.get("/api/v1/cameras")
    camera_id = list_resp.json()[0]["id"]

    zones_resp = client.get(f"/api/v1/cameras/{camera_id}/zones")
    zone_id = zones_resp.json()[0]["id"]

    response = client.delete(f"/api/v1/zones/{zone_id}")
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # Check it exists with inactive state
    get_resp = client.get(f"/api/v1/zones/{zone_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["is_active"] is False


def test_get_nonexistent_zone_api(client: TestClient) -> None:
    """
    Test 9: GET /api/v1/zones/{id} with missing ID returns 404.
    """
    response = client.get("/api/v1/zones/missing-zone-uuid")
    assert response.status_code == 404
    assert "not found" in response.json()["error"]["message"].lower()
