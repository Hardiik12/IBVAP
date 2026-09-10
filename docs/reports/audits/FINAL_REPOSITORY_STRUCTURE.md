# IBVAP — Final Repository Architecture & Structure Specification

**Document Version:** 1.0.0 — Post-Refactor Final  
**Date:** 2026-09-10  
**Status:** 🟢 FROZEN & DEMO READY  
**Automated Test Baseline:** 187 / 187 Tests Passing (113 Backend + 74 AI)  
**Frontend Quality Baseline:** ESLint Clean | TypeScript Clean | 16/16 Next.js Pages Prerendered  

---

## 1. Final Directory Tree

```
IBVAP/
├── README.md                             # Master project documentation (23-point specification)
├── LICENSE                               # MIT open-source license
├── SECURITY.md                           # Cryptographic security & vulnerability disclosure policy
├── AGENTS.md                             # AI agent development directives & master rules
├── .env.example                          # Sanitized environment template (clean placeholders)
├── .gitignore                            # Comprehensive ignore rules (media, caches, locks, secrets)
├── docker-compose.yml                    # Multi-container orchestration (Postgres, Backend, AI, Frontend)
├── pytest.ini                            # Consolidated pytest runner configuration
│
├── backend/                              # Tier 2: FastAPI Operational & Security Backend
│   ├── alembic.ini                       # Database migration configuration
│   ├── Dockerfile                        # Backend container definition
│   ├── entrypoint.sh                     # Backend startup script (Alembic migration -> seed -> uvicorn)
│   ├── requirements.txt                  # Production dependencies (FastAPI, SQLAlchemy, psycopg, passlib, pyotp)
│   ├── requirements-dev.txt              # Development & testing dependencies
│   ├── migrations/                       # Alembic schema version migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 2026_08_29_1935-001_initial_schema.py
│   │       ├── 2026_08_30_0345-002_add_mfa_and_face_auth.py
│   │       └── 2026_08_30_0615-003_add_face_verification_fields.py
│   ├── app/                              # Core FastAPI application package
│   │   ├── main.py                       # FastAPI application factory & middleware
│   │   ├── api/                          # REST routing & dependency injection
│   │   │   ├── api.py                    # Aggregated v1 API router
│   │   │   ├── deps.py                   # DB session, JWT auth & RBAC permission dependencies
│   │   │   └── routes/                   # Domain route handlers (12 route modules)
│   │   ├── core/                         # Configuration, logging, cryptographic security
│   │   │   ├── config.py                 # Pydantic v2 BaseSettings
│   │   │   ├── logging.py                # Structured JSON logging
│   │   │   └── security.py               # Argon2id password hashing, JWT encoding/decoding
│   │   ├── db/                           # Relational persistence & seeding
│   │   │   ├── base.py                   # DeclarativeBase base model
│   │   │   ├── database.py               # SQLAlchemy async/sync engine & sessionmaker
│   │   │   └── seed.py                   # Canonical database seeder (4 roles, default cameras & zones)
│   │   ├── models/                       # SQLAlchemy 2.0 ORM domain entities (7 tables)
│   │   │   ├── alert.py, audit_log.py, camera.py, enums.py, event.py, evidence.py, user.py, zone.py
│   │   ├── schemas/                      # Pydantic request & response serialization schemas
│   │   │   ├── alert.py, audit_log.py, auth.py, camera.py, detection.py, event.py, evidence.py, user.py, websocket.py, zone.py
│   │   ├── services/                     # Core business logic services
│   │   │   ├── alert_service.py, audit_service.py, auth_service.py, camera_service.py, event_service.py, evidence_integrity_service.py, evidence_service.py, face_auth_service.py, mfa_service.py, notification_service.py, user_service.py, websocket_manager.py, zone_service.py
│   │   └── utils/                        # Backend utilities
│   └── tests/                            # Complete backend test suite (113 passing tests)
│       ├── conftest.py                   # Pytest fixtures & isolated SQLite test DB
│       ├── api/                          # REST & WebSocket endpoint integration tests (17 test modules)
│       ├── integration/                  # Live AI dispatch & end-to-end pipeline tests
│       └── unit/                         # Unit tests for models and configuration
│
├── ai/                                   # Tier 1: Computer Vision & Analytics Pipeline
│   ├── Dockerfile                        # AI container definition
│   ├── entrypoint.sh                     # AI container startup script
│   ├── requirements.txt                  # AI dependencies (ultralytics, opencv, supervision, httpx)
│   ├── requirements-dev.txt              # AI testing dependencies
│   ├── benchmarks/                       # Performance & latency benchmarking tools
│   │   ├── detection/
│   │   ├── performance/
│   │   └── tracking/
│   ├── camera/                           # Video acquisition & unified camera sources
│   │   ├── base.py                       # CameraSource abstract base class (read_frame and read alias)
│   │   ├── demo_camera_detection.py      # Camera ingestion to YOLO detection CLI demo
│   │   ├── file.py                       # VideoFileSource (recorded MP4/AVI looping ingestion)
│   │   ├── frame_processor.py            # FrameProcessor, FrameMetadata, FPSCounter
│   │   ├── source.py                     # BaseCameraSource abstraction & factory function
│   │   ├── synthetic.py                  # SyntheticSource (in-memory test frame generator)
│   │   └── webcam.py                     # WebcamSource (hardware USB / built-in camera ingestion)
│   ├── core/                             # AI configuration & structured logging
│   │   ├── config.py                     # AI Pydantic BaseSettings
│   │   └── logging.py                    # Formatted logging
│   ├── detection/                        # Object detection module
│   │   ├── camera_yolo.py                # Standalone demo YOLO preview script
│   │   ├── detector.py                   # YOLODetector wrapper around YOLOv8n
│   │   ├── schemas.py                    # NormalizedDetection data contract
│   │   └── test_detector.py              # Manual test script for YOLO detector
│   ├── events/                           # Intrusion state machine & HTTP dispatching
│   │   ├── dispatcher.py                 # Asynchronous EventDispatcher with retry/auth
│   │   ├── engine.py                     # IntrusionEventEngine (OUTSIDE -> INSIDE state)
│   │   └── schemas.py                    # IntrusionEvent and EventPayload schemas
│   ├── models/                           # Model weights storage (.gitkeep)
│   ├── pipeline/                         # Pipeline orchestration
│   │   └── runner.py                     # CameraPipelineRunner & AIPipeline
│   ├── tests/                            # AI automated test suite (74 passing tests)
│   │   ├── camera/                       # Camera unit tests
│   │   ├── detection/                    # Detector unit & model integrity tests
│   │   ├── events/                       # Dispatcher & state machine tests
│   │   ├── pipeline/                     # AIPipeline orchestrator tests
│   │   ├── tracking/                     # Tracker unit & schema tests
│   │   └── zones/                        # Ray-casting PIP geofence tests
│   ├── tracking/                         # Multi-object tracking module
│   │   ├── schemas.py                    # Track dataclass
│   │   ├── tracker.py                    # ByteTracker wrapper
│   │   └── validate_tracking.py          # Standalone tracking validation CLI
│   └── zones/                            # Geofencing module
│       ├── engine.py                     # PolygonZone & ZoneEngine (Ray-casting PIP)
│       └── schemas.py                    # ZoneConfig & ZoneStatus schemas
│
├── frontend/                             # Tier 3: Next.js 14 Tactical Command Center
│   ├── Dockerfile                        # Multi-stage production container definition
│   ├── package.json, package-lock.json   # Dependencies
│   ├── tsconfig.json, tailwind.config.ts # Configuration
│   ├── app/                              # Next.js 14 App Router routes (16 pages)
│   ├── components/                       # Tactical surveillance components
│   │   ├── alerts/, camera/, events/, evidence/, layout/, ui/
│   │   └── camera/PolygonZoneOverlay.tsx # Interactive polygon boundary renderer
│   ├── context/                          # React context providers (AuthContext, AlertContext, CameraContext)
│   ├── hooks/                            # Custom React hooks (useAlerts, useWebSocket, etc.)
│   ├── services/                         # Clean REST API client domain services (no mock data)
│   │   ├── apiClient.ts, authService.ts, cameraService.ts, eventService.ts, evidenceService.ts, healthService.ts, auditService.ts
│   ├── types/                            # Domain TypeScript contracts
│   ├── utils/                            # Canvas drawing & formatters
│   └── public/                           # Static assets
│
├── scripts/                              # Repository Automation & Helper Scripts
│   ├── development/                      # Development lifecycle scripts
│   │   ├── start-dev.sh                  # Start local database and seed
│   │   └── stop-dev.sh                   # Stop development containers
│   ├── database/                         # Database utility scripts
│   │   └── seed-demo-data.sh             # Seed initial demo accounts and cameras
│   └── presentation/                     # Presentation generation scripts
│       └── generate_pptx.py              # Automated PPTX slide generator
│
├── tools/                                # External simulation tools
│   └── ai_simulator/                     # Synthetic intrusion generator for frontend/backend stress test
│
├── data/                                 # Video assets & evidence snapshots
│   ├── evidence/                         # Runtime evidence storage (.gitkeep)
│   ├── test-cases/                       # Ground-truth test scenarios
│   └── videos/                           # Benchmark, test, and live-demo video clips
│
└── docs/                                 # Master Documentation Suite
    ├── api/                              # REST API specifications & WebSocket contracts
    ├── architecture/                     # Blueprints (System, Backend, Frontend, AI)
    ├── reports/                          # Audit & validation reports
    ├── research/                         # CV, tracking, edge computing research
    ├── sih/                              # SIH presentation decks, defense cards, demo scripts
    │   ├── defense/                      # Judge Q&A, code defense cards, rapid-fire sheets
    │   ├── demo/                         # Demo runbooks, startup guides, contingency playbooks
    │   └── presentation/                 # Slide decks & SIH_FINAL_PRESENTATION.pptx
    └── specs/                            # Master PRD, Architecture, ADR Decisions, Schema DDL
```

