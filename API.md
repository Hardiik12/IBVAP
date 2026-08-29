# IBVAP — API Specification & Data Contracts
## SIH Internal Round MVP

---

## 1. REST API Specifications

Base URL: `http://localhost:8000/api/v1`

### 1.1 System Health
`GET /health` (Exposed at root)
- **Description**: Returns operational status of the backend API.
- **Response `200 OK`**:
```json
{
  "status": "ok",
  "service": "ibvap-backend",
  "version": "0.1.0"
}
```

---

### 1.2 Camera Management

#### List Cameras
`GET /api/v1/cameras`
- **Query Params**: `is_active` (boolean, optional)
- **Response `200 OK`**:
```json
[
  {
    "id": "e4b2d35c-8dfa-4fb4-81d0-1e5b128dc90e",
    "name": "Main Gate Webcam",
    "camera_identifier": "cam-webcam-01",
    "source_type": "WEBCAM",
    "source_url": "0",
    "location": "Demo Area A",
    "is_active": true,
    "created_at": "2026-08-29T10:00:00Z",
    "updated_at": "2026-08-29T10:00:00Z"
  }
]
```

#### Create Camera
`POST /api/v1/cameras`
- **Request Body**:
```json
{
  "name": "Main Gate Webcam",
  "camera_identifier": "cam-webcam-01",
  "source_type": "WEBCAM",
  "source_url": "0",
  "location": "Demo Area A",
  "is_active": true
}
```
- **Response `201 Created`**: Returns created camera object.
- **Response `409 Conflict`** (Duplicate identifier):
```json
{
  "error": {
    "status_code": 409,
    "message": "Camera identifier already exists"
  }
}
```

#### Get Camera by ID
`GET /api/v1/cameras/{camera_id}`
- **Response `200 OK`**: Returns camera details.
- **Response `404 Not Found`**:
```json
{
  "error": {
    "status_code": 404,
    "message": "Camera not found"
  }
}
```

#### Update Camera
`PATCH /api/v1/cameras/{camera_id}`
- **Request Body**: (All fields optional)
```json
{
  "name": "Updated Main Gate Webcam",
  "is_active": false
}
```
- **Response `200 OK`**: Returns updated camera object.

#### Delete Camera (Soft-Deactivation)
`DELETE /api/v1/cameras/{camera_id}`
- **Description**: Marks `is_active = false` to preserve security event audit history (ADR-009).
- **Response `200 OK`**: Returns deactivated camera object.

---

### 1.3 Restricted Zones

#### List Camera Zones
`GET /api/v1/cameras/{camera_id}/zones`
- **Query Params**: `is_active` (boolean, optional)
- **Response `200 OK`**:
```json
[
  {
    "id": "a9e0f31c-3b9a-4c2d-9e1a-8c8872b90f11",
    "camera_id": "e4b2d35c-8dfa-4fb4-81d0-1e5b128dc90e",
    "name": "Perimeter Restricted Zone A",
    "zone_type": "RESTRICTED",
    "polygon": [
      [0.2, 0.3],
      [0.8, 0.3],
      [0.8, 0.9],
      [0.2, 0.9]
    ],
    "is_active": true,
    "created_at": "2026-08-29T10:05:00Z",
    "updated_at": "2026-08-29T10:05:00Z"
  }
]
```

#### Create Zone
`POST /api/v1/cameras/{camera_id}/zones`
- **Request Body**:
```json
{
  "name": "Perimeter Restricted Zone A",
  "zone_type": "RESTRICTED",
  "polygon": [
    [0.2, 0.3],
    [0.8, 0.3],
    [0.8, 0.9],
    [0.2, 0.9]
  ],
  "is_active": true
}
```
- **Response `201 Created`**: Returns created zone object.
- **Response `422 Unprocessable Entity`** (Invalid polygon format):
```json
{
  "detail": [
    {
      "loc": ["body", "polygon"],
      "msg": "Polygon must contain at least 3 points to form a closed shape",
      "type": "value_error"
    }
  ]
}
```

#### Get Zone by ID
`GET /api/v1/zones/{zone_id}`
- **Response `200 OK`**: Returns zone details.
- **Response `404 Not Found`**:
```json
{
  "error": {
    "status_code": 404,
    "message": "Zone not found"
  }
}
```

