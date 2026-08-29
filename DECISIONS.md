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
