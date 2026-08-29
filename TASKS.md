# IBVAP — Implementation Roadmap & Task Matrix
## SIH Internal Round MVP

---

## 1. Phased Implementation Roadmap

```
Phase 0: Architecture & Documentation (DONE)
   ↓
Phase 1: Camera Ingestion Abstraction (OpenCV) ──► Target: M3
   ↓
Phase 2: Object Detection (YOLOv8) ──────────────► Target: M2
   ↓
Phase 3: Multi-Object Tracking (ByteTrack) ──────► Target: M2
   ↓
Phase 4: Restricted Zone Polygon Engine ─────────► Target: M2
   ↓
Phase 5: Intrusion Event Engine ─────────────────► Target: M2
   ↓
Phase 6: Alert Engine & WebSocket Server ────────► Target: M1
   ↓
Phase 7: Evidence Snapshot Capture ──────────────► Target: M5
   ↓
Phase 8: SHA-256 Hash Integrity Engine ─────────► Target: M5
   ↓
Phase 9: Full Frontend & Backend Integration ───► Target: M4 / M1 / M6
   ↓
Phase 10: Testing, Dataset & Benchmarking ───────► Target: M6
   ↓
Phase 11: Presentation & Demo Polish ────────────► Target: All Team
```

---

## 2. Detailed Task Matrix & Acceptance Criteria

### Phase 0 — Documentation & Foundation Setup (COMPLETE)
- [x] Create project monorepo structure.
- [x] Author core documentation (`PROJECT.md`, `PRD.md`, `REQUIREMENTS.md`, `TECH_STACK.md`, `ARCHITECTURE.md`, `API.md`, `DATABASE.md`, `AGENTS.md`, `TASKS.md`, `DECISIONS.md`).

### Phase 1 / M2.1 — Camera Source Ingestion & Computer Vision Foundation (`ai/camera`) (COMPLETE)
- **Owner**: M3 (Video/Edge Lead) / M2 (AI/ML Lead)
- [x] Implement `BaseCameraSource` abstract base class in `ai/camera/source.py`.
- [x] Implement `WebcamSource` for USB / built-in webcams (`cv2.VideoCapture`).
- [x] Implement `VideoFileSource` for recorded test videos (clean EOF detection).
- [x] Implement `create_camera_source` factory pattern.
- [x] Implement `FrameProcessor` in `ai/camera/frame_processor.py` for frame validation, resizing, `FrameMetadata` extraction, and moving-average FPS calculation.
- [x] Implement `CameraPipelineRunner` in `ai/pipeline/runner.py` with diagnostic overlay (`FPS`, `Resolution`, `Source`, `Frame ID`), keyboard quit (`q`/`ESC`), and headless mode (`DISPLAY_PREVIEW=false`).
- [x] Add automated unit & pipeline test suite (`ai/tests/`) passing 25/25 tests.
- [x] Verify full regression suite (`pytest backend/tests/ ai/tests/`) passing cleanly.
- **Acceptance Criteria**: Script reads stream smoothly, displays live telemetry overlays, supports headless server mode, releases camera resources safely, and all pytest tests pass.

### Phase 2 — Object Detection (`ai/detection`)
- **Owner**: M2 (AI/ML Lead)
- [x] Wrap Ultralytics YOLOv8 detector (`yolov8n.pt`).
- [x] Implement detection filtering for target classes (`person`, `vehicle`).
- [x] Normalize raw YOLO output to `NormalizedDetection` dict format.
- **Acceptance Criteria**: Detector processes frames and outputs normalized bounding boxes and confidence scores.

### Phase 3 — Multi-Object Tracking (`ai/tracking`)
- **Owner**: M2 (AI/ML Lead)
- [x] Integrate ByteTrack algorithm.
- [x] Bind normalized detections to persistent `track_id` assignments.
- **Acceptance Criteria**: Track ID remains continuous across successive frames for a subject moving in scene.

### Phase 4 — Virtual Polygon Zone Engine (`ai/zones`)
- **Owner**: M2 (AI/ML Lead)
- [x] Implement spatial point math for bounding box (bottom-center coordinate).
- [x] Implement OpenCV point-in-polygon (cv2.pointPolygonTest) containment test against polygon coordinates.
- **Acceptance Criteria**: Engine correctly classifies point as `INSIDE` or `OUTSIDE` polygon zone.