#### Update Zone
`PATCH /api/v1/zones/{zone_id}`
- **Request Body**: (All fields optional, validates polygon if supplied)
```json
{
  "name": "Adjusted Perimeter Zone A",
  "polygon": [
    [0.3, 0.3],
    [0.7, 0.3],
    [0.7, 0.7],
    [0.3, 0.7]
  ]
}
```
- **Response `200 OK`**: Returns updated zone object.

#### Delete Zone (Soft-Deactivation)
`DELETE /api/v1/zones/{zone_id}`
- **Description**: Marks `is_active = false` to preserve historical integrity (ADR-009).
- **Response `200 OK`**: Returns deactivated zone object.

---

### 1.4 Events Management

#### Create Event
`POST /api/v1/events`
- **Description**: Ingests a new security event from the AI tracking system. If the event type is `INTRUSION`, it automatically creates an associated active Alert within a single database transaction.
- **Request Body**:
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
  "bounding_box": {
    "x1": 420,
    "y1": 210,
    "x2": 510,
    "y2": 480
  },
  "position": {
    "x": 465,
    "y": 480
  },
  "metadata": {
    "source": "ai_pipeline"
  }
}
```
- **Response `201 Created`**:
```json
{
  "id": "f8a0928b-b8da-4fc4-8e10-3d9a108dc220",
  "event_identifier": "EV-2026-000001",
  "event_type": "INTRUSION",
  "camera_id": "e4b2d35c-8dfa-4fb4-81d0-1e5b128dc90e",
  "zone_id": "a9e0f31c-3b9a-4c2d-9e1a-8c8872b90f11",
  "track_id": 17,
  "timestamp": "2026-08-29T16:30:00Z",
  "severity": "HIGH",
  "status": "NEW",
  "bounding_box": {
    "x1": 420,
    "y1": 210,
    "x2": 510,
    "y2": 480
  },
  "position": {
    "x": 465,
    "y": 480
  },
  "metadata": {
    "source": "ai_pipeline"
  },
  "created_at": "2026-08-29T16:30:01Z",
  "alert_id": "b3e0921a-289a-4fdf-9e11-1c1a890dc221"
}
```
- **Response `409 Conflict`** (Mismatched camera/zone pairing):
```json
{
  "error": {
    "status_code": 409,
    "message": "Zone does not belong to camera"
  }
}
```

#### List Events
`GET /api/v1/events`
- **Query Params**: `camera_id` (str), `zone_id` (str), `event_type` (str), `severity` (str), `status` (str), `start_time` (ISO UTC), `end_time` (ISO UTC), `limit` (default 20, max 100), `offset` (default 0).
- **Response `200 OK`**: Returns list of matching events, sorted by `timestamp DESC`.

#### Get Event by ID
`GET /api/v1/events/{event_id}`
- **Response `200 OK`**: Returns event details.
- **Response `404 Not Found`**: Returns standard not found error.

#### Update Event
`PATCH /api/v1/events/{event_id}`
- **Description**: Updates mutable event fields (`status`, `severity`, `metadata`). Attempting to update immutable fields (such as `camera_id` or `event_identifier`) is rejected with `422 Unprocessable Entity` (ADR-010).
- **Request Body**:
```json
{
  "status": "PROCESSED",
  "metadata": {
    "source": "ai_pipeline",
    "notes": "Verified intrusion by Operator 3"
  }
}
```
- **Response `200 OK`**: Returns updated event details.

#### Delete Event
`DELETE /api/v1/events/{event_id}`
- **Response `405 Method Not Allowed`**: Security events are immutable logs and cannot be deleted.

---

### 1.5 Alerts Management

#### List Alerts
`GET /api/v1/alerts`
- **Query Params**: `status` (str), `severity` (str), `camera_id` (str), `limit` (default 20, max 100), `offset` (default 0).
- **Response `200 OK`**: Returns a list of generated alerts, sorted by `created_at DESC`.

#### Get Alert by ID
`GET /api/v1/alerts/{alert_id}`
- **Response `200 OK`**: Returns alert details.

#### Update Alert
`PATCH /api/v1/alerts/{alert_id}`
- **Description**: Updates alert status (e.g., `ACKNOWLEDGED`, `RESOLVED`). Changing status to `ACKNOWLEDGED` automatically populates the `acknowledged_at` UTC timestamp.
- **Request Body**:
```json
{
  "status": "ACKNOWLEDGED",
  "acknowledged_by": "a4d3f35c-8dfa-4fb4-81d0-1e5b128dc90e"
}
```
- **Response `200 OK`**:
```json
{
  "id": "b3e0921a-289a-4fdf-9e11-1c1a890dc221",
  "event_id": "f8a0928b-b8da-4fc4-8e10-3d9a108dc220",
  "severity": "HIGH",
  "status": "ACKNOWLEDGED",
  "message": "Intrusion detected in restricted zone.",
  "created_at": "2026-08-29T16:30:01Z",
  "acknowledged_at": "2026-08-29T16:32:44Z",
  "acknowledged_by": "a4d3f35c-8dfa-4fb4-81d0-1e5b128dc90e"
}
```

---

### 1.6 Evidence Management

#### Associate Evidence with Event
`POST /api/v1/events/{event_id}/evidence`
- **Request Body**:
```json
{
  "evidence_identifier": "EVD-2026-000001",
  "file_path": "evidence/events/EV-2026-000001/frame_001.jpg",
  "captured_at": "2026-08-29T17:30:00Z",
  "metadata": {
    "source": "camera",
    "capture_type": "snapshot"
  }
}
```
- **Response `201 Created`**:
```json
{
  "id": "a9e0f31c-3b9a-4c2d-9e1a-8c8872b90f11",
  "evidence_identifier": "EVD-2026-000001",
  "event_id": "f8a0928b-b8da-4fc4-8e10-3d9a108dc220",
  "file_path": "evidence/events/EV-2026-000001/frame_001.jpg",
  "captured_at": "2026-08-29T17:30:00Z",
  "created_at": "2026-08-29T17:30:01Z",
  "sha256_hash": "",
  "metadata": {
    "source": "camera",
    "capture_type": "snapshot"
  }
}
```

#### List Event Evidence
`GET /api/v1/events/{event_id}/evidence`
- **Response `200 OK`**: Returns a list of evidence records associated with the specified event, sorted by `captured_at ASC`.

#### Get Evidence by ID
`GET /api/v1/evidence/{evidence_id}`
- **Response `200 OK`**: Returns evidence details.

#### Update Evidence
`PATCH /api/v1/evidence/{evidence_id}`
- **Description**: Updates mutable evidence fields (`metadata`). Attempting to update immutable fields (such as `evidence_identifier`, `event_id`, `file_path`, `captured_at`, or `sha256_hash`) is rejected with `422 Unprocessable Entity`.
- **Request Body**:
```json
{
  "metadata": {
    "source": "camera",
    "capture_type": "snapshot",
    "notes": "Verified frame contains target person"
  }
}
```
- **Response `200 OK`**: Returns updated evidence details.

#### Delete Evidence
`DELETE /api/v1/evidence/{evidence_id}`
- **Response `405 Method Not Allowed`**: Evidence records are immutable security logs and cannot be deleted.

### 1.7 Evidence Integrity Verification

#### Generate Evidence Hash
`POST /api/v1/evidence/{evidence_id}/hash`
- **Description**: Generates and persists the cryptographic SHA-256 hash for existing evidence based on the physical file stored on disk.
- **Response `200 OK`** (New Hash Generated):
```json
{
  "id": "a9e0f31c-3b9a-4c2d-9e1a-8c8872b90f11",
  "evidence_identifier": "EVD-2026-000001",
  "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "status": "HASHED"
}
```
- **Response `200 OK`** (Already Hashed - Idempotent):
```json
{
  "id": "a9e0f31c-3b9a-4c2d-9e1a-8c8872b90f11",
  "evidence_identifier": "EVD-2026-000001",
  "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "status": "ALREADY_HASHED"
}
```
- **Response `404 Not Found`** (Missing file on disk or invalid evidence ID):
```json
{
  "error": {
    "status_code": 404,
    "message": "Evidence file not found on disk"
  }
}
```

#### Verify Evidence Integrity
`GET /api/v1/evidence/{evidence_id}/verify`
- **Description**: Recalculates the current SHA-256 hash of the physical file on disk and compares it with the stored hash to check for modifications.
- **Response `200 OK`** (Verified Content):
```json
{
  "evidence_id": "a9e0f31c-3b9a-4c2d-9e1a-8c8872b90f11",
  "verified": true,
  "status": "VERIFIED",
  "stored_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "current_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```
- **Response `200 OK`** (Mismatch / Tampered Content):
```json
{
  "evidence_id": "a9e0f31c-3b9a-4c2d-9e1a-8c8872b90f11",
  "verified": false,
  "status": "MISMATCH",
  "stored_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "current_hash": "f62b8813a1a5b14e9af13c9df924e2e2a1ae3855a121e7d825ff5e0ea28876c1"
}
```
- **Response `200 OK`** (Not Hashed Yet):
```json
{
  "evidence_id": "a9e0f31c-3b9a-4c2d-9e1a-8c8872b90f11",
  "verified": false,
  "status": "NOT_HASHED"
}
```
- **Response `400 Bad Request`** (Path traversal attempt detected):
```json
{
  "error": {
    "status_code": 400,
    "message": "Path traversal attempt detected"
  }
}
---

### 1.8 Authentication

#### User Login
`POST /api/v1/auth/login`
- **Request Body**:
```json
{
  "username_or_email": "admin_user",
  "password": "AdminSecret123!"
}
```
- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```
- **Response `401 Unauthorized`** (Generic Failure):
```json
{
  "error": {
    "status_code": 401,
    "message": "Invalid credentials"
  }
}
```

#### Current User Profile
`GET /api/v1/auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**:
```json
{
  "id": "admin-uuid-001",
  "username": "admin_user",
  "email": "admin@ibvap.test",
  "role": "ADMINISTRATOR",
  "is_active": true,
  "created_at": "2026-08-29T18:00:00Z",
  "updated_at": "2026-08-29T18:00:00Z"
}
```

---

### 1.9 User Management (Administrator Only)

#### Create User
`POST /api/v1/users`
- **Headers**: `Authorization: Bearer <admin_token>`
- **Request Body**:
```json
{
  "username": "new_operator",
  "email": "operator@ibvap.test",
  "password": "SecurePassword123!",
  "role": "OPERATOR"
}
```
- **Response `201 Created`**: Returns created user details (excluding `password_hash`).

#### List Users
`GET /api/v1/users`
- **Headers**: `Authorization: Bearer <admin_token>`
- **Query Params**: `limit` (default 20), `offset` (default 0).
- **Response `200 OK`**: Returns paginated user list.

#### Update User
`PATCH /api/v1/users/{user_id}`
- **Headers**: `Authorization: Bearer <admin_token>`
- **Request Body**:
```json
{
  "email": "updated_operator@ibvap.test",
  "is_active": false
}
```
- **Response `400 Bad Request`**: Returned if attempting to deactivate/demote the last active administrator.

---

### 1.10 Audit Logs (Administrator & Auditor Only)

#### List Audit Logs
`GET /api/v1/audit-logs`
- **Headers**: `Authorization: Bearer <token>`
- **Query Params**: `user_id`, `action`, `resource_type`, `start_time`, `end_time`, `limit`, `offset`.
- **Response `200 OK`**:
```json
[
  {
    "id": "audit-uuid-001",
    "user_id": "operator-uuid-001",
    "action": "EVIDENCE_VERIFIED",
    "resource_type": "EVIDENCE",
    "resource_id": "evi-9910",
    "timestamp": "2026-08-29T19:10:00Z",
    "metadata": {
      "status": "VERIFIED",
      "verified": true
    }
  }
]
```

---

## 2. WebSocket Specification (IMPLEMENTED)

- **WebSocket URL**: `ws://localhost:8000/api/v1/ws/events?token=<jwt_access_token>`
- **Authentication**: JWT Access Token passed via `token` query parameter. Connections without valid active tokens or with unauthorized roles are closed immediately with code `1008` (`WS_1008_POLICY_VIOLATION`).
- **Allowed Roles**: `OPERATOR`, `ANALYST`, `ADMINISTRATOR`, `AUDITOR`.

### Real-Time Intrusion Alert Payload
When an `INTRUSION` event is created and committed to the database, a single coherent notification message containing both event and generated alert attributes is broadcast to all connected WebSocket clients.

```json
{
  "type": "INTRUSION_ALERT",
  "timestamp": "2026-08-29T20:00:00Z",
  "event": {
    "id": "e4a77a98-8c10-410d-852a-995b28d7a123",
    "event_identifier": "EV-WS-INTRUSION-01",
    "event_type": "INTRUSION",
    "camera_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "zone_id": null,
    "track_id": 99,
    "timestamp": "2026-08-29T20:00:00Z",
    "severity": "HIGH",
    "status": "NEW",
    "bounding_box": null,
    "position": null,
    "metadata": null,
    "created_at": "2026-08-29T20:00:00.123456Z",
    "alert_id": "b1ff8b09-9d21-421e-963b-006c39e8b456"
  },
  "alert": {
    "id": "b1ff8b09-9d21-421e-963b-006c39e8b456",
    "event_id": "e4a77a98-8c10-410d-852a-995b28d7a123",
    "severity": "HIGH",
    "status": "ACTIVE",
    "message": "Intrusion detected on camera a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "created_at": "2026-08-29T20:00:00.123456Z",
    "acknowledged_at": null,
    "acknowledged_by": null
  }
}
```

### Reconnection & REST Fallback Strategy
WebSocket connections are transient notifications. If a client disconnects or misses notifications during network drops:
1. The server automatically cleans up dead connection handles without interrupting active clients or throwing unhandled exceptions.
2. The client re-authenticates and reconnects to `ws://localhost:8000/api/v1/ws/events?token=<access_token>`.
3. The client fetches historical events and alerts using standard REST API endpoints (`GET /api/v1/events` and `GET /api/v1/alerts`).

---

## 3. Error Handling

Standard HTTP Error Schema:
```json
{
  "error": {
    "status_code": 404,
    "message": "Resource not found"
  }
}
```

| HTTP Status | Meaning | Usage |
| :--- | :--- | :--- |
| `400 Bad Request` | Invalid payload or polygon geometry | Malformed requests or invalid bounding boxes |
| `401 Unauthorized` | Missing/expired JWT bearer token | Protected routes accessed without token |
| `404 Not Found` | Resource ID does not exist | Invalid camera_id, event_id, or evidence_id |
| `409 Conflict` | Uniqueness violation or camera/zone mismatch | Duplicate event_identifier or zone on another camera |
| `422 Unprocessable Entity` | Pydantic schema validation error | Invalid UUID format or bounding box syntax |
| `500 Internal Error` | Server execution exception | Database write failure |

---

## 4. AI Engine → Backend Integration Contract (M2 → M1 Interface)

The future M2 AI Pipeline (YOLOv8 + ByteTrack) will interface with the M1 Backend strictly by emitting normalized JSON payloads via `POST /api/v1/events`.

### Contract Directives
1. **Model Decoupling**: The backend remains completely independent of YOLO model architectures, ByteTrack tracker logic, OpenCV capture mechanisms, and CUDA/GPU hardware.
2. **Normalized Payload Specification**:
```json
{
  "event_identifier": "EV-2026-0829-0001",
  "event_type": "INTRUSION",
  "camera_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "zone_id": "c1f77b99-1c0b-4ef8-bb6d-8bb9bd380a22",
  "track_id": 17,
  "timestamp": "2026-08-29T20:30:00Z",
  "severity": "HIGH",
  "status": "NEW",
  "bounding_box": {"x1": 420, "y1": 210, "x2": 510, "y2": 480},
  "position": {"x": 465, "y": 480},
  "metadata": {
    "confidence": 0.96,
    "class_name": "person",
    "inference_fps": 31.4
  }
}
```
3. **Authentication**: The AI engine pipeline must authenticate via `POST /api/v1/auth/login` during initialization and attach `Authorization: Bearer <access_token>` headers to all REST event posts.

