# IBVAP Backend Service

FastAPI-based backend application server for the Intelligent Border Video Analytics Platform (IBVAP).

---

## 🛠️ Technology Stack
- **Python**: 3.11+
- **Framework**: FastAPI 0.115+
- **ASGI Server**: Uvicorn
- **Database**: PostgreSQL 16 (via Docker Compose)
- **ORM & Migrations**: SQLAlchemy 2.0 & Alembic
- **Validation & Settings**: Pydantic v2 & Pydantic-Settings
- **Testing**: Pytest & HTTPX TestClient

---

## 📁 Repository Structure
```
backend/
├── app/
│   ├── main.py            # FastAPI application entrypoint & error handlers
│   ├── core/
│   │   ├── config.py      # Environment configuration (Pydantic Settings)
│   │   └── logging.py     # Structured application logging
│   ├── db/
│   │   ├── database.py    # SQLAlchemy engine & sessionmaker factory
│   │   ├── base.py        # Declarative ORM Base class
│   │   └── seed.py        # Development demo seed script
│   ├── models/            # SQLAlchemy database models
│   │   ├── enums.py       # Reusable domain enums
│   │   ├── camera.py      # Camera entity
│   │   ├── zone.py        # Zone entity (Polygon coordinates)
│   │   ├── event.py       # Event entity (Intrusion, Track ID)
│   │   ├── alert.py       # Alert entity (1:1 with Event)
│   │   ├── evidence.py    # Evidence entity (SHA-256 metadata, RESTRICT delete)
│   │   ├── user.py        # User entity (RBAC, password_hash)
│   │   └── audit_log.py   # Audit log entity
│   ├── schemas/           # Pydantic API validation schemas
│   │   ├── camera.py      # Camera creation & response validation
│   │   └── zone.py        # Polygon validation rules & zone schemas
│   ├── api/
│   │   ├── api.py         # Centralized API router registry
│   │   └── routes/        # REST API controllers
│   │       ├── cameras.py # Camera CRUD routes
│   │       └── zones.py   # Zone CRUD routes
│   ├── services/          # Business logic handlers
│   │   ├── camera_service.py
│   │   └── zone_service.py
│   └── utils/             # Hashing & helper utilities
├── migrations/            # Alembic database migration scripts
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 2026_08_29_0000-phase2_database_models.py
├── tests/
│   ├── conftest.py        # Pytest fixtures & in-memory SQLite overrides
│   ├── api/               # API route tests (test_health.py, test_cameras.py, test_zones.py)
│   └── unit/              # Unit tests (test_config.py, test_models.py)
├── alembic.ini            # Alembic configuration
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development & testing dependencies
├── .env.example           # Environment template
└── README.md
```

---

## 🚀 Setup & Execution

### 1. Environment Setup
```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Database Migrations & Seed Data
Start PostgreSQL:
```bash
docker compose up -d postgres
```
Apply migrations:
```bash
alembic upgrade head
```
Seed initial demo data:
```bash
python -m app.db.seed
```

### 4. Run FastAPI Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
- **Root Metadata**: `http://localhost:8000/`
- **Health Check**: `http://localhost:8000/health`
- **Interactive OpenAPI Docs**: `http://localhost:8000/docs`

### 5. Run Pytest Suite
```bash
pytest tests/
```

---

## 🚦 REST API Usage Examples

### 1. Cameras API

#### Create a Camera Feed
```bash
curl -X POST "http://localhost:8000/api/v1/cameras" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Internal Demo Camera",
       "camera_identifier": "cam-webcam-01",
       "source_type": "WEBCAM",
       "location": "Demo Area",
       "is_active": true
     }'
```

#### List Active Cameras
```bash
curl "http://localhost:8000/api/v1/cameras?is_active=true"
```

#### Update a Camera location
```bash
curl -X PATCH "http://localhost:8000/api/v1/cameras/{camera_id}" \
     -H "Content-Type: application/json" \
     -d '{"location": "North Entrance Fence"}'
```

#### Soft Deactivate a Camera
```bash
curl -X DELETE "http://localhost:8000/api/v1/cameras/{camera_id}"
```

---

### 2. Zones API

