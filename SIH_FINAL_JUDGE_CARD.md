# IBVAP — SIH Final Judge Defense Master Card

Keep this quick-defense card accessible for rapid-fire technical questions from the judging panel.

---

### 1. What problem does IBVAP solve?
"Eliminates human visual fatigue in 24/7 border monitoring, filters false alarms through state-machine geofencing, and guarantees digital evidence integrity with cryptographic SHA-256 validation."

### 2. Why YOLOv8?
"Delivers an optimal balance of high throughput (198+ FPS) and mean average precision (mAP) for multi-class detection (person, vehicle, animal) with sub-10ms inference latency."

### 3. Why ByteTrack?
"Unlike traditional trackers, ByteTrack associates both high-score and low-score detection boxes using Kalman filtering, maintaining persistent identity during occlusion without the heavy computational cost of appearance embeddings."

### 4. How is an intrusion determined?
"Through bottom-center foot-point extraction $[x_{center}, y_{bottom}]$ evaluated against a normalized polygon boundary via Shapely ray-casting Point-in-Polygon (PIP) analysis."

### 5. Why polygon zones instead of rectangles?
"Border perimeters, roads, and fences follow irregular geometric lines. Arbitrary 2D polygons fit natural topography and prevent false triggers on adjacent permitted zones."

### 6. How do you prevent duplicate events?
"Intrusion alerts trigger strictly on `OUTSIDE` $\to$ `INSIDE` state transitions. Continuous presence inside the polygon is suppressed. Re-sent packets are rejected via deterministic `event_identifier` unique constraints (HTTP 409)."

### 7. How does the AI authenticate with the backend?
"The AI worker uses an authenticated `EventDispatcher` holding scoped credentials to sign HTTP POST requests with a 15-minute JWT bearer token to `/api/v1/events`."

### 8. How does RBAC work?
"Enforces 4 discrete role boundaries at the API layer: `ADMINISTRATOR` (full control), `OPERATOR` (monitoring & alert ACK), `ANALYST` (telemetry view), and `AUDITOR` (immutable audit log review)."

### 9. How is evidence tampering detected?
"A SHA-256 hash is computed at the moment of frame persistence. During inspection, the backend recalculates the hash from disk bytes. Any 1-bit difference immediately triggers 🔴 `TAMPER DETECTED`."

### 10. Why SHA-256?
"NIST-approved, collision-resistant cryptographic hash function producing a 256-bit digest with $2^{128}$ preimage resistance, guaranteeing court-admissible chain of custody."

### 11. What happens if the backend goes offline?
"The frontend status badge switches to `BACKEND ● OFFLINE | DB: DISCONNECTED`. It surfaces clean offline notices without crashing or displaying synthetic mock data, auto-reconnecting upon recovery."

### 12. What happens if the AI model is corrupted?
"On startup, the AI engine verifies the weights file against `AI_MODEL_SHA256`. If the digest fails, it triggers a `RuntimeError` and terminates immediately (Fail-Closed architecture)."

### 13. How does WebSocket delivery work?
"Clients authenticate via query token `?token=<JWT>`. Upon PostgreSQL database commit, `NotificationService` pushes structured JSON alert cards directly to connected UI clients in <10ms."

### 14. Why PostgreSQL?
"Provides ACID transactional integrity for alerts and audit logs, foreign key constraints ensuring evidence cannot be orphaned, and robust JSONB support for polygon geometries."

### 15. How would this scale to thousands of cameras?
"By deploying distributed GPU AI workers streaming events through an Apache Kafka message broker to a load-balanced FastAPI ingestion pool with MinIO/S3 object storage and Redis Pub/Sub WebSocket gateways."

### 16. What is currently implemented?
"Complete end-to-end stack: YOLOv8, ByteTrack, Polygon PIP, State Machine, EventDispatcher, FastAPI REST, PostgreSQL, JWT/RBAC, WebSockets, Next.js UI, SHA-256 verification, and Audit logging."

### 17. What remains future work?
"Production cloud scaling: distributed Kafka event streaming, S3 object storage for multi-year retention, and thermal infrared sensor fusion for zero-light night operations."

### 18. What makes this different from a simple CCTV system?
"Traditional CCTV passively records unverified video. IBVAP autonomously detects, tracks, filters, pushes real-time alerts, and provides mathematically tamper-proof evidence with an immutable audit trail."
