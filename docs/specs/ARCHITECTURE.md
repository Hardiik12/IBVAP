# IBVAP — System Architecture & Pipeline Design
## SIH Internal Round MVP

---

## 1. High-Level Architecture Overview

IBVAP follows a decoupled, three-tier modular architecture:
1. **AI Processing Engine** (Stream Ingestion, Object Detection, Tracking, Spatial Logic, Event Generation)
2. **Backend Application Server** (FastAPI Service Layer, PostgreSQL Storage, Real-Time WebSockets, SHA-256 Verification Engine)
3. **Frontend Operational Dashboard** (Next.js Single Page Application, Video/Overlay Player, Alert Feed, Evidence Verification Modal)

```
                       +-----------------------------+
                       |   Physical / File Camera    |
                       +--------------+--------------+
                                      |
                                  Raw Frame
                                      v
+--------------------------------------------------------------------------+
|                            AI ENGINE (Python)                            |
|  +----------------+    +----------------+    +------------------------+  |
|  | OpenCV Reader  | -> | YOLOv8 Detect  | -> |  ByteTrack Tracker     |  |
|  +----------------+    +----------------+    +-----------+------------+  |
|                                                          |               |
|                                                     Track State          |
|                                                          v               |
|  +----------------+    +----------------+    +------------------------+  |
|  | Event Dispatch | <- | Event Engine   | <- | Polygon Zone Engine    |  |
|  +-------+--------+    +----------------+    +------------------------+  |
+----------|---------------------------------------------------------------+
           |
      HTTP Event Payload
           v
+--------------------------------------------------------------------------+
|                          BACKEND SERVER (FastAPI)                        |
|  +----------------+    +----------------+    +------------------------+  |
|  | REST API Router|    | Service Layer  |    | WebSocket Broadcaster  |  |
|  +-------+--------+    +-------+--------+    +-----------+------------+  |
|          |                     |                         |               |
|          v                     v                         |               |
|  +----------------+    +----------------+                |               |
|  |  PostgreSQL DB |    | SHA-256 Engine |                |               |
|  +----------------+    +----------------+                |               |
+----------------------------------------------------------|---------------+
                                                           |
                                               WebSocket / REST Data
                                                           v
+--------------------------------------------------------------------------+
|                     FRONTEND DASHBOARD (Next.js)                         |
|  +----------------+    +----------------+    +------------------------+  |
|  | Live Monitor   |    | Real-Time Feed |    | Evidence Verification  |  |
|  | Canvas Overlay |    | Alerts Table   |    | Tamper Inspector Modal |  |
|  +----------------+    +----------------+    +------------------------+  |
+--------------------------------------------------------------------------+
```

---

## 2. AI Processing Pipeline Lifecycle

### 2.1 Computer Vision Foundation (M2.1 Implemented Baseline)

The `ai/` module provides a decoupled, modular frame-processing pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                 CAMERA SOURCE ABSTRACTION                   │
│ 1. WebcamSource(camera_index)  OR  VideoFileSource(path)   │
│ 2. BaseCameraSource interface (open, read, release)         │
└──────────────────────────────┬──────────────────────────────┘
                               │ Read BGR numpy array frame
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      FRAME PROCESSOR                        │
│ 1. Validate Non-Null BGR Array & Positive Dimensions        │
│ 2. Perform Optional Frame Resizing (target_width, height)  │
│ 3. Extract FrameMetadata (frame_id, timestamp, width, height)│
│ 4. Compute Empirical Processing FPS (Sliding Window Timer)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ Processed Frame + Telemetry
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  PIPELINE RUNNER & PREVIEW                  │
│ 1. Render Diagnostic Telemetry Overlay (FPS, Res, Source)   │
│ 2. Display Live GUI Preview (cv2.imshow) OR Headless Mode   │
│ 3. Keyboard Shutdown Handler ('q' / ESC key)                │
│ 4. Safe Hardware Resource Cleanup (source.release())        │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 End-to-End Target AI Pipeline (Future Phases)

```
[Frame Capture] 
       │ 1. Read BGR numpy array frame from CameraSource
       ▼
[Detector Inference] 
       │ 2. YOLOv8 predicts bounding boxes, class IDs, confidences
       ▼
[Data Normalization] 
       │ 3. Format into NormalizedDetections: [x1, y1, x2, y2, conf, class_id]
       ▼
[Tracker Association] 
       │ 4. ByteTrack matches detections to active tracks, assigns persistent track_id
       ▼
[Spatial Point Math] 
       │ 5. Compute bottom-center reference point: (x_center = (x1+x2)/2, y_bottom = y2)
       ▼
[Zone Containment Test] 
       │ 6. OpenCV pointPolygonTest PIP checks point against active zone polygon
       ▼
[State Machine Evaluation] 
       │ 7. Compare current zone state with previous track state:
       │    - OUTSIDE -> INSIDE: Trigger INTRUSION Event & state = INSIDE
       │    - INSIDE  -> INSIDE: Maintain state (Suppress duplicate event)
       │    - INSIDE  -> OUTSIDE: Reset state = OUTSIDE
       ▼
[Event & Evidence Dispatch] 
            - Save snapshot frame to data/evidence/<id>.jpg
            - Post event payload + snapshot metadata to Backend API
```