#### Create a Polygon Restricted Zone
```bash
curl -X POST "http://localhost:8000/api/v1/cameras/{camera_id}/zones" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Perimeter Restricted Zone A",
       "zone_type": "RESTRICTED",
       "polygon": [
         [0.20, 0.30],
         [0.80, 0.30],
         [0.80, 0.80],
         [0.20, 0.80]
       ],
       "is_active": true
     }'
```

#### List Zones for a Camera
```bash
curl "http://localhost:8000/api/v1/cameras/{camera_id}/zones"
```

#### Update a Zone Polygon
```bash
curl -X PATCH "http://localhost:8000/api/v1/zones/{zone_id}" \
     -H "Content-Type: application/json" \
     -d '{
       "polygon": [
         [0.30, 0.30],
         [0.70, 0.30],
         [0.70, 0.70],
         [0.30, 0.70]
       ]
     }'
```

---

### 3. Events API

#### Ingest a New Security Event
```bash
curl -X POST "http://localhost:8000/api/v1/events" \
     -H "Content-Type: application/json" \
     -d '{
       "event_identifier": "EV-2026-0001",
       "event_type": "INTRUSION",
       "camera_id": "{camera_uuid}",
       "zone_id": "{zone_uuid}",
       "track_id": 17,
       "timestamp": "2026-08-29T16:30:00Z",
       "severity": "HIGH",
       "status": "NEW",
       "bounding_box": {"x1": 420, "y1": 210, "x2": 510, "y2": 480},
       "position": {"x": 465, "y": 480},
       "metadata": {"pipeline": "yolov8_bytetrack"}
     }'
```

#### List Events (Newest First)
```bash
curl "http://localhost:8000/api/v1/events?camera_id={camera_uuid}&limit=10&offset=0"
```

#### Update Event Status
```bash
curl -X PATCH "http://localhost:8000/api/v1/events/{event_uuid}" \
     -H "Content-Type: application/json" \
     -d '{"status": "PROCESSED"}'
```

---

### 4. Alerts API

#### List Active Intrusion Alerts
```bash
curl "http://localhost:8000/api/v1/alerts?status=ACTIVE&limit=10"
```

#### Acknowledge an Alert
```bash
curl -X PATCH "http://localhost:8000/api/v1/alerts/{alert_uuid}" \
     -H "Content-Type: application/json" \
     -d '{"status": "ACKNOWLEDGED", "acknowledged_by": "{user_uuid}"}'
```

---

### 5. Evidence API

#### Associate Evidence with an Event
```bash
curl -X POST "http://localhost:8000/api/v1/events/{event_uuid}/evidence" \
     -H "Content-Type: application/json" \
     -d '{
       "evidence_identifier": "EVD-2026-0001",
       "file_path": "evidence/events/EV-2026-0001/frame_001.jpg",
       "captured_at": "2026-08-29T17:30:00Z",
       "metadata": {"pipeline": "camera", "capture_type": "snapshot"}
     }'
```

#### List Evidence for an Event
```bash
curl "http://localhost:8000/api/v1/events/{event_uuid}/evidence"
```

#### Get Evidence Details
```bash
curl "http://localhost:8000/api/v1/evidence/{evidence_uuid}"
```

#### Update Evidence Metadata
```bash
curl -X PATCH "http://localhost:8000/api/v1/evidence/{evidence_uuid}" \
     -H "Content-Type: application/json" \
     -d '{"metadata": {"pipeline": "camera", "notes": "verified entry"}}'
```

#### Generate Evidence Cryptographic SHA-256 Hash
```bash
curl -X POST "http://localhost:8000/api/v1/evidence/{evidence_uuid}/hash"
```

#### Verify Evidence Integrity & Check for Tampering
```bash
curl "http://localhost:8000/api/v1/evidence/{evidence_uuid}/verify"
```

---

## 🔬 Evidence Integrity Demonstration Script
To verify the tamper-detection capabilities of the platform:
1. **Store Evidence**: Create an evidence metadata record via `POST /api/v1/events/{event_id}/evidence` with a `file_path` (e.g. `frame_001.jpg`).
2. **Place physical file**: Store a mock snapshot file (e.g. JPEG, text) inside the `data/evidence/` directory at the matching path.
3. **Generate Hash**: Run `POST /api/v1/evidence/{evidence_id}/hash` to compute the SHA-256 digest of the physical file and persist it.
4. **Verify Original**: Run `GET /api/v1/evidence/{evidence_id}/verify` and confirm the response status is `VERIFIED`.
5. **Simulate Tampering**: Edit the physical file manually inside `data/evidence/` to change its contents.
6. **Verify Tampered**: Run `GET /api/v1/evidence/{evidence_id}/verify` again and confirm it returns `MISMATCH`, indicating the evidence has been tampered with.
7. **Restore & Verify**: Revert the physical file contents back to the original content and verify again to see the status return to `VERIFIED`.