---

## 2. Directory Responsibilities

| Directory | Core Responsibility |
| :--- | :--- |
| `backend/` | Hosts the FastAPI REST API, WebSocket event gateway, SQLAlchemy models, Alembic migrations, security services (Argon2id, JWT, TOTP, SFace), and backend test suite. |
| `ai/` | Hosts the computer vision inference engine: YOLOv8n object detection, ByteTrack tracking, PolygonZone ray-casting geofencing, IntrusionEventEngine state machine, and asynchronous EventDispatcher. |
| `frontend/` | Hosts the Next.js 14 App Router tactical command center: real-time WebSocket alert feed, camera fleet viewer, interactive polygon canvas, evidence vault, and audit log viewer. |
| `scripts/` | Contains clean, organized operational shell scripts for development orchestration (`scripts/development/`), database seeding (`scripts/database/`), and presentation assets (`scripts/presentation/`). |
| `tools/` | Hosts external testing tools including the AI intrusion simulator for backend and frontend stress testing. |
| `data/` | Manages local media assets: test video sequences, benchmark clips, ground-truth scenarios, and runtime evidence snapshot storage. |
| `docs/` | Central repository documentation organized into architecture, API, research, reports, SIH presentation assets, and master specifications. |

---

## 3. Dependency Direction & System Flow

