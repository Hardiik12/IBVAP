# IBVAP — Architecture Decision Records (ADRs)
## SIH Internal Round MVP

---

## ADR-001: Monorepo Directory Structure

- **Context**: The team consists of 6 developers split into 4 core sections (AI, Backend, Frontend, Integration).
- **Decision**: Adopt a clean monorepo structure (`ai/`, `backend/`, `frontend/`, `integration/`, `docs/`, `data/`) with explicitly isolated virtual environments and dependency specifications.
- **Rationale**: Enables concurrent development without cross-module corruption while maintaining unified documentation and configuration control.
- **Status**: ACCEPTED.

---

## ADR-002: Camera Source Abstraction (Webcam First over RTSP)

- **Context**: Real-world border surveillance uses RTSP/IP cameras, but network streams introduce setup fragility during time-constrained Hackathon evaluations.
- **Decision**: Abstract frame ingestion behind a `CameraSource` interface, prioritizing USB/built-in webcams and recorded video files for the MVP, while leaving RTSP as a future plugin.
- **Rationale**: Guarantees 100% demo reliability on standard evaluation laptops without hardware or network stream dependencies.
- **Status**: ACCEPTED.

---

## ADR-003: Model Selection & Internal Data Normalization

- **Context**: Object detection models evolve rapidly; tying backend logic directly to Ultralytics YOLO output creates brittle coupling.
- **Decision**: Use Ultralytics YOLOv8n + ByteTrack for the MVP, but convert all raw outputs into internal `NormalizedDetection` and `Track` data structures.
- **Rationale**: Allows replacing or upgrading the detector/tracker in the future without altering the spatial zone engine, event engine, or database schemas.
- **Status**: ACCEPTED.

---

## ADR-004: Bottom-Center Bounding Box Reference Point for Zone Testing

- **Context**: Bounding boxes represent 2D rectangular areas, but point-in-polygon spatial containment testing requires discrete coordinate points.
- **Decision**: Compute spatial reference coordinates using the bottom-center of the person bounding box: $(\frac{x_1+x_2}{2}, y_2)$.
- **Rationale**: In ground-plane surveillance, the bottom-center of a person's bounding box accurately represents where their feet touch the ground, producing intuitive intrusion detection when crossing perimeter lines.
- **Status**: ACCEPTED.

---

## ADR-005: SHA-256 Evidence Hashing over Blockchain

- **Context**: Digital evidence requires verifiable tamper detection. Blockchain is frequently proposed but adds heavy runtime complexity and external RPC dependencies.
- **Decision**: Compute standard cryptographic SHA-256 hashes of snapshot images upon event capture, store the hash digest in PostgreSQL, and provide an instant recalculation verification API.
- **Rationale**: Demonstrates deterministic tamper detection with sub-10ms execution speed, zero external network dependency, and complete cryptographic rigor. (Clarification: SHA-256 proves file integrity against post-capture tampering, not real-world event authenticity).
- **Status**: ACCEPTED.

---

## ADR-006: FastAPI + PostgreSQL + Next.js Stack Selection

- **Context**: Need a responsive, real-time web application capable of handling WebSocket event streaming and low-latency API queries.
- **Decision**: Select Python FastAPI + PostgreSQL for backend/database and Next.js 14 (React 18 + TypeScript + Tailwind CSS) for the frontend dashboard.
- **Rationale**: FastAPI provides high-throughput async processing and native WebSockets. Next.js offers modern SSR/SPA rendering and clean UI component architecture.
- **Status**: ACCEPTED.

---

## ADR-007: Track State Machine & Alert Suppression

- **Context**: A person remaining inside a restricted zone across 300 consecutive frames would generate 300 duplicate intrusion alerts if checked statelessly per frame.
- **Decision**: Implement a state machine tracking `OUTSIDE` → `INSIDE` state transitions per `track_id`. Emit an `INTRUSION` event **only on the positive transition edge**, maintaining state while inside and resetting only upon exit.
- **Rationale**: Eliminates alert spam, preserves operator sanity, and drastically reduces database write load while ensuring reliable incident capture.
- **Status**: ACCEPTED.

---

## ADR-008: Evidence Relational Deletion Restriction Policy

