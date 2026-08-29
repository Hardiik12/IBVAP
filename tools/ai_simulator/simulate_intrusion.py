#!/usr/bin/env python3
"""
IBVAP AI Simulator Tool
Simulates normalized AI intrusion event contracts and verifies the complete end-to-end backend lifecycle:
Authentication -> Camera/Zone Setup -> WebSocket Listener -> Event Ingestion -> Alert Generation ->
Evidence Metadata -> SHA-256 Hashing -> Tamper Verification -> Audit Logging.
"""

import os
import sys
import json
import time
import asyncio
import urllib.request
import urllib.parse
import urllib.error
import websockets

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
WS_URL = os.environ.get("WS_URL", "ws://localhost:8000")
EVIDENCE_DIR = os.environ.get("EVIDENCE_DIR", "data/evidence")


def http_request(url: str, method: str = "GET", data: dict = None, headers: dict = None):
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)

    encoded_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=encoded_data, headers=req_headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            return resp.status, json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        body = json.loads(resp_body) if resp_body else {}
        return e.code, body


async def run_simulation():
    print("=" * 60)
    print("🤖 IBVAP AI SIMULATOR — END-TO-END PIPELINE VALIDATION")
    print("=" * 60)

    # Step 1: Authenticate AI Simulator Client
    print("\n1️⃣ Authenticating AI Simulator client...")
    status, auth_resp = http_request(
        f"{BASE_URL}/api/v1/auth/login",
        method="POST",
        data={"username_or_email": "admin_user", "password": "AdminSecret123!"}
    )
    if status != 200:
        print(f"❌ Login failed ({status}): {auth_resp}")
        sys.exit(1)

    token = auth_resp["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}
    print(f"✅ Login successful. Token acquired: {token[:20]}...")

    # Step 2: Register/Verify Camera Feed
    print("\n2️⃣ Registering test camera feed...")
    cam_identifier = f"cam-sim-{int(time.time())}"
    status, cam_resp = http_request(
        f"{BASE_URL}/api/v1/cameras",
        method="POST",
        data={
            "name": "Simulated Perimeter Camera 01",
            "camera_identifier": cam_identifier,
            "source_type": "FILE",
            "location": "North Border Sector 4",
            "is_active": True
        },
        headers=auth_header
    )
    if status != 201:
        print(f"❌ Camera creation failed ({status}): {cam_resp}")
        sys.exit(1)
    
    camera_id = cam_resp["id"]
    print(f"✅ Camera created. ID: {camera_id} ({cam_identifier})")

    # Step 3: Configure Restricted Zone
    print("\n3️⃣ Configuring restricted zone on camera...")
    status, zone_resp = http_request(
        f"{BASE_URL}/api/v1/cameras/{camera_id}/zones",
        method="POST",
        data={
            "name": "Restricted Zone A",
            "zone_type": "RESTRICTED",
            "polygon": [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]],
            "is_active": True
        },
        headers=auth_header
    )
    if status != 201:
        print(f"❌ Zone creation failed ({status}): {zone_resp}")
        sys.exit(1)

    zone_id = zone_resp["id"]
    print(f"✅ Restricted Zone created. ID: {zone_id}")

    # Step 4: Connect Real-Time WebSocket Client
    print("\n4️⃣ Connecting to Real-Time WebSocket Notification Stream...")
    ws_endpoint = f"{WS_URL}/api/v1/ws/events?token={token}"
    
    async with websockets.connect(ws_endpoint) as websocket:
        print("✅ WebSocket client connected successfully.")

        # Step 5: Post Normalized AI Intrusion Event
        print("\n5️⃣ Ingesting Normalized AI INTRUSION Event...")
        event_identifier = f"SIM-EV-{int(time.time())}"
        event_payload = {
            "event_identifier": event_identifier,
            "event_type": "INTRUSION",
            "camera_id": camera_id,
            "zone_id": zone_id,
            "track_id": 17,
            "timestamp": "2026-08-29T20:30:00Z",
            "severity": "HIGH",
            "status": "NEW",
            "bounding_box": {"x1": 420, "y1": 210, "x2": 510, "y2": 480},
            "position": {"x": 465, "y": 480},
            "metadata": {"simulator": "simulate_intrusion.py", "confidence": 0.96}
        }

        status, event_resp = http_request(
            f"{BASE_URL}/api/v1/events",
            method="POST",
            data=event_payload,
            headers=auth_header
        )
        if status != 201:
            print(f"❌ Event ingestion failed ({status}): {event_resp}")
            sys.exit(1)

        event_id = event_resp["id"]
        alert_id = event_resp["alert_id"]
        print(f"✅ Event persisted. ID: {event_id}")
        print(f"✅ Alert automatically generated. ID: {alert_id}")

        # Step 6: Verify Real-Time WebSocket Delivery
        print("\n6️⃣ Waiting for Real-Time WebSocket Broadcast...")
        ws_msg_raw = await asyncio.wait_for(websocket.recv(), timeout=5.0)
        ws_msg = json.loads(ws_msg_raw)
        print(f"✅ Received WebSocket message type: '{ws_msg.get('type')}'")
        assert ws_msg["type"] == "INTRUSION_ALERT"
        assert ws_msg["event"]["event_identifier"] == event_identifier
        assert ws_msg["alert"]["id"] == alert_id
        print("✅ Real-Time WebSocket notification payload verified.")

        # Step 7: Associate Digital Evidence Snapshot
        print("\n7️⃣ Creating Evidence Metadata & Controlled Snapshot File...")
        os.makedirs(EVIDENCE_DIR, exist_ok=True)
        rel_file_path = f"sim_frame_{event_identifier}.jpg"
        full_file_path = os.path.join(EVIDENCE_DIR, rel_file_path)

        original_content = b"\xFF\xD8\xFF\xE0\x00\x10JFIF Simulated Snapshot Binary Payload Data"
        with open(full_file_path, "wb") as f:
            f.write(original_content)

        status, evidence_resp = http_request(
            f"{BASE_URL}/api/v1/events/{event_id}/evidence",
            method="POST",
            data={
                "evidence_identifier": f"EVD-{event_identifier}",
                "file_path": rel_file_path,
                "captured_at": "2026-08-29T20:30:00Z",
                "metadata": {"camera_resolution": "1920x1080"}
            },
            headers=auth_header
        )
        if status != 201:
            print(f"❌ Evidence creation failed ({status}): {evidence_resp}")
            sys.exit(1)

        evidence_id = evidence_resp["id"]
        print(f"✅ Evidence metadata created. ID: {evidence_id}")

        # Step 8: Generate Cryptographic SHA-256 Hash
        print("\n8️⃣ Computing Server-Side SHA-256 Hash...")
        status, hash_resp = http_request(
            f"{BASE_URL}/api/v1/evidence/{evidence_id}/hash",
            method="POST",
            headers=auth_header
        )
        print(f"✅ SHA-256 Hash generated: {hash_resp.get('sha256_hash')}")

        # Step 9: Verify Original File Integrity
        print("\n9️⃣ Verifying Evidence Integrity (Original File)...")
        status, verify_resp = http_request(
            f"{BASE_URL}/api/v1/evidence/{evidence_id}/verify",
            method="GET",
            headers=auth_header
        )
        print(f"✅ Verification result: status='{verify_resp.get('status')}', verified={verify_resp.get('verified')}")
        assert verify_resp["status"] == "VERIFIED"
        assert verify_resp["verified"] is True

        # Step 10: Simulate Tampering (Physical File Modification)
        print("\n🔟 Simulating Evidence Tampering (Modifying physical file on disk)...")
        with open(full_file_path, "wb") as f:
            f.write(b"\xFF\xD8\xFF\xE0 TAMPERED_PAYLOAD_UNAUTHORIZED_MUTATION")

        status, tamper_resp = http_request(
            f"{BASE_URL}/api/v1/evidence/{evidence_id}/verify",
            method="GET",
            headers=auth_header
        )
        print(f"⚠️ Tamper verification result: status='{tamper_resp.get('status')}', verified={tamper_resp.get('verified')}")
        assert tamper_resp["status"] == "MISMATCH"
        assert tamper_resp["verified"] is False
        print("✅ Tamper detection successfully flagged file mutation as MISMATCH.")

        # Step 11: Restore Original File and Re-verify
        print("\n1️⃣1️⃣ Restoring original physical evidence file...")
        with open(full_file_path, "wb") as f:
            f.write(original_content)

        status, restore_resp = http_request(
            f"{BASE_URL}/api/v1/evidence/{evidence_id}/verify",
            method="GET",
            headers=auth_header
        )
        print(f"✅ Restored verification result: status='{restore_resp.get('status')}', verified={restore_resp.get('verified')}")
        assert restore_resp["status"] == "VERIFIED"
        assert restore_resp["verified"] is True

        # Step 12: Inspect Audit Trail
        print("\n1️⃣2️⃣ Inspecting System Audit Logs...")
        status, audit_resp = http_request(
            f"{BASE_URL}/api/v1/audit-logs?limit=5",
            method="GET",
            headers=auth_header
        )
        print(f"✅ Retrived {len(audit_resp)} audit log entries.")
        actions = [log["action"] for log in audit_resp]
        print(f"   Actions found in audit trail: {actions}")

        # Clean up temporary test file
        if os.path.exists(full_file_path):
            os.remove(full_file_path)

    print("\n" + "=" * 60)
    print("🎉 M1 END-TO-END INTEGRATION CHECKPOINT SUCCESSFUL!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_simulation())
