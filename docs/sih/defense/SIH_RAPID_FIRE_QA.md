# IBVAP — Top 20 Judge Rapid-Fire Q&A Cheat Sheet

**Answer Length:** 20–40 Seconds Each  
**Focus:** Technical Precision, Directness, Empirical Facts  

---

### 1. Why use ByteTrack instead of DeepSORT?
"DeepSORT uses a heavy appearance descriptor model that reduces throughput. ByteTrack associates both high-confidence and low-confidence detection boxes using Kalman filtering, maintaining persistent identities through occlusion while maintaining over 198 FPS throughput."

### 2. How do you prevent false positive alerts from shadows or wind?
"We extract the ground-contact foot point $[x_{center}, y_{bottom}]$ of the detection box rather than the bounding box centroid. Shadows and upper-body extremities do not trigger alerts unless the physical ground contact crosses the polygon boundary."

### 3. What happens if an intruder stays inside the zone for 10 minutes?
"Our intrusion engine uses a deterministic state machine. An alert is emitted strictly on the `OUTSIDE` $\to$ `INSIDE` state transition. While the track remains inside, redundant alerts are suppressed, preventing alert flooding."

### 4. How does the AI worker authenticate to the backend?
"The AI `EventDispatcher` holds scoped service credentials, acquires a JWT bearer token, and signs every event submission to `/api/v1/events`, utilizing exponential backoff retry in case of transient network drops."

### 5. Why is SHA-256 evidence hashing done on the server and not the browser?
"The browser cannot be trusted as an evidentiary authority. Computing the SHA-256 digest on the backend directly from raw frame bytes guarantees non-repudiation and prevents client-side forgery."

### 6. What happens if someone modifies an evidence image directly on disk?
"When an operator clicks 'Verify Integrity', the backend re-reads the raw disk bytes, computes the current SHA-256 hash, and compares it to the database digest. Any 1-bit alteration immediately triggers 🔴 `TAMPER DETECTED`."

### 7. How does WebSocket authentication prevent eavesdropping?
"WebSocket connections require a valid JWT passed during the initial HTTP handshake. The backend validates the signature and claims before upgrading the connection, rejecting unauthenticated clients with WebSocket close code 1008."

### 8. What is the measured system throughput and latency?
"Our AI ingestion benchmark measures **198.58 FPS** on 1280x720 video. Event persistence from detection to PostgreSQL commit takes **50–65 ms**, followed by sub-10ms WebSocket delivery to the frontend."

### 9. How do you prevent duplicate events from network retries?
"Events contain a deterministic `event_identifier` derived from camera ID, track ID, and timestamp window. If submitted twice, PostgreSQL unique constraints return HTTP 409 Conflict, ensuring exactly-once persistence."

### 10. What happens if the AI model weights are corrupted or replaced?
"IBVAP implements a fail-closed model integrity check. On startup, the engine computes the SHA-256 hash of the `.pt` weights and compares it to `AI_MODEL_SHA256`. A mismatch raises a `RuntimeError` and immediately halts execution."

### 11. How does your RBAC model separate operator duties?
"We enforce four discrete roles: `ADMINISTRATOR` (full management), `OPERATOR` (operational monitoring and alert acknowledgment), `ANALYST` (read-only telemetry), and `AUDITOR` (immutable audit log review and forensic verification)."

### 12. How does the UI handle backend disconnections?
"The Next.js frontend catches network failures, displays `BACKEND ● OFFLINE | DB: DISCONNECTED`, and initiates bounded exponential backoff reconnection without crashing or displaying synthetic fallback data."

### 13. What database is used and why?
"We use PostgreSQL for its ACID transaction guarantees, strict foreign key constraints between events, alerts, and evidence, and robust JSONB support for normalized polygon coordinate geometries."

### 14. Why isn't Docker being run during the live presentation?
"To showcase pure native performance and avoid disk virtualization bottlenecks on our presentation laptop. Docker Compose manifests are fully configured and verified in our repository."

### 15. How would this system scale to 100 border cameras?
"By deploying distributed AI worker containers across a Kubernetes cluster, streaming events through an Apache Kafka message broker to a load-balanced FastAPI ingestion pool with Redis Pub/Sub WebSocket gateways."

### 16. What is stored in the audit log?
"Every security-relevant event: successful and failed logins, role changes, zone modifications, alert acknowledgments, and SHA-256 verification checks, along with user ID, client IP, and UTC timestamps."

### 17. How do you handle nighttime or low-light conditions?
"The YOLOv8 pipeline can be swapped or fused with thermal infrared (FLIR) weights without altering the tracking, geofencing, event dispatch, or evidence verification architecture."

### 18. What prevents an operator from falsely claiming an alert was not received?
"The post-commit WebSocket broadcast records the dispatch timestamp, and operator acknowledgment is permanently recorded in the append-only `audit_logs` table with their user ID and timestamp."

### 19. How many regression tests does the codebase have?
"We maintain a comprehensive suite of **183 automated tests** covering REST endpoints, RBAC permissions, WebSocket authentication, AI tracking, polygon ray-casting, model validation, and security audit vectors."

### 20. What is the single biggest technical achievement of this project?
"Transforming unauthenticated raw video pixels into a closed-loop, cryptographically verifiable, and legally auditable security pipeline in sub-100 milliseconds."
