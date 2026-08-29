# IBVAP — Product Requirements Document (PRD)
## SIH Internal Round MVP

---

## 1. Product Vision & Goals

### 1.1 Vision
IBVAP (Intelligent Border Video Analytics Platform) transforms continuous surveillance video into actionable security events, eliminating operator visual fatigue and enhancing situational awareness in critical border and perimeter security operations.

### 1.2 Internal Round Goal
Build a demonstrable, research-backed vertical slice prototype for the SIH Internal Round that proves end-to-end real-time intrusion detection, alerting, evidence snapshot generation, and cryptographic SHA-256 evidence integrity verification on a live webcam feed.

---

## 2. Stakeholders & User Personas

### 2.1 Stakeholders
- **SIH Evaluators / Judges**: Assessing technical depth, research validity, architecture quality, and demonstration clarity.
- **Security Operators**: End users relying on automated alerts and evidence logs to monitor restricted zones.
- **Auditors & Investigators**: Verifying evidence file integrity using cryptographic hashes.

### 2.2 User Personas
1. **Operator (Security Personnel)**:
   - *Goal*: Monitor active camera feeds, view real-time intrusion alerts, inspect incident snapshots.
   - *Need*: Clear visual overlays (bounding boxes, zone polygons), immediate pop-up alerts.
2. **Analyst / Auditor**:
   - *Goal*: Review historical intrusion events, export evidence packages, verify evidence against tampering.
   - *Need*: Searchable event logs, one-click SHA-256 verification, tamper detection test tool.
3. **Administrator**:
   - *Goal*: Configure camera sources, define restricted zone polygons, manage user accounts and system settings.

---

## 3. Functional Requirements

| Requirement ID | Module | Description | Priority |
| :--- | :--- | :--- | :--- |
| **FR-CAM-01** | Camera | Ingest live frames from USB webcam or laptop built-in webcam via OpenCV | **P0** |
| **FR-CAM-02** | Camera | Support fallback frame ingestion from pre-recorded video files | **P0** |
| **FR-DET-01** | AI Detection | Detect objects (`person`, `vehicle`) in live video frames using Ultralytics YOLOv8 | **P0** |
| **FR-DET-02** | AI Detection | Normalize detection outputs into standard internal representations | **P0** |
| **FR-TRK-01** | AI Tracking | Assign and maintain persistent `track_id` across frames using ByteTrack | **P0** |
| **FR-ZONE-01** | Zone Engine | Support definition of restricted virtual polygon zones on camera coordinates | **P0** |
| **FR-ZONE-02** | Zone Engine | Calculate spatial reference point (bottom-center of bounding box for persons) | **P0** |
| **FR-ZONE-03** | Zone Engine | Evaluate spatial containment (Point-in-Polygon) against active restricted zones | **P0** |
| **FR-EVT-01** | Event Engine | Identify state transition (`OUTSIDE` → `INSIDE`) and emit `INTRUSION` event | **P0** |
| **FR-EVT-02** | Event Engine | Prevent duplicate alert spam while an object remains `INSIDE` the zone | **P0** |
| **FR-ALT-01** | Alert System | Broadcast real-time intrusion alerts to frontend via WebSockets | **P0** |
| **FR-EVI-01** | Evidence | Capture and save a full-resolution image snapshot at the moment of intrusion | **P0** |
| **FR-EVI-02** | Evidence | Compute SHA-256 hash of the saved evidence snapshot image | **P0** |
| **FR-EVI-03** | Evidence | Provide verification endpoint/UI to recalculate hash and detect file tampering | **P0** |
| **FR-UI-01** | Dashboard | Display live camera feed with real-time bounding box and polygon zone overlays | **P0** |
| **FR-UI-02** | Dashboard | Provide real-time alert notification panel and historical event log table | **P0** |
| **FR-UI-03** | Dashboard | Provide evidence inspection modal with one-click SHA-256 hash verification | **P0** |

---

## 4. Non-Functional Requirements

### 4.1 Performance & Latency
- **Processing FPS**: $\ge 15$ FPS local execution on standard modern development hardware (CPU/GPU).
- **End-to-End Latency**: Frame capture to dashboard alert push $\le 250$ ms.
- **Hash Computation**: SHA-256 generation time $\le 15$ ms per evidence image.

### 4.2 Security & Integrity
- **Password Security**: Passwords hashed using bcrypt/argon2.
- **Authentication**: JWT-based authentication for backend API routes.
- **Cryptographic Verification**: Deterministic SHA-256 hash calculation over raw evidence image bytes.

### 4.3 Reliability & Modularity
- **Modular Decoupling**: AI processing pipeline, backend storage, and frontend UI must be strictly separated.
- **Camera Fallback**: If physical webcam fails, system must seamlessly fall back to recorded test video.

---

## 5. Scope Boundaries

### 5.1 In Scope (P0 - Mandatory MVP)
- Single live camera feed (Webcam/File fallback)
- YOLOv8 Person & Vehicle detection
- ByteTrack persistent multi-object tracking
- Virtual polygon zone & point-in-polygon intrusion logic
- Real-time WebSocket alert delivery
- Snapshot evidence capture & SHA-256 verification engine
- Operational Next.js dashboard

### 5.2 Conditional Extensions (P1)
- RTSP / IP camera support
- Interactive polygon drawing UI
- Additional event types (EXIT, LOITERING)

### 5.3 Out of Scope (Future Roadmap)
- Blockchain integration
- Kubernetes / Cloud microservice deployment
- Multi-camera cross-tracking & identity correlation
- Face recognition or ANPR modules

---

## 6. Success Metrics & Key Performance Indicators (KPIs)

1. **Vertical Slice Execution**: 100% successful execution of the 16-step demonstration workflow.
2. **Detection & Tracking Latency**: AI inference + tracking + zone evaluation under 100ms per frame.
3. **Tamper Detection Accuracy**: 100% detection rate for modified evidence copies in tamper verification testing.
4. **False Alert Rate**: 0 duplicate intrusion alerts emitted while subject stays inside the zone.
