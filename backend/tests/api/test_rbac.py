from fastapi.testclient import TestClient


def test_operator_rbac_permissions(operator_client: TestClient) -> None:
    """Test OPERATOR role permissions matrix."""
    # 1. Can view cameras, zones, events, alerts
    assert operator_client.get("/api/v1/cameras").status_code == 200
    assert operator_client.get("/api/v1/events").status_code == 200
    assert operator_client.get("/api/v1/alerts").status_code == 200

    # 2. Cannot manage cameras (403)
    cam_resp = operator_client.post("/api/v1/cameras", json={"name": "Forbidden Cam", "camera_identifier": "cam-forb-1"})
    assert cam_resp.status_code == 403

    # 3. Cannot view audit logs (403)
    assert operator_client.get("/api/v1/audit-logs").status_code == 403


def test_analyst_rbac_permissions(analyst_client: TestClient) -> None:
    """Test ANALYST role permissions matrix."""
    # 1. Can view cameras, events, alerts
    assert analyst_client.get("/api/v1/cameras").status_code == 200
    assert analyst_client.get("/api/v1/events").status_code == 200
    assert analyst_client.get("/api/v1/alerts").status_code == 200

    # 2. Cannot acknowledge alerts (403)
    assert analyst_client.patch("/api/v1/alerts/some-id", json={"status": "ACKNOWLEDGED"}).status_code == 403

    # 3. Cannot manage cameras (403)
    assert analyst_client.post("/api/v1/cameras", json={"name": "Forbidden Cam 2", "camera_identifier": "cam-forb-2"}).status_code == 403

    # 4. Cannot view audit logs (403)
    assert analyst_client.get("/api/v1/audit-logs").status_code == 403


def test_auditor_rbac_permissions(auditor_client: TestClient) -> None:
    """Test AUDITOR role permissions matrix."""
    # 1. Can view events, alerts, and audit logs
    assert auditor_client.get("/api/v1/events").status_code == 200
    assert auditor_client.get("/api/v1/alerts").status_code == 200
    assert auditor_client.get("/api/v1/audit-logs").status_code == 200

    # 2. Cannot view cameras or zones (403)
    assert auditor_client.get("/api/v1/cameras").status_code == 403

    # 3. Cannot manage cameras or users (403)
    assert auditor_client.post("/api/v1/cameras", json={"name": "Forbidden Cam 3", "camera_identifier": "cam-forb-3"}).status_code == 403
    assert auditor_client.get("/api/v1/users").status_code == 403


def test_administrator_rbac_permissions(admin_client: TestClient) -> None:
    """Test ADMINISTRATOR role full permission matrix."""
    assert admin_client.get("/api/v1/cameras").status_code == 200
    assert admin_client.get("/api/v1/events").status_code == 200
    assert admin_client.get("/api/v1/alerts").status_code == 200
    assert admin_client.get("/api/v1/users").status_code == 200
    assert admin_client.get("/api/v1/audit-logs").status_code == 200
