# IBVAP — Intelligent Border Video Analytics Platform
## Master Project Document — SIH Internal Round MVP

---

## 1. Project Overview & Context

**IBVAP** stands for **Intelligent Border Video Analytics Platform**. It is an AI-powered, real-time video analytics platform designed to assist security and border/perimeter monitoring personnel by transforming continuous video streams into structured, actionable security events.

Traditional video monitoring requires operators to observe multiple camera feeds continuously, causing visual fatigue and missed security events. IBVAP automates this workflow:

```
Camera Feed 
  → Frame Capture 
  → Object Detection (YOLO) 
  → Multi-Object Tracking (ByteTrack) 
  → Spatial Polygon Analysis (Restricted Zone) 
  → State Transition Evaluation (OUTSIDE → INSIDE) 
  → Security Event Generation (INTRUSION) 
  → Real-Time Alert Broadcast (WebSocket) 
  → Evidence Capture (Frame Snapshot) 
  → Evidence Integrity Verification (SHA-256 Hash) 
  → Operational Web Dashboard (Next.js)
```

### Context & Scope
The long-term vision encompasses cross-camera tracking, ANPR, face analytics, edge node clusters, and predictive surveillance. However, **the immediate target is the SIH Internal Round MVP**—a reliable, demonstrable prototype proving the core technical slice with empirical validation.

---

## 2. SIH Internal Round Objective

The objective of the SIH Internal Round is to prove technical depth, research rigor, clean architecture, and reliable execution through a complete working vertical slice.

### Core MVP Technical Slice
```
LIVE CAMERA (Webcam/USB)
  ↓
VIDEO PROCESSING (OpenCV)
  ↓
OBJECT DETECTION (Ultralytics YOLO)
  ↓
OBJECT TRACKING (ByteTrack)
  ↓
RESTRICTED-ZONE ANALYSIS (Point-in-Polygon)
  ↓
INTRUSION EVENT ENGINE (State Transition)
  ↓
REAL-TIME ALERT (WebSocket)
  ↓
EVIDENCE CAPTURE (Snapshot + Metadata)
  ↓
SHA-256 INTEGRITY VERIFICATION (Cryptographic Hash)
  ↓
OPERATIONAL DASHBOARD (Next.js / React)
```

The team prioritizes:
1. Working vertical slice over broad feature count.
2. Research-backed decisions over arbitrary library choices.
3. Empirical performance measurement over guessed claims.
4. Clean architectural boundaries separating AI, Backend, and Frontend.

---

## 3. Problem Statement & Research Question

### Problem Statement
Monitoring continuous perimeter surveillance footage in security environments requires significant human attention. Operators monitoring multiple video feeds experience rapid cognitive fatigue, leading to delayed response times or missed perimeter violations. 

### Key Research Question
> *Can a lightweight, edge-oriented computer-vision pipeline detect and track objects in a live camera feed, reliably identify when a tracked person enters an operator-defined restricted area, and generate cryptographically verifiable digital evidence with minimal end-to-end latency?*

---

## 4. Core MVP Use Case & Demo Walkthrough

The primary MVP scenario is a end-to-end, reproducible demonstration:

1. **System Initialization**: Start IBVAP backend, AI pipeline, and frontend dashboard.
2. **Camera Connection**: Connect laptop webcam or USB camera; live video feeds onto the dashboard.
3. **Zone Configuration**: Define a restricted polygon zone overlaid on the camera feed.
4. **Subject Entry**: A person enters the live camera field of view.
5. **Detection**: YOLO detects the subject (`class: person`, confidence score, bounding box).
6. **Tracking**: ByteTrack assigns a persistent identity (`track_id: 17`).
7. **Spatial Calculation**: Bottom-center coordinate `(x_center, y_bottom)` of the bounding box is computed.
8. **Zone Evaluation**: Point-in-polygon algorithm checks containment against the restricted zone.
9. **State Transition**: State transitions from `OUTSIDE` → `INSIDE`.
10. **Event Generation**: Event engine emits an `INTRUSION` event payload.
11. **Real-time Alert**: Dashboard receives an instant WebSocket alert with severity and track details.
12. **Evidence Capture**: High-resolution frame snapshot is saved alongside event metadata.
13. **Integrity Hashing**: System computes a SHA-256 hash of the evidence image and stores it in PostgreSQL.
14. **Dashboard Display**: The operator views the alert, event log, snapshot, and hash value.
15. **Integrity Verification**: Operator triggers hash verification; system recalculates hash and reports `VERIFIED`.
16. **Controlled Tamper Test**: Operator modifies a test copy of the evidence image; verification re-runs and correctly reports `TAMPERED / MISMATCH`.