---

## 3. Data Normalization Contracts

To prevent model lock-in, the AI engine enforces strict internal dataclass representations:

### 3.1 Normalized Detection Dict
```json
{
  "class_id": 0,
  "class_name": "person",
  "confidence": 0.92,
  "bbox": [150.0, 220.0, 310.0, 590.0]
}
```

### 3.2 Track State Object
```json
{
  "track_id": 17,
  "class_name": "person",
  "confidence": 0.92,
  "bbox": [150.0, 220.0, 310.0, 590.0],
  "reference_point": [230.0, 590.0],
  "current_zone_state": "INSIDE",
  "last_updated": "2026-08-29T18:30:00.100Z"
}
```

---

## 4. Evidence Hashing & Verification Pipeline

```
                     INTRUSION EVENT DETECTED
                                │
                                ▼
                     Save Frame Snapshot (.jpg)
                                │
                                ▼
                  Read Binary Image File Bytes
                                │
                                ▼
                 Compute SHA-256 Hash Digest
                  (64-character Hexadecimal)
                                │
                                ▼
              Save Record in Database (file_path + hash)
                                │
    ┌───────────────────────────┴───────────────────────────┐
    ▼                                                       ▼
[Verification Test]                                [Tamper Demonstration]
    │                                                       │
Read File Bytes from Disk                               Edit File Bytes / Save Copy
    │                                                       │
Compute Current SHA-256                                 Compute Current SHA-256
    │                                                       │
Compare (Current == Stored)                             Compare (Current == Stored)
    │                                                       │
    ▼                                                       ▼
Result: VERIFIED (Match)                                Result: TAMPERED (Mismatch)
```

---

## 5. Architectural Principles

1. **Separation of AI and Business Domain**: YOLO and ByteTrack do not know about database schemas or REST endpoints. They emit pure event data structures.
2. **Stateless Service Handlers**: Backend service layer methods maintain idempotency and do not hold transient camera state.
3. **Optimized DB I/O**: Frame detections are processed entirely in-memory; only structured security events, alerts, and evidence metadata are persisted to PostgreSQL.

---

## 6. Real-Time WebSocket Notification Architecture

IBVAP uses an in-process FastAPI WebSocket Connection Manager (`WebSocketManager`) to broadcast real-time security events to operational clients:

```
[AI Pipeline / Client]
         │
         │ HTTP POST /api/v1/events
         ▼
┌────────────────────────────────────────────────────────┐
│                   BACKEND SERVICE                      │
│ 1. EventService.create_event()                         │
│ 2. AlertService.create_alert_internal() (if INTRUSION) │
│ 3. db.commit() ─── Transaction Committed               │
└────────────────────────┬───────────────────────────────┘
                         │
        (Strictly Post-Commit Callback)
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│               NOTIFICATION SERVICE                     │
│ 1. Build JSON Payload (Event + Alert data)             │
│ 2. WebSocketManager.broadcast(payload)                 │
└────────────────────────┬───────────────────────────────┘
                         │
       ┌─────────────────┴─────────────────┐
       ▼                                   ▼
 [Client 1: OPERATOR]               [Client 2: ANALYST]
  WS /api/v1/ws/events               WS /api/v1/ws/events
```

### Architectural Directives
- **Post-Commit Guarantee**: Notifications trigger **only after database commit succeeds**, ensuring clients never receive phantom alerts for rolled-back transactions.
- **Database = Source of Truth**: WebSockets provide real-time ephemeral notifications. Historical state and missed messages during disconnections are fetched via REST APIs (`GET /api/v1/events` and `GET /api/v1/alerts`).
- **Query-Token Authentication**: WebSockets require `WS /api/v1/ws/events?token=<access_token>`. Invalid or expired tokens are closed immediately with code `1008` (Policy Violation).

---

## 7. End-to-End Integration Flow & Security Control Mapping

### 7.1 Cross-Component Data Lifecycle

