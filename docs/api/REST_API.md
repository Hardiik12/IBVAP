# IBVAP REST API Specification

**Base URL:** `http://localhost:8000/api/v1`  
**Authentication:** Bearer JWT in `Authorization: Bearer <token>` header  
**Response Formats:** `application/json`  

---

## 1. System & Health Endpoints

### Health Check
- **`GET /health`** (Root level)
- **Permissions:** Public
- **Response `200 OK`**:
```json
{
  "status": "ok",
  "service": "ibvap-backend",
  "version": "0.1.0"
}
```

---

## 2. Authentication & MFA

### Password Authentication
- **`POST /api/v1/auth/login`**
- **Request Body:**
```json
{
  "username_or_email": "operator_user",
  "password": "OperatorSecret123!"
}
```
- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Current User Profile
- **`GET /api/v1/auth/me`**
- **Headers:** `Authorization: Bearer <token>`
- **Response `200 OK`**: Returns current user object (excluding password hashes).

### TOTP Multi-Factor Authentication
- **`POST /api/v1/mfa/verify`**
- **Request Body:**
```json
{
  "user_id": "usr-uuid-001",
  "totp_code": "123456"
}
```
- **Response `200 OK`**: Upgrades session token to `fully_authenticated`.

### Biometric Facial Verification
- **`POST /api/v1/face-auth/verify`**
- **Request Body:** Form data with user_id and webcam frame image.
- **Response `200 OK`**: Returns match status and cosine similarity score.

---

## 3. Camera Fleet Management

### List Cameras
- **`GET /api/v1/cameras`**
- **Query Params:** `is_active` (boolean, optional)
- **Permissions:** All authenticated users (`ADMINISTRATOR`, `OPERATOR`, `ANALYST`, `AUDITOR`)

### Create Camera
- **`POST /api/v1/cameras`**
- **Permissions:** `ADMINISTRATOR` only
- **Request Body:**
```json
{
  "name": "Perimeter Sector Alpha",
  "camera_identifier": "cam-01",
  "source_type": "WEBCAM",
  "source_url": "0",
  "location": "North Fence Line",
  "is_active": true
}
```

### Get / Update / Deactivate Camera
- **`GET /api/v1/cameras/{id}`**
- **`PATCH /api/v1/cameras/{id}`** (`ADMINISTRATOR` only)
- **`DELETE /api/v1/cameras/{id}`** (`ADMINISTRATOR` only — soft deactivation)

---

## 4. Exclusion Zone Geofencing

### List Zones for Camera
- **`GET /api/v1/cameras/{camera_id}/zones`**
- **Response `200 OK`**: Array of polygon zone configurations.

### Create Zone
- **`POST /api/v1/cameras/{camera_id}/zones`**
- **Permissions:** `ADMINISTRATOR`, `OPERATOR`
- **Request Body:**
```json
{
  "name": "Restricted Sector 1",
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

---

## 5. Security Events & Intrusion Ingestion

### Ingest AI Event
- **`POST /api/v1/events`**
- **Permissions:** `ADMINISTRATOR`, `OPERATOR` (AI Service Account)
- **Request Body:**
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
  "bounding_box": {"x1": 420, "y1": 210, "x2": 510, "y2": 480},
  "position": {"x": 465, "y": 480},
  "metadata": {"source": "ai_pipeline"}
}
```

### List Events
- **`GET /api/v1/events`**
- **Query Params:** `camera_id`, `zone_id`, `event_type`, `severity`, `status`, `start_time`, `end_time`, `limit`, `offset`.

---

## 6. Operational Alerts Workflow

### List Alerts
- **`GET /api/v1/alerts`**
- **Query Params:** `status`, `severity`, `camera_id`, `limit`, `offset`.

### Acknowledge / Resolve Alert
- **`PATCH /api/v1/alerts/{id}`**
- **Permissions:** `ADMINISTRATOR`, `OPERATOR`
- **Request Body:**
```json
{
  "status": "ACKNOWLEDGED",
  "acknowledged_by": "usr-uuid-001"
}
```

---

## 7. Forensic Evidence & Tamper Verification

### List Event Evidence
- **`GET /api/v1/events/{event_id}/evidence`**

### Verify Evidence SHA-256 Hash
- **`GET /api/v1/evidence/{evidence_id}/verify`**
- **Permissions:** All authenticated users (`ADMINISTRATOR`, `OPERATOR`, `ANALYST`, `AUDITOR`)
- **Response `200 OK`**:
```json
{
  "evidence_id": "evi-uuid-001",
  "verified": true,
  "status": "VERIFIED",
  "stored_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "current_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

---

## 8. Immutable Audit Trail

### List Audit Logs
- **`GET /api/v1/audit-logs`**
- **Permissions:** `ADMINISTRATOR`, `ANALYST`, `AUDITOR`
- **Query Params:** `user_id`, `action`, `resource_type`, `start_time`, `end_time`, `limit`, `offset`.