---

## 5. Camera Strategy & Source Abstraction

The MVP prioritizes input reliability over complex network hardware:

### Priority Order
1. **USB Webcam** (Primary hardware target)
2. **Laptop Built-in Webcam** (Secondary hardware fallback)
3. **Recorded Test Video File** (Guaranteed fallback for reproducible testing)
4. **Phone Camera Stream** (IP Camera app stream)
5. **RTSP / IP Camera** (Future P1 capability)

### Camera Abstraction Interface
The AI pipeline consumes frames from an abstract `CameraSource` interface:
```python
class CameraSource(ABC):
    @abstractmethod
    def read_frame() -> Tuple[bool, np.ndarray]: pass
    @abstractmethod
    def release() -> None: pass
```
*Implementations*: `WebcamSource`, `VideoFileSource`, `RTSPSource`.

---

## 6. AI Pipeline & Model Architecture

```
Camera Source 
  ↓ Frame Capture
OpenCV Ingestion
  ↓ BGR Frame Array
Ultralytics YOLO Detector
  ↓ Normalized Detections List
ByteTrack Multi-Object Tracker
  ↓ Persistent Tracks List
Zone Engine (OpenCV PIP)
  ↓ Spatial Containment Status
Event Engine (State Machine)
  ↓ Intrusion Event Payload
Backend Dispatch
```

### Stack Components
- **Python 3.11**
- **OpenCV (`opencv-python`)**
- **Ultralytics YOLOv8** (YOLOv8n / YOLOv8s)
- **ByteTrack** (`lap` + `scipy` assignment)
- **NumPy** & **OpenCV pointPolygonTest**

---

## 7. Detection & Internal Normalization

Objects are detected and normalized into a frame-agnostic structure before being passed to downstream modules:

```json
{
  "class_id": 0,
  "class_name": "person",
  "confidence": 0.94,
  "bbox": [120, 240, 310, 580]
}
```
*Bounding Box Representation*: `[x1, y1, x2, y2]` in pixel coordinates.

---

## 8. Tracking & Identity Persistence

ByteTrack maintains persistent identities (`track_id`) across successive frames to eliminate duplicate alerts and handle transient occlusions.

```json
{
  "track_id": 17,
  "class_name": "person",
  "confidence": 0.94,
  "bbox": [124, 242, 312, 582],
  "reference_point": [218, 582],
  "timestamp": "2026-08-29T18:00:00.124Z"
}
```

---

## 9. Restricted Zone Engine & Spatial Logic

The spatial reference point for a detected person is the **bottom-center** of the bounding box:
$$\text{center}_x = \frac{x_1 + x_2}{2}, \quad \text{bottom}_y = y_2$$

### Point-in-Polygon (Ray-Casting Algorithm)
```
Point Outside Polygon  → State: OUTSIDE → No Event
Point Inside Polygon   → State: INSIDE
State Transition: OUTSIDE → INSIDE → Emits INTRUSION Event
State Continuation: INSIDE → INSIDE → Maintains State (No Duplicate Event)
State Transition: INSIDE → OUTSIDE → Resets State to OUTSIDE
```

Hysteresis buffer (cooldown timer / frame threshold) prevents event flickering near polygon edges.

---

## 10. Event Engine

Separates raw vision outputs from operational domain logic.

### Primary Event Payload Schema
```json
{
  "event_id": "evt-77291a",
  "event_type": "INTRUSION",
  "camera_id": "cam-webcam-01",
  "zone_id": "zone-alpha",
  "track_id": 17,
  "class_name": "person",
  "severity": "HIGH",
  "timestamp": "2026-08-29T18:00:00.150Z",
  "bounding_box": [124, 242, 312, 582],
  "reference_point": [218, 582]
}
```

---