### 6. Authentication & User Management API

#### User Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username_or_email": "admin_user", "password": "AdminSecret123!"}'
```

#### Get Current User Profile
```bash
curl "http://localhost:8000/api/v1/auth/me" \
     -H "Authorization: Bearer <access_token>"
```

#### List Audit Logs (Admin/Auditor Only)
```bash
curl "http://localhost:8000/api/v1/audit-logs" \
     -H "Authorization: Bearer <access_token>"
```

---

### 7. Real-Time WebSocket API

#### Connect to Real-Time Event & Alert Stream
```bash
# Connect using wscat CLI tool or browser WebSocket client
wscat -c "ws://localhost:8000/api/v1/ws/events?token=<access_token>"
```
*(On database commit of an `INTRUSION` event, a single real-time JSON message containing event & alert attributes is broadcast immediately to all connected sockets).*

### 8. Running the AI Simulator Tool
To run the automated end-to-end integration simulation against a running backend server:
```bash
# Ensure server is running: uvicorn app.main:app --port 8000
python tools/ai_simulator/simulate_intrusion.py
```
*(Executes step-by-step validation of authentication, camera/zone creation, real-time WebSocket delivery, evidence hashing, tamper detection, and audit logging).*

---

## 🔬 Evidence Integrity Demonstration Script
To verify the tamper-detection capabilities of the platform:
1. **Store Evidence**: Create an evidence metadata record via `POST /api/v1/events/{event_id}/evidence` with a `file_path` (e.g. `frame_001.jpg`).
2. **Place physical file**: Store a mock snapshot file (e.g. JPEG, text) inside the `data/evidence/` directory at the matching path.
3. **Generate Hash**: Run `POST /api/v1/evidence/{evidence_id}/hash` to compute the SHA-256 digest of the physical file and persist it.
4. **Verify Original**: Run `GET /api/v1/evidence/{evidence_id}/verify` and confirm the response status is `VERIFIED`.
5. **Simulate Tampering**: Edit the physical file manually inside `data/evidence/` to change its contents.
6. **Verify Tampered**: Run `GET /api/v1/evidence/{evidence_id}/verify` again and confirm it returns `MISMATCH`, indicating the evidence has been tampered with.
7. **Restore & Verify**: Revert the physical file contents back to the original content and verify again to see the status return to `VERIFIED`.

---

## 🚦 Implementation Status

- [x] **Backend Phase 1**: Backend Foundation (FastAPI engine, Pydantic settings, CORS, logging, `/health`).
- [x] **Backend Phase 2**: Database Models & Persistence Foundation (`Camera`, `Zone`, `Event`, `Alert`, `Evidence`, `User`, `AuditLog`, Alembic migration, model unit tests).
- [x] **Backend Phase 3**: Camera & Zone API Foundation (CRUD endpoints with Pydantic validation, SQLite-persistence test overrides, soft deactivation).
- [x] **Backend Phase 4**: Event & Alert API Foundation (Ingestion, transactional generation, camera-zone validation, pagination, mutable constraints).
- [x] **Backend Phase 5**: Evidence API & Lifecycle Foundation (Metadata association, Pydantic conflicts decoupled, immutable updates rejected).
- [x] **Backend Phase 6**: Evidence Integrity & SHA-256 Verification (Path resolution security, chunked file hashing, verify mismatch detection).
- [x] **Backend Phase 7**: Authentication, RBAC & Audit Integration (Argon2id password hashing, JWT access tokens, user management, RBAC matrices, audit logging).
- [x] **Backend Phase 8**: Real-Time WebSocket Event & Alert Delivery (`WebSocketManager`, query-token authentication, post-commit event broadcast).
- [x] **M1 Integration Checkpoint**: End-to-End Backend Integration Validation (AI Simulator tool, cross-component integration suite, 98/98 pytest tests passing).