- **Context**: Cascading deletes (`CASCADE`) on event records would automatically destroy associated digital evidence records, corrupting the digital chain of custody.
- **Decision**: Configure foreign key constraints on `evidence.event_id` with `ondelete="RESTRICT"`.
- **Rationale**: Ensures evidence snapshot metadata and cryptographic SHA-256 hashes cannot be destroyed accidentally by deleting an event record, preserving auditability and legal integrity.
- **Status**: ACCEPTED.

---

## ADR-009: Soft Deactivation Policy for Cameras & Zones

- **Context**: Deleting a camera or zone config record using hard SQL `DELETE` cascades to dependent tables (such as events, alerts, and audit logs), which compromises historical security logs.
- **Decision**: Endpoints `DELETE /api/v1/cameras/{id}` and `DELETE /api/v1/zones/{id}` execute soft deactivation (`is_active = False`) instead of hard deletion.
- **Rationale**: Retains all operational log references, event records, and evidence chain of custody intact while ensuring the camera/zone no longer participates in active AI processing.
- **Status**: ACCEPTED.

---

## ADR-010: Event Immutability & Alert Suppressions

- **Context**: Event logs are critical historical records of border breaches. Deleting or modifying event identifiers, timestamps, or spatial camera/zone links after the fact would allow tampering with surveillance history.
- **Decision**: Restrict Event updates to status, severity, and metadata fields, forbidding other inputs via strict schema validations (`extra="forbid"`). Disable `DELETE` operations on Event endpoints entirely.
- **Rationale**: Guarantees the stability of the historical audit trail, while automatically linking intrusion events to active alerts inside atomic transactions.
- **Status**: ACCEPTED.

---

## ADR-011: Database Persistence Strategy for Unhashed Evidence

- **Context**: Evidence records must support cryptographic verification. While the Phase 2 database schema sets `sha256_hash` to `NOT NULL` in PostgreSQL, the SHA-256 hashing computation service is deferred until Phase 6.
- **Decision**: Persist newly created evidence records with an empty string `""` in the `sha256_hash` column.
- **Rationale**: Resolves database NOT NULL constraints without altering Alembic migrations, keeping the schema clean and stable until the integrity engine is implemented in the next phase.
- **Status**: ACCEPTED.

---

## ADR-012: Authentication, RBAC & Audit Trail Security Policy

- **Context**: Access control, password security, and administrative oversight must prevent unauthorized system modifications and protect evidence integrity.
- **Decision**:
  1. Use **Argon2id** (`pwdlib`) for password hashing.
  2. Implement Bearer **JWT tokens** with configurable expiration (`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, default 30 min).
  3. Enforce **RBAC Matrix** across endpoints (`OPERATOR`, `ANALYST`, `ADMINISTRATOR`, `AUDITOR`).
  4. Block self-deactivation or demotion of the final active administrator.
  5. Log audit events for `LOGIN_SUCCESS`, `LOGIN_FAILURE`, `CAMERA_CREATED/UPDATED/DEACTIVATED`, `ZONE_CREATED/UPDATED/DEACTIVATED`, `ALERT_ACKNOWLEDGED`, `EVIDENCE_VERIFIED`, and `USER_CREATED/UPDATED`.
- **Rationale**: Ensures OWASP-compliant password security, precise authorization boundaries, and tamper-resistant administrative tracking.
- **Status**: ACCEPTED.

---

## ADR-013: In-Process WebSocket Connection Manager & Query-Token Authentication for Internal Round MVP

- **Context**: Real-time event notifications must be delivered to operational dashboard clients without adding complex network infrastructure dependencies.
- **Decision**:
  1. Implement an **in-process FastAPI connection manager** (`WebSocketManager`) without external message brokers (no Redis, Kafka, or Celery).
  2. Authenticate WebSocket handshakes using JWT access tokens passed via query parameters (`WS /api/v1/ws/events?token=<access_token>`).
  3. Trigger broadcasts strictly **post-commit** after database write operations succeed.
- **Rationale**: Meets SIH internal round MVP requirements with zero external infrastructure overhead while preserving atomic database transactions.
- **Limitation**: The in-memory registry is designed for a single backend instance and does not synchronize active connections across multi-instance production clusters (which can be introduced in production phases using Redis Pub/Sub).
- **Status**: ACCEPTED.