### Phase 5 — Intrusion Event Engine (`ai/events`)
- **Owner**: M2 (AI/ML Lead)
- [x] Implement track state transition machine (`OUTSIDE` → `INSIDE`).
- [x] Emit `INTRUSION` event payload upon positive transition.
- [x] Apply hysteresis/cooldown to suppress duplicate alert spam while subject stays `INSIDE`.
- **Acceptance Criteria**: Entering polygon generates exactly 1 intrusion event; remaining inside generates 0 extra events.

### Backend Phase 1 — Backend Foundation (`backend/app`) (COMPLETE)
- **Owner**: M1 (Backend Lead)
- [x] FastAPI application engine initialized with metadata, root `/`, `/health`, and error handling.
- [x] Environment configuration (`app/core/config.py`) using `pydantic-settings`.
- [x] SQLAlchemy 2.0 engine, `SessionLocal`, and `get_db` dependency in `app/db/database.py`.
- [x] Alembic migration setup (`alembic.ini`, `migrations/env.py`).
- [x] Pytest suite in `tests/api/test_health.py` and `tests/unit/test_config.py`.
- **Acceptance Criteria**: Application initializes cleanly, `/health` returns `status = ok`, tests pass without live DB dependency.

### Backend Phase 2 — Database Models & Persistence Foundation (`backend/app/models`) (COMPLETE)
- **Owner**: M1 (Backend Lead)
- [x] Reusable domain enums (`CameraSourceType`, `ZoneType`, `EventType`, `EventSeverity`, `AlertStatus`, `UserRole`).
- [x] SQLAlchemy 2.0 ORM models for `Camera`, `Zone`, `Event`, `Alert`, `Evidence`, `User`, `AuditLog`.
- [x] Evidence deletion restriction policy (`ondelete="RESTRICT"`).
- [x] Model registration with `Base.metadata` for Alembic autogeneration.
- [x] Alembic migration `phase2_database_models` created and validated.
- [x] Demo data seed script (`app/db/seed.py`).
- [x] Pytest suite `tests/unit/test_models.py` with 7 model tests passing.
- **Acceptance Criteria**: All 7 models defined with relationships, indexes, unique constraints, migration generated, unit tests passing.

### Backend Phase 3 — Camera & Zone APIs (`backend/app/api`) (COMPLETE)
- **Owner**: M1 (Backend Lead)
- [x] Centralized API router with prefix `/api/v1` (`app/api/api.py`).
- [x] Pydantic schemas for Camera and Zone (`CameraCreate`, `CameraUpdate`, `CameraResponse`, `ZoneCreate`, `ZoneUpdate`, `ZoneResponse`).
- [x] Strict polygon validation checking (coordinates between 0.0 and 1.0, minimum 3 points).
- [x] Service layer logic handling duplicate constraints, existence checks, and soft deactivations (`is_active = False`).
- [x] Camera API endpoints: GET/POST/PATCH/DELETE.
- [x] Zone API endpoints: GET/POST/PATCH/DELETE.
- [x] Full automated API test suite (`tests/api/test_cameras.py` and `tests/api/test_zones.py`) passing cleanly.
- **Acceptance Criteria**: Centralized route registry integrated in main.py, input schemas strictly validated, soft deletion implemented for cameras/zones, 29 pytest tests passing.

### Backend Phase 4 — Event & Alert APIs (`backend/app/api`) (COMPLETE)
- **Owner**: M1 (Backend Lead)
- [x] Pydantic schemas for Event and Alert (`EventCreate`, `EventUpdate`, `EventResponse`, `AlertUpdate`, `AlertResponse`).
- [x] Extraneous parameter check (`extra="forbid"`) to enforce event and alert field immutability.
- [x] Schema-level bounding box and position coordinate object validation.
- [x] Camera-zone alignment mapping checks (raises 409 Conflict if mismatched).
- [x] Service layers (`event_service.py` and `alert_service.py`) handling transactional event and alert insertions.
- [x] Automated Alert generation on `INTRUSION` event types (status initialized to `ACTIVE`).
- [x] Acknowledgment handling (status update to `ACKNOWLEDGED` populates `acknowledged_at` timestamp).
- [x] Pagination limits and range-based timestamp filters (`limit` default 20, max 100).
- [x] Event API endpoints: GET/POST/PATCH (DELETE returns 405 Method Not Allowed).
- [x] Alert API endpoints: GET/PATCH.
- [x] Full automated API test suite (`tests/api/test_events.py` and `tests/api/test_alerts.py`) passing cleanly.
- **Acceptance Criteria**: Events and alerts registered under central route controller, transactional event-alert creation verified, field updates strictly restricted, range/pagination query filters active, 45 pytest tests passing.

