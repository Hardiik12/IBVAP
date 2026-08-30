# IBVAP — SIH Judge Attack Simulation & Defense Matrix

This document simulates a skeptical judging panel probing edge cases, failure modes, real-time performance claims, and architectural limitations.

---

### 1. Why is this better than conventional CCTV?
- **Answer (30s):** "Conventional CCTV is passive recording that requires fatigued human observers and produces unverified video files. IBVAP provides active AI detection, filters alert spam through state-machine geofencing, pushes live alerts in under 10ms over WebSockets, and mathematically guarantees evidence integrity with server-side SHA-256 validation."
- **Technical Evidence:** [`ai/events/intrusion_engine.py`](file:///Users/hardik/Downloads/IBVAP/ai/events/intrusion_engine.py) & [`backend/app/services/evidence_integrity_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/evidence_integrity_service.py).
- **Honest MVP Limitation:** Requires an edge compute node (GPU or modern CPU) to run YOLOv8 rather than a basic analog DVR.

---

### 2. What exactly is your AI doing frame-by-frame?
- **Answer (35s):** "Each frame undergoes YOLOv8 inference yielding class bounding boxes. ByteTrack applies Kalman filtering to assign persistent Track IDs. We extract the bottom-center foot-point $[x_{center}, y_{bottom}]$ and execute a Shapely ray-casting Point-in-Polygon check against normalized polygon coordinates."
- **Technical Evidence:** [`ai/detection/detector.py`](file:///Users/hardik/Downloads/IBVAP/ai/detection/detector.py), [`ai/tracking/tracker.py`](file:///Users/hardik/Downloads/IBVAP/ai/tracking/tracker.py), [`ai/zones/polygon_zone.py`](file:///Users/hardik/Downloads/IBVAP/ai/zones/polygon_zone.py).
- **Honest MVP Limitation:** Single-worker video ingestion pipeline per camera stream.

---

### 3. How do you handle false positives from shadows or vegetation?
- **Answer (30s):** "We ground detections by extracting the foot-point contact coordinate rather than the bounding box centroid. Shadows, waving tree branches, or birds in the upper frame do not trigger an intrusion unless the ground-level contact point breaches the polygon boundary."
- **Technical Evidence:** `PolygonZone.contains_point(point)` in [`ai/zones/polygon_zone.py`](file:///Users/hardik/Downloads/IBVAP/ai/zones/polygon_zone.py).
- **Honest MVP Limitation:** Low-flying drones or aerial objects require separate elevation geofencing.

---

### 4. How is an intrusion mathematically determined?
- **Answer (30s):** "Through the Jordan Curve Theorem implemented via Shapely ray-casting: a ray is cast from the query point to infinity; an odd number of boundary edge intersections proves the point is inside the polygon. An intrusion event is emitted only upon a state transition from `OUTSIDE` to `INSIDE`."
- **Technical Evidence:** [`ai/events/intrusion_engine.py`](file:///Users/hardik/Downloads/IBVAP/ai/events/intrusion_engine.py).
- **Honest MVP Limitation:** Polygon coordinates must be mapped to the camera perspective during initial zone calibration.

---

### 5. Why ByteTrack instead of DeepSORT?
- **Answer (30s):** "DeepSORT relies on a heavy ReID deep neural network for appearance embeddings, dropping throughput below 30 FPS. ByteTrack matches both high-confidence and low-confidence detection boxes using Kalman filtering, preserving identities during occlusion while achieving 198+ FPS."
- **Technical Evidence:** [`ai/tracking/tracker.py`](file:///Users/hardik/Downloads/IBVAP/ai/tracking/tracker.py) & `PERFORMANCE_RESULTS.md`.
- **Honest MVP Limitation:** If a target is fully occluded for more than 30 consecutive frames, a new Track ID is assigned upon reappearance.

---

### 6. What happens when the camera feed goes offline?
- **Answer (25s):** "The AI video reader detects zero frames from the capture source, logs a clean disconnect warning without crashing, and closes the stream. The backend maintains existing historical events and alerts in PostgreSQL."
- **Technical Evidence:** [`ai/pipeline/runner.py`](file:///Users/hardik/Downloads/IBVAP/ai/pipeline/runner.py).
- **Honest MVP Limitation:** Current MVP runner does not currently have automated RTSP stream reconnect retries.

---

### 7. What happens when the FastAPI backend goes offline?
- **Answer (30s):** "The Next.js frontend catches the loss of heartbeat, instantly displaying `BACKEND ● OFFLINE | DB: DISCONNECTED`. The UI gracefully shows offline notices without crashing or displaying synthetic mock data, automatically re-hydrating when the backend recovers."
- **Technical Evidence:** [`frontend/hooks/useHealthCheck.ts`](file:///Users/hardik/Downloads/IBVAP/frontend/hooks/useHealthCheck.ts) & [`frontend/components/layout/SystemStatusBadge.tsx`](file:///Users/hardik/Downloads/IBVAP/frontend/components/layout/SystemStatusBadge.tsx).
- **Honest MVP Limitation:** Local single-node deployment rather than a multi-AZ load-balanced gateway.

---

### 8. Can an attacker inject fake AI intrusion events?
- **Answer (30s):** "No. The `/api/v1/events` endpoint is protected by JWT authentication and requires a valid bearer token signed with the server secret. Unauthenticated or invalid token requests are rejected immediately with HTTP 401 Unauthorized."
- **Technical Evidence:** [`backend/app/api/deps.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/api/deps.py) & [`backend/tests/api/test_security_audit.py`](file:///Users/hardik/Downloads/IBVAP/backend/tests/api/test_security_audit.py).
- **Honest MVP Limitation:** The AI worker and backend must share pre-configured service credentials.

---

### 9. Can evidence be modified on disk without detection?
- **Answer (30s):** "No. At the exact millisecond of intrusion, the backend writes the JPEG frame to disk and calculates its binary SHA-256 hash, storing the digest in PostgreSQL. Any modification of even a single byte on disk results in an immediate 🔴 `TAMPER DETECTED` mismatch during verification."
- **Technical Evidence:** [`backend/app/services/evidence_integrity_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/evidence_integrity_service.py).
- **Honest MVP Limitation:** Does not prevent file deletion by root OS users, though missing files return clean `FILE_NOT_FOUND` errors.

---

### 10. Does SHA-256 prove legal chain of custody?
- **Answer (30s):** "Yes. SHA-256 is an NIST-approved cryptographic standard with $2^{128}$ collision resistance. Pairing the hash digest with immutable PostgreSQL `audit_logs` recording the capture timestamp, verifying actor ID, and IP address provides non-repudiation in legal forensics."
- **Technical Evidence:** [`backend/app/services/audit_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/audit_service.py).
- **Honest MVP Limitation:** Stored in PostgreSQL rather than a hardware security module (HSM) or public blockchain ledger.

---

### 11. Why use JWT for API authentication?
- **Answer (25s):** "JWTs provide stateless, cryptographically signed bearer tokens containing user identity and role claims, enabling sub-millisecond API authorization with strict 15-minute expiration windows without requiring database session lookups on every request."
- **Technical Evidence:** [`backend/app/services/auth_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/auth_service.py).
- **Honest MVP Limitation:** Token revocation before the 15-minute expiration relies on token expiry rather than a distributed blacklist.

---

### 12. How does your RBAC model prevent privilege escalation?
- **Answer (30s):** "FastAPI dependencies (`require_role`) enforce strict role boundaries on every endpoint: `ADMINISTRATOR` (full CRUD), `OPERATOR` (alert ACK), `ANALYST` (read-only telemetry), and `AUDITOR` (immutable audit review). Unauthorized role calls return HTTP 403 Forbidden."
- **Technical Evidence:** [`backend/app/api/deps.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/api/deps.py).
- **Honest MVP Limitation:** Static predefined 4-tier role hierarchy rather than dynamic attribute-based access control (ABAC).

---

### 13. How does this system scale to 100 cameras?
- **Answer (35s):** "By containerizing AI inference workers across a Kubernetes cluster, streaming detections through an Apache Kafka message broker, and persisting to a PostgreSQL database cluster with MinIO/S3 object storage for evidence archives."
- **Technical Evidence:** Documented in [`SCALABILITY_ROADMAP.md`](file:///Users/hardik/Downloads/IBVAP/SCALABILITY_ROADMAP.md).
- **Honest MVP Limitation:** This enterprise scale architecture is documented as future production roadmap; the current MVP runs as a single-node host.

---

### 14. What happens when multiple cameras trigger intrusions simultaneously?
- **Answer (30s):** "FastAPI processes event submissions asynchronously across non-blocking async database transactions. PostgreSQL foreign keys and indexes handle concurrent writes, and `WebSocketManager` pushes structured JSON alert cards to the UI."
- **Technical Evidence:** [`backend/app/services/event_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/event_service.py) & [`backend/app/api/routes/ws.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/api/routes/ws.py).
- **Honest MVP Limitation:** Single in-process WebSocket connection pool.

---

### 15. What happens under low-light or poor night conditions?
- **Answer (25s):** "The YOLOv8 architecture is modality-agnostic; pre-trained thermal infrared (FLIR) weights can be substituted directly via config without modifying the ByteTrack tracking, polygon geofencing, or backend event pipeline."
- **Technical Evidence:** Configurable model path in [`ai/core/config.py`](file:///Users/hardik/Downloads/IBVAP/ai/core/config.py).
- **Honest MVP Limitation:** Night vision thermal weights require separate model calibration.

---

### 16. What happens during severe target occlusion?
- **Answer (30s):** "ByteTrack uses Kalman filter velocity predictions to estimate target trajectory when bounding boxes are temporarily lost or partially occluded. It maintains track identity for up to 30 buffer frames before retiring the track."
- **Technical Evidence:** [`ai/tracking/tracker.py`](file:///Users/hardik/Downloads/IBVAP/ai/tracking/tracker.py).
- **Honest MVP Limitation:** Complete physical occlusion exceeding 30 frames will register as a new track upon re-emergence.

---

### 17. Is 198.58 FPS true end-to-end inference or just preprocessing?
- **Answer (30s):** "198.58 FPS is the measured throughput of the unified AI ingestion pipeline—including frame reading, YOLOv8 inference, ByteTrack Kalman tracking, foot-point extraction, and Shapely polygon containment—on 300 frames of 1280x720 video on Apple Silicon hardware."
- **Technical Evidence:** Benchmark script [`ai/benchmarks/performance/benchmark_pipeline.py`](file:///Users/hardik/Downloads/IBVAP/ai/benchmarks/performance/benchmark_pipeline.py).
- **Honest MVP Limitation:** Measured on local workstation hardware; edge devices (e.g. Raspberry Pi) will have lower throughput without a GPU accelerator.

---

### 18. What is actually implemented versus proposed?
- **Answer (35s):** "Implemented & verified: YOLOv8 detection, ByteTrack tracking, Polygon PIP, Intrusion state machine, JWT/RBAC auth, FastAPI REST, PostgreSQL persistence, WebSockets, Next.js UI, SHA-256 evidence verification, and Audit logging (183 tests). Proposed for future: Kubernetes scaling, Kafka broker, and S3 object storage."
- **Technical Evidence:** [`M3.6_FINAL_SIH_READINESS_REPORT.md`](file:///Users/hardik/Downloads/IBVAP/M3.6_FINAL_SIH_READINESS_REPORT.md).
- **Honest MVP Limitation:** We do not claim distributed multi-node clustering in the MVP.

---

### 19. What is your single biggest limitation today?
- **Answer (25s):** "Our biggest MVP limitation is single-node deployment: video ingestion, backend API, and database reside on the same local host, which is ideal for tactical edge command posts but requires a distributed broker (Kafka) for enterprise multi-site deployments."
- **Technical Evidence:** Documented in [`KNOWN_LIMITATIONS.md`](file:///Users/hardik/Downloads/IBVAP/KNOWN_LIMITATIONS.md).
- **Honest MVP Limitation:** Localhost scope.

---

### 20. What is the next feature you would build after SIH?
- **Answer (25s):** "We would implement thermal infrared sensor fusion with automated PTZ camera slew-to-cue tracking, allowing a wide-angle camera detection to automatically steer and zoom an optical PTZ camera onto the intruder."
- **Technical Evidence:** [`SCALABILITY_ROADMAP.md`](file:///Users/hardik/Downloads/IBVAP/SCALABILITY_ROADMAP.md).
- **Honest MVP Limitation:** PTZ camera hardware control is post-MVP roadmap.
