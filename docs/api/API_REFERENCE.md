# IBVAP API Quick Reference & Data Contracts

## 1. REST Endpoint Summary Table

| Category | Method | Path | Required Role | Description |
| :--- | :--- | :--- | :--- | :--- |
| **System** | `GET` | `/health` | Public | Backend health and status check |
| **Auth** | `POST` | `/api/v1/auth/login` | Public | Password authentication (returns JWT) |
| **Auth** | `GET` | `/api/v1/auth/me` | Authenticated | Get current authenticated user profile |
| **Auth** | `POST` | `/api/v1/mfa/verify` | Authenticated | Verify RFC 6238 TOTP code |
| **Auth** | `POST` | `/api/v1/face-auth/verify`| Authenticated | Verify 1-to-1 facial embedding |
| **Cameras** | `GET` | `/api/v1/cameras` | Authenticated | List all configured camera sources |
| **Cameras** | `POST` | `/api/v1/cameras` | `ADMINISTRATOR` | Register new camera source |
| **Cameras** | `GET` | `/api/v1/cameras/{id}` | Authenticated | Get single camera details |
| **Cameras** | `PATCH`| `/api/v1/cameras/{id}` | `ADMINISTRATOR` | Update camera settings |
| **Cameras** | `DELETE`| `/api/v1/cameras/{id}`| `ADMINISTRATOR` | Soft-deactivate camera |
| **Zones** | `GET` | `/api/v1/cameras/{id}/zones` | Authenticated | List polygon zones for a camera |
| **Zones** | `POST` | `/api/v1/cameras/{id}/zones` | `ADMIN`, `OPERATOR` | Create new exclusion zone |
| **Zones** | `PATCH`| `/api/v1/zones/{id}` | `ADMIN`, `OPERATOR` | Update zone polygon boundaries |
| **Zones** | `DELETE`| `/api/v1/zones/{id}` | `ADMIN`, `OPERATOR` | Deactivate zone |
| **Events** | `POST` | `/api/v1/events` | `ADMIN`, `OPERATOR` | Ingest AI intrusion event |
| **Events** | `GET` | `/api/v1/events` | Authenticated | Query paginated event history |
| **Events** | `GET` | `/api/v1/events/{id}` | Authenticated | Get single event details |
| **Alerts** | `GET` | `/api/v1/alerts` | Authenticated | List active/acknowledged alarms |
| **Alerts** | `PATCH`| `/api/v1/alerts/{id}` | `ADMIN`, `OPERATOR` | Acknowledge/resolve alarm |
| **Evidence**| `GET` | `/api/v1/events/{id}/evidence`| Authenticated| List evidence snapshots for event |
| **Evidence**| `GET` | `/api/v1/evidence/{id}` | Authenticated | Get single evidence record |
| **Evidence**| `GET` | `/api/v1/evidence/{id}/verify`| Authenticated| Verify on-disk SHA-256 hash |
| **Audit** | `GET` | `/api/v1/audit-logs` | `ADMIN`, `ANALYST`, `AUDITOR` | Query immutable audit trail |
| **WebSocket**| `WS` | `/api/v1/ws/events?token=<JWT>` | Authenticated | Live real-time alarm stream |

---

## 2. Core Data Contracts

### NormalizedDetection (`ai/detection/schemas.py`)
```json
{
  "class_id": 0,
  "class_name": "person",
  "confidence": 0.94,
  "bbox": [120.0, 240.0, 310.0, 580.0]
}
```

### Track (`ai/tracking/schemas.py`)
```json
{
  "track_id": 17,
  "class_id": 0,
  "class_name": "person",
  "confidence": 0.94,
  "bbox": [120.0, 240.0, 310.0, 580.0],
  "feet_position": [215.0, 580.0]
}
```

### EventPayload (`ai/events/schemas.py`)
```json
{
  "event_identifier": "EV-2026-000001",
  "event_type": "INTRUSION",
  "camera_id": "e4b2d35c-8dfa-4fb4-81d0-1e5b128dc90e",
  "zone_id": "a9e0f31c-3b9a-4c2d-9e1a-8c8872b90f11",
  "track_id": 17,
  "timestamp": "2026-08-29T16:30:00Z",
  "severity": "HIGH",
  "status": "NEW",
  "bounding_box": {"x1": 120, "y1": 240, "x2": 310, "y2": 580},
  "position": {"x": 215, "y": 580},
  "metadata": {"confidence": 0.94, "class_name": "person"}
}
```
