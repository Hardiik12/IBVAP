from fastapi.testclient import TestClient


def test_create_camera_api(client: TestClient) -> None:
    """
    Test 1: POST /api/v1/cameras creates camera successfully.
    """
    payload = {
        "name": "Front Entry Camera",
        "camera_identifier": "cam-front-01",
        "source_type": "WEBCAM",
        "location": "Main Entrance",
        "is_active": True
    }
    response = client.post("/api/v1/cameras", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Front Entry Camera"
    assert data["camera_identifier"] == "cam-front-01"
    assert "id" in data


def test_create_camera_duplicate_identifier_api(client: TestClient) -> None:
    """
    Test 2: POST /api/v1/cameras with duplicate camera_identifier returns 409.
    """
    payload = {
        "name": "Another Front Camera",
        "camera_identifier": "cam-front-01",  # Duplicate identifier
        "source_type": "RTSP"
    }
    response = client.post("/api/v1/cameras", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert "identifier already exists" in data["error"]["message"]


def test_list_cameras_api(client: TestClient) -> None:
    """
    Test 3: GET /api/v1/cameras lists all cameras.
    """
    response = client.get("/api/v1/cameras")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(cam["camera_identifier"] == "cam-front-01" for cam in data)


def test_get_camera_by_id_api(client: TestClient) -> None:
    """
    Test 4: GET /api/v1/cameras/{id} returns the requested camera.
    """
    # List to find existing camera ID
    list_resp = client.get("/api/v1/cameras")
    camera_id = list_resp.json()[0]["id"]

    response = client.get(f"/api/v1/cameras/{camera_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == camera_id
    assert data["camera_identifier"] == "cam-front-01"


def test_update_camera_api(client: TestClient) -> None:
    """
    Test 5: PATCH /api/v1/cameras/{id} updates fields successfully.
    """
    list_resp = client.get("/api/v1/cameras")
    camera_id = list_resp.json()[0]["id"]

    payload = {
        "name": "Updated Entry Camera",
        "location": "Front Gate Lobby",
        "is_active": False
    }
    response = client.patch(f"/api/v1/cameras/{camera_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Entry Camera"
    assert data["location"] == "Front Gate Lobby"
    assert data["is_active"] is False


def test_soft_delete_camera_api(client: TestClient) -> None:
    """
    Test 6: DELETE /api/v1/cameras/{id} soft deactivates camera.
    """
    # Create a new camera to delete
    payload = {
        "name": "Temporary Camera",
        "camera_identifier": "cam-temp-01"
    }
    create_resp = client.post("/api/v1/cameras", json=payload)
    camera_id = create_resp.json()["id"]

    response = client.delete(f"/api/v1/cameras/{camera_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False

    # Verify it still exists in the system
    get_resp = client.get(f"/api/v1/cameras/{camera_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["is_active"] is False


def test_get_nonexistent_camera_api(client: TestClient) -> None:
    """
    Test 7: GET /api/v1/cameras/{id} with missing ID returns 404.
    """
    response = client.get("/api/v1/cameras/missing-camera-uuid")
    assert response.status_code == 404
    assert "not found" in response.json()["error"]["message"].lower()


def test_invalid_camera_request_api(client: TestClient) -> None:
    """
    Test 8: POST /api/v1/cameras with missing required fields returns 422.
    """
    response = client.post("/api/v1/cameras", json={})
    assert response.status_code == 422
