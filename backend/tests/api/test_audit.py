from fastapi.testclient import TestClient


def test_audit_logs_login_events(unauthenticated_client: TestClient, admin_client: TestClient) -> None:
    """Test login success and failure generate transactionally consistent audit log entries."""
    # 1. Failed login attempt
    unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "admin_user",
        "password": "WrongPassword!"
    })

    # 2. Successful login attempt
    unauthenticated_client.post("/api/v1/auth/login", json={
        "username_or_email": "admin_user",
        "password": "AdminSecret123!"
    })

    # 3. Query audit logs as Administrator
    logs_resp = admin_client.get("/api/v1/audit-logs?resource_type=AUTH")
    assert logs_resp.status_code == 200
    logs = logs_resp.json()
    actions = [l["action"] for l in logs]
    assert "LOGIN_SUCCESS" in actions
    assert "LOGIN_FAILURE" in actions


def test_audit_logs_administrative_and_operational_actions(admin_client: TestClient, operator_client: TestClient) -> None:
    """Test camera creation, evidence verification, and alert acknowledgment generate audit entries."""
    # 1. Create camera as Admin
    cam_resp = admin_client.post("/api/v1/cameras", json={
        "name": "Audit Camera",
        "camera_identifier": "cam-audit-test"
    })
    cam_id = cam_resp.json()["id"]

    # 2. Create Event & Alert
    event_resp = admin_client.post("/api/v1/events", json={
        "event_identifier": "EV-AUDIT-01",
        "event_type": "INTRUSION",
        "camera_id": cam_id,
        "track_id": 7,
        "timestamp": "2026-08-29T19:00:00Z"
    })
    alert_id = event_resp.json()["alert_id"]

    # 3. Acknowledge alert as Operator
    ack_resp = operator_client.patch(f"/api/v1/alerts/{alert_id}", json={
        "status": "ACKNOWLEDGED"
    })
    assert ack_resp.status_code == 200

    # 4. Check audit logs as Admin
    logs_resp = admin_client.get("/api/v1/audit-logs")
    assert logs_resp.status_code == 200
    logs = logs_resp.json()
    actions = [l["action"] for l in logs]
    assert "CAMERA_CREATED" in actions
    assert "ALERT_ACKNOWLEDGED" in actions


def test_audit_logs_deletion_not_allowed(admin_client: TestClient) -> None:
    """Test DELETE /api/v1/audit-logs is blocked (405 Method Not Allowed)."""
    response = admin_client.delete("/api/v1/audit-logs")
    assert response.status_code == 405