```
[ Camera / Video Ingestion ]
           │
           ▼
   [ YOLOv8n Detector ]
           │
           ▼
   [ ByteTrack Tracker ]
           │
           ▼
[ Polygon Geofence Engine ]
           │
           ▼
[ Intrusion State Machine ]
           │
           ▼ (EventPayload)
[ Async EventDispatcher ] ──── HTTP POST ────► [ FastAPI REST API (/api/v1/events) ]
                                                            │
                                        ┌───────────────────┴───────────────────┐
                                        ▼                                       ▼
                             [ PostgreSQL Database ]                 [ WebSocket Gateway ]
                             (Events, Evidence, Audit)                          │
                                                                                ▼
                                                                  [ Next.js Tactical UI ]
```

- **Dependency Rules:**
  1. `ai/` depends only on its self-contained CV libraries (`ultralytics`, `opencv`, `supervision`, `httpx`). It has **zero dependencies on FastAPI or PostgreSQL**.
  2. `backend/` serves as the authoritative persistence and security layer. It receives structured `EventPayload` contracts from `ai/` and broadcasts live alerts to `frontend/`.
  3. `frontend/` consumes backend REST and WebSocket APIs. It contains **zero mock data** and interacts exclusively with real server endpoints.

---

## 4. Entry Points

| Tier / Function | Entry Point Command | Description |
| :--- | :--- | :--- |
| **FastAPI Backend** | `cd backend && uvicorn app.main:app --port 8000` | REST API, OpenAPI docs (`/docs`), WebSocket hub |
| **Next.js Frontend** | `cd frontend && npm run dev` | Web Command Center UI (`http://localhost:3000`) |
| **AI Live Webcam** | `python -m ai.pipeline.runner --source webcam --index 0 --display` | Live camera ingestion + YOLO + ByteTrack + HUD |
| **AI Video File** | `python -m ai.pipeline.runner --source video_file --video-path <path>` | Recorded video sequence inference |
| **Docker Compose** | `docker compose up --build -d` | Complete 4-tier containerized stack |
| **Database Seeder** | `python -m backend.app.db.seed` | Seeds roles, demo accounts, cameras, and zones |
| **Intrusion Simulator**| `python tools/ai_simulator/simulate_intrusion.py` | Generates synthetic intrusion events for testing |

---

## 5. Test Suite Locations & Discovery

- **Test Framework:** Pytest 9.1+ with `asyncio` plugin and Next.js / TypeScript test tooling.
- **Pytest Configuration:** `pytest.ini` discovering `ai/tests/` and `backend/tests/`.
- **Total Passing Tests:** **187 / 187** (100% pass rate).
  - `backend/tests/`: 113 tests (API integration, RBAC, WebSocket, evidence integrity, auth, models).
  - `ai/tests/`: 74 tests (Camera sources, YOLO detector, model integrity, ByteTrack, polygon zones, dispatcher).
  - `frontend/`: ESLint clean, TypeScript compiler clean, 16/16 prerendered static routes.
