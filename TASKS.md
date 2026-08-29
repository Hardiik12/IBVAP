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

### Phase 1 — Camera Source Ingestion (`ai/camera`)
- **Owner**: M3 (Video/Edge Lead)
- [ ] Implement `CameraSource` abstract base class.
- [ ] Implement `WebcamSource` (USB / Laptop built-in webcam via OpenCV `cv2.VideoCapture`).
- [ ] Implement `VideoFileSource` (Recorded test video fallback).
- **Acceptance Criteria**: Script reads video stream smoothly and displays live RGB frames without memory leaks.

### Phase 2 — Object Detection (`ai/detection`)
- **Owner**: M2 (AI/ML Lead)
- [ ] Wrap Ultralytics YOLOv8 detector (`yolov8n.pt`).
- [ ] Implement detection filtering for target classes (`person`, `vehicle`).
- [ ] Normalize raw YOLO output to `NormalizedDetection` dict format.
- **Acceptance Criteria**: Detector processes frames and outputs normalized bounding boxes and confidence scores.

### Phase 3 — Multi-Object Tracking (`ai/tracking`)
- **Owner**: M2 (AI/ML Lead)
- [ ] Integrate ByteTrack algorithm.
- [ ] Bind normalized detections to persistent `track_id` assignments.
- **Acceptance Criteria**: Track ID remains continuous across successive frames for a subject moving in scene.

### Phase 4 — Virtual Polygon Zone Engine (`ai/zones`)
- **Owner**: M2 (AI/ML Lead)
- [ ] Implement spatial point math for bounding box (bottom-center coordinate).
- [ ] Implement Shapely point-in-polygon containment test against polygon coordinates.
- **Acceptance Criteria**: Engine correctly classifies point as `INSIDE` or `OUTSIDE` polygon zone.

### Phase 5 — Intrusion Event Engine (`ai/events`)
- **Owner**: M2 (AI/ML Lead)
- [ ] Implement track state transition machine (`OUTSIDE` → `INSIDE`).
- [ ] Emit `INTRUSION` event payload upon positive transition.
- [ ] Apply hysteresis/cooldown to suppress duplicate alert spam while subject stays `INSIDE`.
- **Acceptance Criteria**: Entering polygon generates exactly 1 intrusion event; remaining inside generates 0 extra events.

### Phase 6 — Alert System & Backend Service (`backend/app`)
- **Owner**: M1 (Backend Lead)
- [ ] Implement FastAPI REST route `POST /api/v1/events`.
- [ ] Implement WebSocket manager (`ws://localhost:8000/ws/alerts`).
- [ ] Setup PostgreSQL database models with SQLAlchemy and Alembic migrations.
- **Acceptance Criteria**: Ingested intrusion event stores record in DB and broadcasts WebSocket alert immediately.

### Phase 7 — Evidence Snapshot Capture (`backend/app/services` & `ai/pipeline`)
- **Owner**: M5 (Security/Evidence Lead)
- [ ] Implement frame snapshot capture on intrusion event.
- [ ] Store JPEG image file at `data/evidence/<evidence_id>.jpg`.
- **Acceptance Criteria**: Intrusion event saves a clear snapshot image associated with the event.

### Phase 8 — SHA-256 Integrity Engine (`backend/app/utils`)
- **Owner**: M5 (Security/Evidence Lead)
- [ ] Implement SHA-256 hash calculator over evidence image binary.
- [ ] Persist hash digest in `evidence` PostgreSQL table.
- [ ] Implement REST verification endpoint `POST /api/v1/evidence/{id}/verify`.
- **Acceptance Criteria**: Verification endpoint returns `VERIFIED` for untouched file, and `TAMPERED` for modified copy.

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
