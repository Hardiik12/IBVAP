# IBVAP — Intelligent Border Video Analytics Platform
## SIH Internal Round MVP

An AI-powered video analytics platform designed to assist security personnel by converting continuous camera/video feeds into actionable security events.

---

## 📌 Master Documentation Index

- **[Master Project Document (`PROJECT.md`)](file:///Users/hardik/Downloads/IBVAP/PROJECT.md)** — Core master document, vision, 16-step demo story, and SIH Internal Round MVP scope.
- **[Product Requirements (`PRD.md`)](file:///Users/hardik/Downloads/IBVAP/PRD.md)** — User personas, functional/non-functional requirements, KPIs.
- **[System Requirements (`REQUIREMENTS.md`)](file:///Users/hardik/Downloads/IBVAP/REQUIREMENTS.md)** — Hardware, software runtimes, dependencies, and environment specs.
- **[Technology Stack (`TECH_STACK.md`)](file:///Users/hardik/Downloads/IBVAP/TECH_STACK.md)** — Tech selection matrix and architectural rationale.
- **[System Architecture (`ARCHITECTURE.md`)](file:///Users/hardik/Downloads/IBVAP/ARCHITECTURE.md)** — End-to-end dataflow, AI pipeline lifecycle, and evidence hashing architecture.
- **[API Specification (`API.md`)](file:///Users/hardik/Downloads/IBVAP/API.md)** — REST API endpoints, WebSocket contracts, payload schemas.
- **[Database Design (`DATABASE.md`)](file:///Users/hardik/Downloads/IBVAP/DATABASE.md)** — Relational ERD, table DDLs, and efficient data storage strategy.
- **[AI Agent Rules (`AGENTS.md`)](file:///Users/hardik/Downloads/IBVAP/AGENTS.md)** — Mandatory directives and stop rules for AI coding assistants.
- **[Implementation Tasks (`TASKS.md`)](file:///Users/hardik/Downloads/IBVAP/TASKS.md)** — Phased roadmap (Phase 0 to Phase 11) and task matrix.
- **[Architecture Decisions (`DECISIONS.md`)](file:///Users/hardik/Downloads/IBVAP/DECISIONS.md)** — Architecture Decision Records (ADRs 001–007).

---

## 🎯 Current Status

- **Repository Status**: Repository initialized & documentation completed.
- **Current Phase**: Phase 0 complete. Phase 1 (Camera Ingestion Abstraction) pending authorization.

---

## 👥 Team Structure & Ownership

- **M1 (Backend Lead)**: FastAPI REST endpoints, PostgreSQL DB, SQLAlchemy ORM, Alembic migrations.
- **M2 (AI/ML Lead)**: YOLO object detection, ByteTrack tracking, Polygon zone engine, Event state machine.
- **M3 (Video/Edge Lead)**: Camera abstraction, OpenCV frame ingestion pipeline, video stream optimization.
- **M4 (Frontend Lead)**: Next.js App Router, Operational Dashboard views, Canvas bounding box overlays, WebSockets.
- **M5 (Security & Evidence Lead)**: JWT Authentication, RBAC, Evidence file management, SHA-256 integrity verification engine.
- **M6 (Integration / QA Lead)**: E2E orchestration, test dataset validation, performance benchmarking, SIH presentation story.

---

## ⚙️ Development Guidelines

1. **Do not directly push to `main`**. Use feature branches and pull requests.
2. **Never commit secrets or credentials**.
3. **Follow the phase-gated execution plan** in [`TASKS.md`](file:///Users/hardik/Downloads/IBVAP/TASKS.md).
