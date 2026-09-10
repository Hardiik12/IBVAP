# IBVAP — SIH Judge Technical Q&A Defense Guide

This document prepares the team with authoritative, technically precise answers to the 30 most critical architecture, security, AI, and scalability questions during the SIH evaluation.

---

### 1. Why is this problem important?
Border security requires continuous, 24/7 monitoring across vast geographic sectors. Human operators suffer from visual fatigue within 20 minutes, leading to missed incursions. IBVAP eliminates cognitive overload by autonomously converting raw video into cryptographically verified, actionable intrusion alerts with an immutable audit trail.

### 2. What makes IBVAP different from a normal CCTV system?
Traditional CCTV is passive and unauthenticated. IBVAP provides active AI inference (YOLOv8 + ByteTrack), polygon zone ray-casting, instant WebSocket push notifications, and cryptographic SHA-256 chain-of-custody verification to prevent digital evidence tampering.

### 3. Why YOLOv8?
YOLOv8 provides the optimal Pareto frontier between inference throughput (198+ FPS) and mean average precision (mAP) for real-time edge surveillance, supporting person, vehicle, and animal classifications with minimal latency.

### 4. Why ByteTrack?
Unlike Simple Online and Realtime Tracking (SORT) which discards low-score detection boxes, ByteTrack associates both high-score and low-score boxes using Kalman filtering, maintaining persistent identity during occlusion, shadow transitions, and partial camera obstruction.

### 5. How is an intrusion defined?
An intrusion is defined by a deterministic state transition machine: an object with a persistent Track ID moving from `OUTSIDE` the virtual polygon boundary to `INSIDE` across consecutive video frames.

### 6. How are zones represented?
Zones are represented as normalized 2D polygon coordinate arrays `[[x1, y1], [x2, y2], ...]`, where $0.0 \le x, y \le 1.0$, rendering them independent of physical camera resolution and aspect ratio.

### 7. How does the AI communicate with the backend?
The AI worker uses an authenticated `EventDispatcher` that signs HTTP POST requests with a scoped JWT bearer token to `/api/v1/events`, utilizing exponential backoff retry in the event of transient network drops.

### 8. Why use JWT?
JSON Web Tokens (JWT) provide stateless, cryptographically signed bearer credentials (HMAC-SHA256) containing operator identity, role claims, and strict 15-minute expiration windows without requiring database session lookups on every request.

### 9. How does RBAC work?
Role-Based Access Control is enforced at the FastAPI dependency layer (`require_role`), separating permissions across `ADMINISTRATOR` (full management), `OPERATOR` (operational mutations & alert ACK), `ANALYST` (read-only telemetry), and `AUDITOR` (audit log and evidence review).

### 10. How do you prevent duplicate events?
Idempotency is enforced by computing a deterministic `event_identifier` from the camera ID, track ID, and intrusion timestamp window. If the same event is submitted again, PostgreSQL unique constraints trigger an HTTP 409 Conflict, which the dispatcher treats as an idempotent success.

### 11. How do you prevent fake AI events?
The `/api/v1/events` endpoint is restricted to authenticated AI service credentials, validates camera and zone database IDs, and rejects any payload lacking cryptographic JWT authorization.

### 12. How do you detect evidence tampering?
When evidence is captured, its binary SHA-256 hash is computed immediately and stored in PostgreSQL. During forensic inspection, the backend re-reads the physical disk file, recalculates the SHA-256 digest, and flags any bit-level difference as 🔴 `MISMATCH (TAMPER DETECTED)`.

### 13. Why SHA-256?
SHA-256 is an NIST-approved, collision-resistant cryptographic hash function producing a 256-bit (64-hexadecimal) digest with $2^{128}$ preimage resistance, guaranteeing evidentiary integrity in legal and military forensics.

### 14. Where is the hash generated?
The hash is generated exclusively on the backend server (`hashlib.sha256`) at the exact moment of frame persistence. The frontend never computes or dictates the authoritative checksum.

### 15. Can a user modify the stored hash?
No. The `sha256_hash` database column is immutable after creation and cannot be updated through public REST APIs. Any modification to the database or disk produces an immediate verification mismatch.

### 16. How does WebSocket authentication work?
Clients must provide a valid JWT via the query parameter `?token=<JWT>`. During the WebSocket handshake, FastAPI verifies the token signature and claims, closing unauthenticated connections with code `1008 (Policy Violation)`.

### 17. What happens if WebSocket disconnects?
The frontend `useWebSocket` hook catches the disconnect, transitions the UI status to `WS: OFFLINE`, and initiates bounded exponential backoff reconnection (up to 10 attempts, 10s maximum delay) without dropping historical data.

### 18. What happens if the backend goes offline?
The frontend status badge immediately switches to `BACKEND ● OFFLINE | DB: DISCONNECTED`. REST services surface clean offline banners without crashing or displaying synthetic mock data.

### 19. What happens if PostgreSQL goes offline?
The backend health check reports `database: disconnected`. Transient queries return structured 503 Service Unavailable errors, and `audit_logs` are preserved up to the moment of disconnection.

### 20. What happens if the YOLO model is corrupted?
The AI engine validates the model weights against `AI_MODEL_SHA256` before loading. If the checksum fails, the system triggers a `RuntimeError` and terminates immediately (Fail-Closed architecture) rather than running compromised inference.

### 21. What happens if the same event is sent twice?
The backend returns HTTP 409 Conflict. The database rejects the duplicate, and the WebSocket broadcaster suppresses duplicate event broadcasts.

### 22. How does audit logging work?
Every security event (login success/failure, zone modification, alert acknowledgement, evidence verification) is committed to an append-only `audit_logs` table recording the user ID, action enum, resource ID, client IP, and UTC timestamp.

### 23. What happens if evidence is missing?
The verification endpoint returns HTTP 404 with a structured error `Evidence snapshot file not found on disk`, cleanly rendered in the UI without exposing internal server paths.

### 24. What is the measured FPS?
The unified video ingestion benchmark measured **198.58 FPS** on 300 frames of 1280x720 video on Apple Silicon local hardware, exceeding the real-time threshold (30 FPS) by 6.6x.

### 25. What is the event latency?
Event dispatch from AI intrusion detection to PostgreSQL commit executes in approximately **50–65 ms**, followed by sub-10ms WebSocket broadcast to the React frontend.

### 26. Is the system production-ready?
The core platform is fully functional and hardened for the SIH MVP. Production enhancements (TLS certificates, Redis Pub/Sub cluster, object storage archives) are documented in the Scalability Roadmap.

### 27. Why isn't Docker being used for the presentation?
To eliminate virtualization overhead, prevent disk container bottlenecks during the live demo, and showcase pure native Python/FastAPI and Next.js performance on local host. Docker Compose manifests remain verified in the repository.

### 28. How would this scale to multiple cameras?
By deploying multiple containerized AI worker instances, each consuming an RTSP stream and dispatching events asynchronously to the centralized FastAPI/PostgreSQL cluster.

### 29. How would this scale to multiple AI workers?
By placing a Redis Pub/Sub or Apache Kafka message broker between the AI dispatchers and backend ingestion workers, load balancing event streams across worker pools.

### 30. What would you change for production?
For national border deployment: migrate to HTTPS/TLS certificates, implement MinIO/S3 object storage for multi-year evidence retention, deploy a distributed Redis WebSocket gateway, and enable Argon2id hardware-accelerated authentication nodes.