## 11. Alert & Real-Time Communication

Events trigger alerts pushed to the dashboard over WebSockets (`ws://localhost:8000/ws/alerts`).

### Alert Schema
```json
{
  "alert_id": "alt-99120",
  "event_id": "evt-77291a",
  "event_type": "INTRUSION",
  "camera_id": "cam-webcam-01",
  "zone_name": "Perimeter Restricted Zone A",
  "track_id": 17,
  "severity": "HIGH",
  "timestamp": "2026-08-29T18:00:00.155Z",
  "status": "UNACKNOWLEDGED"
}
```

---

## 12. Evidence & SHA-256 Integrity Verification

### Evidence Pipeline
1. **Snapshot Capture**: AI pipeline saves the frame image at the moment of intrusion to `data/evidence/<evidence_id>.jpg`.
2. **Hash Generation**: Backend computes `SHA-256` hash of the binary file:
   $$\text{Hash} = \text{SHA256}(\text{ImageBytes})$$
3. **Database Record**: Metadata (event_id, file_path, hash, timestamp) saved in PostgreSQL.
4. **Integrity Verification API**:
   - Computes current hash of file at `file_path`.
   - Compares current hash with `stored_hash`.
   - Returns `VERIFIED` (Match) or `TAMPERED` (Mismatch).

*Clarification*: SHA-256 proves file integrity against tampering after recording; it does not validate real-world event authenticity.

---

## 13. System Architecture & Tech Stack

```
[ Camera Ingestion (OpenCV) ]
             ↓
[ AI Engine (YOLOv8 + ByteTrack + Zone/Event Engine) ]
             ↓ REST / HTTP
[ Backend API (FastAPI + SQLAlchemy + PostgreSQL) ]
       ↓                  ↓
[ WebSocket Alerts ]   [ Evidence Hashing (SHA-256) ]
       ↓                  ↓
[ Frontend Operational Dashboard (Next.js + React + Tailwind) ]
```

### Technology Stack
- **AI/CV**: Python 3.11, OpenCV, Ultralytics YOLOv8, ByteTrack, NumPy
- **Backend**: FastAPI, Uvicorn, PostgreSQL, SQLAlchemy ORM, Alembic, Pydantic, Python-jose (JWT), Passlib
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide React, HTML5 Canvas Overlay

---

## 14. Database Schema Overview

Primary Relational Entities:
- `users`: ID, username, email, password_hash, role (`OPERATOR`, `ANALYST`, `ADMIN`, `AUDITOR`)
- `cameras`: ID, name, source_type, source_uri, status
- `zones`: ID, camera_id, name, polygon_coordinates (JSONB)
- `events`: ID, camera_id, zone_id, track_id, event_type, severity, timestamp
- `alerts`: ID, event_id, status, created_at
- `evidence`: ID, event_id, file_path, sha256_hash, captured_at
- `audit_logs`: ID, user_id, action, details, timestamp

---

## 15. Research & Evaluation Plan

### Controlled Test Dataset (`data/test-cases/`)
- **TEST-001 (Normal Movement)**: Person moves outside restricted zone. *Expected*: 0 events.
- **TEST-002 (Single Intrusion)**: Person crosses polygon boundary. *Expected*: 1 Intrusion event + Alert + Snapshot + Hash.
- **TEST-003 (Zone Stay)**: Person remains inside polygon. *Expected*: 0 duplicate alerts.
- **TEST-004 (Zone Exit)**: Person leaves polygon. *Expected*: State reset to OUTSIDE.
- **TEST-005 (Re-entry)**: Person exits and re-enters. *Expected*: 2nd Intrusion event generated.
- **TEST-006 (Multiple Trackers)**: 3 people moving simultaneously. *Expected*: 3 distinct track IDs.
- **TEST-007 (Occlusion)**: Subject passes behind obstacle. *Expected*: ID continuity evaluated.
- **TEST-008 (Vehicle Detection)**: Vehicle enters scene. *Expected*: Vehicle class detection.

### Empirical Benchmarks (`docs/testing/benchmark-results.md`)
- Frame processing throughput (FPS)
- Detection & tracking latency (ms)
- Point-in-polygon evaluation latency (ms)
- End-to-end event-to-alert latency (ms)
- SHA-256 calculation & verification time (ms)