### Backend Phase 5 — Evidence API & Evidence Lifecycle (`backend/app/api`) (COMPLETE)
- **Owner**: M1 (Backend Lead)
- [x] Decouple Pydantic alias conflict with SQLAlchemy metadata.
- [x] Pydantic schemas for Evidence (`EvidenceCreate`, `EvidenceUpdate`, `EvidenceResponse`).
- [x] Unhashed database persistence strategy using empty string defaults (`sha256_hash = ""`) to resolve database not null constraints without migration.
- [x] Extraneous parameters update check (`extra="forbid"`) to enforce evidence metadata immutability.
- [x] Service layer (`evidence_service.py`) handling evidence creation, listing, retrieval, and updates.
- [x] Event existence validation on evidence creation (raises 404 if missing).
- [x] Evidence ID uniqueness enforcement (raises 409 Conflict if duplicate).
- [x] Evidence API endpoints: POST / GET (event specific) and GET / PATCH (individual). DELETE returns 405 Method Not Allowed.
- [x] Full automated API test suite (`tests/api/test_evidence.py`) passing cleanly.
- **Acceptance Criteria**: Evidence registry integrated, Pydantic metadata alias resolved, immutable updates rejected, range/relationships consistent, 55 pytest tests passing.

### Backend Phase 6 — Evidence Integrity & SHA-256 Verification (`backend/app/api`) (COMPLETE)
- **Owner**: M1 (Backend Lead)
- [x] Nullable `sha256_hash` database schema change in SQLAlchemy model.
- [x] Alembic migration (`make_evidence_hash_nullable`) generated, populated, and executed.
- [x] Add `EVIDENCE_ROOT` parameter to application core settings.
- [x] Remove `sha256_hash` from client-controlled schemas (`EvidenceCreate`/`EvidenceUpdate`) to prevent external client overwrite.
- [x] Safe path resolution engine (`Path.is_relative_to`) preventing directory traversal outside the evidence root.
- [x] Incremental chunked hashing function (`calculate_sha256`) processing large files without high memory utilization.
- [x] Idempotency check in hash generation (retaining existing hashes without overwrite).
- [x] POST `/api/v1/evidence/{evidence_id}/hash` endpoint persisting digests.
- [x] GET `/api/v1/evidence/{evidence_id}/verify` endpoint comparing current and stored digests.
- [x] Handled `NOT_HASHED`, `VERIFIED`, and `MISMATCH` statuses with clear verification response models.
- [x] Full automated API test suite (`tests/api/test_evidence_integrity.py`) passing cleanly.
- **Acceptance Criteria**: Hashing generated on-demand server-side, client-controlled overrides blocked, path traversal attempts rejected, file modification detected via `MISMATCH`, and 62 pytest tests passing.

### Phase 7 — Evidence Snapshot Capture (`backend/app/services` & `ai/pipeline`)
- **Owner**: M5 (Security/Evidence Lead)
- [ ] Implement frame snapshot capture on intrusion event.
- [ ] Store JPEG image file at `data/evidence/<evidence_id>.jpg`.
- **Acceptance Criteria**: Intrusion event saves a clear snapshot image associated with the event.

### Backend Phase 7 — Authentication, RBAC & Audit Integration (`backend/app`) (COMPLETE)
- **Owner**: M1 (Backend Lead)
- [x] Argon2id password hashing using `pwdlib`.
- [x] JWT access token creation & verification (`PyJWT`) with configurable `JWT_SECRET_KEY` and expiration.
- [x] Login endpoint `POST /api/v1/auth/login` returning Bearer tokens and generic 401 error handling.
- [x] Current user profile endpoint `GET /api/v1/auth/me`.
- [x] User management endpoints (`GET/POST/PATCH /api/v1/users`) reserved for `ADMINISTRATOR`.
- [x] Admin self-deactivation protection (preventing deactivating or demoting the final active administrator).
- [x] Audit logging engine (`AuditService.log_action`) tracking `LOGIN_SUCCESS`, `LOGIN_FAILURE`, `CAMERA_*`, `ZONE_*`, `ALERT_ACKNOWLEDGED`, `EVIDENCE_VERIFIED`, `USER_*`.
- [x] Audit log endpoint `GET /api/v1/audit-logs` restricted to `ADMINISTRATOR` and `AUDITOR` roles (DELETE returns 405).
- [x] Protected all API endpoints (`/cameras`, `/zones`, `/events`, `/alerts`, `/evidence`) with Bearer token authentication and role checking dependencies.
- [x] Full automated API test suite (`test_auth.py`, `test_users.py`, `test_rbac.py`, `test_audit.py`) passing cleanly.
- **Acceptance Criteria**: OWASP password security active, RBAC matrix enforced across routes, audit trail generated transactionally, and 83 pytest tests passing.

