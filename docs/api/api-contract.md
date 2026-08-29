# IBVAP API Contract (DRAFT)

This document defines the high-level internal and external interface specifications for IBVAP.

---

## 1. AI Engine → Backend REST / Ingestion Interface (DRAFT)

### Event Payload Schema (`POST /api/v1/events`)
```json
{
  "event_type": "INTRUSION",
  "camera_id": "cam-01",
  "zone_id": "zone-restricted-alpha",
  "track_id": 17,
  "class_name": "person",
  "confidence": 0.94,
  "timestamp": "2026-08-29T18:00:00Z",
  "severity": "HIGH",
  "bbox": [120, 240, 310, 580],
  "evidence": {
    "snapshot_base64": "...",
    "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  }
}
```

---

## 2. Backend → Frontend REST API (DRAFT)

- `GET /api/v1/health` — System status check
- `GET /api/v1/cameras` — List active camera feeds
- `GET /api/v1/events` — Retrieve event log with pagination & filters
- `GET /api/v1/evidence/{evidence_id}` — Retrieve evidence details and stored SHA-256 hash
- `POST /api/v1/evidence/{evidence_id}/verify` — Run server-side SHA-256 verification against current file contents

---

## 3. Backend → Frontend Real-time WebSocket (`ws://localhost:8000/ws/alerts`) (DRAFT)

Pushes real-time alerts upon INTRUSION event detection.

```json
{
  "event_id": "evt-88392",
  "event_type": "INTRUSION",
  "camera_id": "cam-01",
  "zone_id": "zone-restricted-alpha",
  "track_id": 17,
  "timestamp": "2026-08-29T18:00:00Z",
  "severity": "HIGH",
  "evidence_id": "ev-00912"
}
```
