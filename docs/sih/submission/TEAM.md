# IBVAP Team Structure & Ownership

This document defines team roles, section ownership, and responsibility boundaries for the IBVAP Internal-Round MVP.

---

## Member Roles

### M1 — Backend Lead
- **Primary Domain**: Backend architecture, FastAPI services, PostgreSQL database, REST & WebSocket endpoints, event persistence.

### M2 — AI / ML Lead
- **Primary Domain**: YOLO object detection, ByteTrack tracking, restricted polygon spatial engine, intrusion event generation.

### M3 — Video / Edge Lead
- **Primary Domain**: Camera ingestion (Webcam, USB, Video File, future RTSP), frame processing, edge pipeline optimization.

### M4 — Frontend Lead
- **Primary Domain**: Next.js dashboard, live video/detection overlay UI, alerts feed, evidence viewer, verification controls.

### M5 — Security & Evidence Lead
- **Primary Domain**: Authentication (JWT), evidence snapshot hashing (SHA-256), tamper verification workflow, security controls, audit logs.

### M6 — Integration, QA & Research Lead
- **Primary Domain**: Cross-module integration, automated testing, benchmarking (FPS, latency), research documentation consolidation, demo validation.

---

## Major Engineering Sections

1. **Backend**: FastAPI, Database, REST/WebSocket APIs, Evidence metadata (M1, M5)
2. **Frontend**: Next.js Dashboard, Real-time Alerts, Evidence Verification UI (M4)
3. **AI**: Camera ingestion, YOLO, ByteTrack, Virtual Fencing, Event Engine (M2, M3)
4. **Integration**: End-to-end orchestration, Docker setups, Testing & Benchmarking (M6)