```
┌───────────────────────────────────────────────────────────────────────────┐
│                       AI SIMULATOR / M2 PIPELINE                          │
│ 1. Authenticate via POST /api/v1/auth/login -> Receive JWT Token          │
│ 2. Construct Normalized Event JSON (camera_id, zone_id, track_id, etc.)  │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │ HTTP POST /api/v1/events
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                           M1 BACKEND SERVER                               │
│ 1. Validate JWT & Role Permissions (OPERATOR / ADMIN)                     │
│ 2. Validate Camera & Zone Existence + Camera/Zone Parent Relationship     │
│ 3. Atomic Transaction: Event Record Created + Alert Record Generated      │
│ 4. db.commit() ─── Transaction Committed                                  │
│ 5. Post-Commit Hook: NotificationService.notify_event_created()           │
└───────────────────┬───────────────────────────────────┬───────────────────┘
                    │ Broadcast                         │ Metadata
                    ▼                                   ▼
┌──────────────────────────────────────┐    ┌───────────────────────────────┐
│       WEBSOCKET BROADCASTER          │    │     EVIDENCE INTEGRITY        │
│ WS /api/v1/ws/events?token=<JWT>     │    │ 1. Store frame snapshot       │
│ Delivers real-time INTRUSION_ALERT   │    │ 2. Generate SHA-256 hash      │
│ JSON payload to active clients       │    │ 3. Verify integrity (VERIFIED)│
└──────────────────────────────────────┘    │ 4. Flag mutation (MISMATCH)   │
                                            └───────────────┬───────────────┘
                                                            │ Action Logged
                                                            ▼
                                            ┌───────────────────────────────┐
                                            │         AUDIT TRAIL           │
                                            │ Immutable AuditLog table      │
                                            │ tracks LOGIN, CAMERA, ZONE,   │
                                            │ ALERT_ACK, EVIDENCE_VERIFIED  │
                                            └───────────────────────────────┘
```

### 7.2 Security Architecture Mapping Matrix

| Security Layer / Control | Status | Implemented Mechanism (M1 MVP) | Proposed / Production Target |
| :--- | :--- | :--- | :--- |
| **Layer 1: Audit Logging** | **IMPLEMENTED** | Immutable `AuditLog` table, read-only endpoint, DELETE returns 405. | Centralized SIEM forwarding, syslog export. |
| **Layer 2: Evidence Integrity** | **IMPLEMENTED** | Server-side SHA-256 chunked hashing, directory traversal block, mismatch detection. | Hardware Security Module (HSM), digital signature certificates. |
| **Layer 3: Encryption** | **PROPOSED** | HTTP / WS (Development). | Mandatory HTTPS (TLS 1.3), WSS, AES-256 evidence disk encryption. |
| **Layer 4: Network Isolation** | **PROPOSED** | Localhost / docker network. | Air-gapped border network, VPC segmentation, firewall rules. |
| **Layer 5: Identity & Access** | **IMPLEMENTED** | Argon2id password hashing, JWT Bearer tokens, RBAC permissions matrix. | Multi-Factor Authentication (MFA), OAuth2 / OIDC SSO integration. |
| **Layer 6: System Hardening** | **IMPLEMENTED** | Path traversal protection, strict Pydantic `extra="forbid"`, admin self-deactivation block. | SELinux profiles, container vulnerability scanning, VAPT certification. |

---

## 8. Docker Compose Deployment Architecture (M3.2)

```
                        ┌───────────────────────────────┐
                        │      USER BROWSER (HOST)      │
                        │  Dashboard: localhost:3000   │
                        │  API / WS:  localhost:8000   │
                        └───────┬───────────────┬───────┘
                                │ HTTP          │ WS / REST
                                ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DOCKER COMPOSE (ibvap-network)                         │
│                                                                             │
│  ┌───────────────────────┐          ┌────────────────────────────────────┐  │
│  │   frontend:3000       │          │   backend:8000 (FastAPI)           │  │
│  │   Node 20 Alpine      │          │   Python 3.12-slim                 │  │
│  │   Next.js Standalone  │          │   Healthcheck: GET /health         │  │
│  └───────────────────────┘          └───────┬────────────────────▲───────┘  │
│                                             │                    │          │
│                                             │ SQLAlchemy 2.0     │ HTTP     │
│                                             │ :5432              │ REST/JWT │
│                                             ▼                    │          │
│                                     ┌───────────────┐    ┌───────┴───────┐  │
│                                     │ postgres:15   │    │ ai:latest     │  │
│                                     │ Alpine        │    │ YOLO + Byte   │  │
│                                     │ Volume:       │    │ Video Ingest  │  │
│                                     │ postgres_data │    └───────────────┘  │
│                                     └───────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Container Specifications
1. **`postgres` (`postgres:15-alpine`)**: Persistent volume `postgres_data`, readiness healthcheck via `pg_isready`.
2. **`backend` (`Python 3.12-slim`)**: Non-root `appuser`, runs Alembic migrations on startup, conditionally seeds demo data via `RUN_SEED=true`, exposes REST & WebSocket on port `8000`.
3. **`ai` (`Python 3.12-slim`)**: Non-root `appuser`, pre-flight backend connectivity validation, OpenCV/YOLO/ByteTrack processing on video streams mounted read-only from `./data/videos`.
4. **`frontend` (`Node 20-alpine`)**: Non-root `nextjs` user, production Next.js dashboard exposed on port `3000`.



