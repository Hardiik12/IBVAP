# IBVAP — API Specification & Data Contracts
## SIH Internal Round MVP

---

## 1. REST API Specifications

Base URL: `http://localhost:8000/api/v1`

### 1.1 System Health
`GET /health`
- **Description**: Returns operational status of the backend API and PostgreSQL database connection.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected",
  "timestamp": "2026-08-29T18:40:00Z"
}
```

---

### 1.2 Camera Management
`GET /cameras`
- **Description**: Returns all registered camera sources and status.
- **Response `200 OK`**:
```json
[
  {
    "id": "cam-01",
    "name": "Main Gate Webcam",
    "source_type": "webcam",
    "source_index": 0,
    "status": "ACTIVE",
    "created_at": "2026-08-29T10:00:00Z"
  }
]
```

---

### 1.3 Restricted Zones
`GET /cameras/{camera_id}/zones`
- **Description**: Returns defined polygon zones for a specific camera.
- **Response `200 OK`**:
```json
[
  {
    "id": "zone-alpha",
    "camera_id": "cam-01",
    "name": "Restricted Perimeter Zone A",
    "polygon": [
      [0.2, 0.3],
      [0.8, 0.3],
      [0.8, 0.9],
      [0.2, 0.9]
    ],
    "created_at": "2026-08-29T10:05:00Z"
  }
]
```

---

### 1.4 Events Ingestion & Log
`POST /events`
- **Description**: Ingestion endpoint called by the AI engine when an intrusion occurs.
- **Request Body**:
```json
{
  "camera_id": "cam-01",
  "zone_id": "zone-alpha",
  "event_type": "INTRUSION",
  "track_id": 17,
  "class_name": "person",
  "confidence": 0.93,
  "severity": "HIGH",
  "timestamp": "2026-08-29T18:42:10.150Z",
  "bbox": [120, 240, 310, 580],
  "evidence_snapshot": "base64_encoded_jpeg_string..."
}
```
- **Response `201 Created`**:
```json
{
  "event_id": "evt-99201",
  "alert_id": "alt-55102",
  "evidence_id": "evi-33104",
  "status": "PROCESSED"
}
```

`GET /events`
- **Description**: Query event history with optional pagination and filters.
- **Query Params**: `camera_id`, `event_type`, `limit`, `offset`.

---

### 1.5 Evidence Integrity & Verification
`GET /evidence/{evidence_id}`
- **Description**: Retrieve metadata, snapshot image URL, and stored SHA-256 hash for an evidence record.
- **Response `200 OK`**:
```json
{
  "evidence_id": "evi-33104",
  "event_id": "evt-99201",
  "file_path": "/data/evidence/evi-33104.jpg",
  "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "captured_at": "2026-08-29T18:42:10.150Z",
  "image_url": "/api/v1/evidence/evi-33104/image"
}
```

`POST /evidence/{evidence_id}/verify`
- **Description**: Recalculates SHA-256 hash of the evidence image file on disk and compares against stored hash.
- **Response `200 OK` (Verified)**:
```json
{
  "evidence_id": "evi-33104",
  "stored_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "current_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "status": "VERIFIED",
  "match": true,
  "verified_at": "2026-08-29T18:45:00.010Z"
}
```
- **Response `200 OK` (Tampered)**:
```json
{
  "evidence_id": "evi-33104",
  "stored_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "current_hash": "8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4",
  "status": "TAMPERED",
  "match": false,
  "verified_at": "2026-08-29T18:46:12.010Z"
}
```

---

## 2. WebSocket Specification

WebSocket URL: `ws://localhost:8000/ws/alerts`

### Connection Lifecycle
1. Client establishes WebSocket connection.
2. Server accepts and sends initial connection handshake message.
3. Upon any new `INTRUSION` event, server broadcasts JSON payload immediately to connected clients.

### Broadcast Alert Schema
```json
{
  "type": "NEW_ALERT",
  "alert_id": "alt-55102",
  "event_id": "evt-99201",
  "event_type": "INTRUSION",
  "camera_id": "cam-01",
  "zone_name": "Restricted Perimeter Zone A",
  "track_id": 17,
  "severity": "HIGH",
  "timestamp": "2026-08-29T18:42:10.155Z",
  "evidence_id": "evi-33104"
}
```

---

## 3. Error Handling

Standard HTTP Error Schema:
```json
{
  "detail": {
    "error_code": "RESOURCE_NOT_FOUND",
    "message": "Evidence record with ID 'evi-99999' was not found."
  }
}
```

| HTTP Status | Meaning | Usage |
| :--- | :--- | :--- |
| `400 Bad Request` | Invalid payload or polygon geometry | Malformed requests or invalid bounding boxes |
| `401 Unauthorized` | Missing/expired JWT bearer token | Protected routes accessed without token |
| `404 Not Found` | Resource ID does not exist | Invalid camera_id, event_id, or evidence_id |
| `500 Internal Error` | Server execution exception | Database crash or disk read error |