---

## 16. Scope Boundaries & Roadmap

### P0 — Mandatory MVP Scope (SIH Internal Round)
- Live webcam input (OpenCV)
- YOLO person detection
- ByteTrack tracking
- Virtual polygon zone containment
- Intrusion event generation (OUTSIDE → INSIDE)
- WebSocket alert push
- Evidence snapshot save
- SHA-256 hash generation & verification API
- Next.js Dashboard with live feed, alerts, event log, and evidence verification.

### P1 — Conditional Extensions (If P0 is stable)
- RTSP camera feed support
- Phone camera stream ingestion
- Interactive polygon drawing UI on dashboard
- Additional event types (EXIT, LOITERING)
- ANPR / Vehicle plate recognition module

### Future Vision (Out of MVP Scope)
- Multi-camera cross-tracking
- Blockchain-based immutable audit log
- Microservice architecture & Kubernetes deployment
- Predictive threat analytics
- Production government system integration

---

## 17. Team Roles & Development Responsibilities

- **M1 (Backend Lead)**: FastAPI REST endpoints, PostgreSQL DB, SQLAlchemy ORM, Alembic migrations.
- **M2 (AI/ML Lead)**: YOLO model, ByteTrack tracking, Polygon zone engine, Event state machine.
- **M3 (Video/Edge Lead)**: Camera abstraction, OpenCV frame pipeline, video stream optimization.
- **M4 (Frontend Lead)**: Next.js App Router, Dashboard views, Canvas bounding box overlay, WebSockets.
- **M5 (Security & Evidence Lead)**: JWT Auth, RBAC, Evidence file management, SHA-256 verification engine.
- **M6 (Integration, QA & Research Lead)**: E2E orchestration, test dataset validation, performance benchmarking, presentation stories.

---

## 18. Assumptions & Unresolved Questions

### Assumptions
1. Hardware used for internal round demo is a modern laptop capable of running YOLOv8n CPU/GPU inference at > 15 FPS.
2. Webcams (built-in or USB) provide standard 720p/1080p RGB streams.
3. Network connection between frontend and backend is localhost / low-latency LAN.

### Unresolved Questions
1. *Optimal Polygon Coordinate Normalization*: Should zone polygon coordinates be stored in raw pixel space `(x, y)` or normalized `(0.0-1.0)` space relative to camera resolution? (*Resolution: Use normalized 0.0-1.0 coordinates to handle variable stream resolutions.*)
2. *Frame Rate Throttling for AI Inference*: Should AI run on every frame or skip frames (e.g., process 1 out of 2 frames) to conserve CPU/GPU? (*Resolution: Benchmark local hardware in Phase 10; default to processing every frame for YOLOv8n.*)

---

## 19. Phased Development Workflow

- **Phase 0**: Repository & Documentation Setup (Complete)
- **Phase 1**: Camera Ingestion (`CameraSource` → OpenCV)
- **Phase 2**: Object Detection Integration (YOLOv8)
- **Phase 3**: Multi-Object Tracking Integration (ByteTrack)
- **Phase 4**: Virtual Polygon Zone Engine (OpenCV / PIP)
- **Phase 5**: Intrusion Event Engine (State Machine)
- **Phase 6**: Alert Engine & WebSocket Broadcast
- **Phase 7**: Evidence Snapshot Capture Engine
- **Phase 8**: SHA-256 Integrity Verification Engine
- **Phase 9**: Full Backend & Frontend Dashboard Integration
- **Phase 10**: Testing, Dataset Benchmarking & Tamper Demonstration
- **Phase 11**: SIH Presentation Readiness & Demo Practice

---

## 20. AI Coding Agent Rules

1. **Read `PROJECT.md` first** before making architectural proposals or changes.
2. **Strict Phase Adherence**: Implement only the requested phase. Do not jump ahead.
3. **No Unapproved Feature Creep**: Do not implement blockchain, microservices, or RTSP unless explicitly commanded.
4. **Preserve Interfaces**: Keep internal data contracts (`Detection`, `Track`, `EventPayload`) normalized.
5. **No Fabricated Benchmarks**: Only record empirical benchmark numbers from test execution.
