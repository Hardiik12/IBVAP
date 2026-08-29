from fastapi.testclient import TestClient


def test_health_endpoint_status_code(client: TestClient) -> None:
    """
    Test 1: GET /health returns HTTP 200 OK.
    """
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_response_content(client: TestClient) -> None:
    """
    Test 2: GET /health response contains valid status.
    """
    response = client.get("/health")
    data = response.json()
    assert data.get("status") in ["ok", "healthy", "degraded"]
    assert "service" in data
    assert "version" in data


def test_root_endpoint(client: TestClient) -> None:
    """
    Test 3: GET / returns root service metadata.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data.get("service") == "IBVAP Backend API"
    assert "version" in data