### Backend Phase 8 — Real-Time WebSocket Event & Alert Delivery (`backend/app/api/ws`) (COMPLETE)
- **Owner**: M1 (Backend Lead)
- [x] In-process WebSocket connection manager (`WebSocketManager` in `app/services/websocket_manager.py`).
- [x] JWT query parameter authentication (`ws://localhost:8000/api/v1/ws/events?token=<access_token>`).
- [x] Role-based access control allowing `OPERATOR`, `ANALYST`, `ADMINISTRATOR`, `AUDITOR`.
- [x] Immediate close (code `1008`) for missing, invalid, or expired tokens, or inactive users.
- [x] Pydantic WebSocket notification schema (`WebSocketEventMessage` in `app/schemas/websocket.py`).
- [x] Post-commit broadcast event trigger (`NotificationService.notify_event_created` in `app/services/notification_service.py`).
- [x] Single coherent payload containing event and alert fields broadcast on `INTRUSION` events.
- [x] Dead connection cleanup without interrupting active clients or crashing backend server.
- [x] Full automated test suite (`tests/api/test_websocket.py`) passing cleanly.
### M1 Integration Checkpoint — End-to-End Validation (COMPLETE)
- **Owner**: M1 (Backend Lead)
- [x] AI Simulator Tool (`tools/ai_simulator/simulate_intrusion.py`) simulating normalized AI event contracts.
- [x] Dedicated cross-component E2E integration test suite (`tests/integration/test_e2e_pipeline.py`).
- [x] Verified complete flow: Login -> JWT -> Camera Setup -> Zone Setup -> WS Connect -> Event Ingestion -> Alert Generation -> Real-Time WS Broadcast -> Evidence Snapshot -> SHA-256 Hash -> Verification (VERIFIED) -> Physical File Modification -> Tamper Detection (MISMATCH) -> File Restoration -> Re-Verification (VERIFIED) -> Audit Log Verification.
- [x] Executed 7 failure & edge case tests (404 invalid camera, 404 invalid zone, 409 camera/zone mismatch, 409 duplicate event_identifier, 401 unauthorized REST API, 401 expired JWT, 1008 unauthorized WS).
- [x] Verified REST and WebSocket consistency.
- [x] Verified 98/98 pytest tests passing cleanly across unit, api, and integration test suites.
- **Acceptance Criteria**: Complete end-to-end integration flow verified empirically, zero real AI code introduced into backend, and 98 pytest tests passing.

### Phase 9 — Frontend Operational Dashboard (`frontend/`)
- **Owner**: M4 (Frontend Lead)
- [ ] Build Next.js Dashboard layout with live video monitor & Canvas overlay.
- [ ] Implement real-time WebSocket alert notification feed.
- [ ] Build Evidence Inspection modal with one-click SHA-256 verification button.
- **Acceptance Criteria**: Dashboard displays live overlays, alerts on intrusion, and verifies evidence hashes interactively.

### Phase 10 — Testing & Benchmarking (`integration/tests` & `docs/testing`)
- **Owner**: M6 (Integration / QA Lead)
- [ ] Execute test dataset (TEST-001 through TEST-008).
- [ ] Record empirical FPS, inference latency, tracking stability, and hash verification speed in `docs/testing/benchmark-results.md`.
- **Acceptance Criteria**: All 8 test scenarios verified; benchmark document populated with real metrics.

### Phase 11 — SIH Presentation & Demo Practice (All Team)
- **Owner**: All Team Members / M6 Lead
- [ ] Rehearse 16-step live demonstration narrative.
- [ ] Validate camera failovers and controlled tamper test script.
- **Acceptance Criteria**: 100% reproducible live demo execution under 5 minutes.
