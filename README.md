# IBVAP — Intelligent Border Video Analytics Platform
## Smart India Hackathon (SIH) Internal Round MVP

**Status**: 🟢 **FROZEN & DEMO READY** | **Test Baseline**: 183 / 183 PASSED | **Pipeline Throughput**: 198+ FPS  

---

## 1. Executive Overview
IBVAP is an end-to-end autonomous border surveillance platform that transforms live camera video into cryptographically verifiable intrusion alerts. Combining real-time **YOLOv8** object detection, **ByteTrack** multi-object tracking, and **Polygon Point-in-Polygon (PIP)** ray-casting geofencing, IBVAP delivers instant sub-65ms event persistence and sub-10ms WebSocket alert dispatching to a tactical Next.js command center with server-authoritative **SHA-256 binary evidence integrity verification** and immutable security audit logging.

---

## 2. Quickstart — Local Live Demonstration (No Docker Required)

### Step 1: Start PostgreSQL
```bash
# Verify local database is active:
pg_isready -h localhost -p 5432
# Seed default roles, cameras, and zones:
PYTHONPATH=. backend/.venv/bin/python backend/app/db/seed.py
```

### Step 2: Start FastAPI Backend
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Health endpoint:* `http://localhost:8000/health`

### Step 3: Start Next.js Tactical UI
```bash
cd frontend
npm run dev
```
*Access UI:* `http://localhost:3000` (Log in with `admin` / demo credentials)

### Step 4: Run AI Video Pipeline
```bash
PYTHONPATH=. backend/.venv/bin/python ai/pipeline/runner.py --source VIDEO_FILE --video-path data/videos/benchmark/benchmark_1280x720.avi
```
*(Or run live camera with `--source WEBCAM`)*

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

## 🚀 Quick Start (Docker Compose)

The complete IBVAP stack can be launched reproducibly in a single command:

```bash
# 1. Clone repository and navigate to root
git clone <repo-url>
cd IBVAP

# 2. Copy environment template
cp .env.example .env

# 3. Build and launch all services in background
docker compose up --build -d

# 4. View live logs
docker compose logs -f

# 5. Stop all services (preserves database volume)
docker compose down

# 6. Reset database volume (clean state)
docker compose down -v
```

### 🌐 Service Endpoints

| Service | Container Name | Host URL | Description |
| :--- | :--- | :--- | :--- |
| **Frontend Dashboard** | `ibvap-frontend` | `http://localhost:3000` | Operational Next.js dashboard & real-time alerts |
| **FastAPI Backend** | `ibvap-backend` | `http://localhost:8000` | REST API, OpenAPI docs (`/docs`), and `/health` |
| **WebSocket Stream** | `ibvap-backend` | `ws://localhost:8000/api/v1/ws/events` | Real-time intrusion notification broadcast |
| **PostgreSQL Database**| `ibvap-postgres` | Internal (`5432`) | SQLAlchemy 2.0 relational persistence |
| **AI Ingestion Engine**| `ibvap-ai` | Internal (`http://backend:8000`) | Headless YOLOv8 + ByteTrack video processing |

---

## 💻 Local Host Development Mode (Native Webcam Support)

For live macOS webcam demonstrations with Tactical HUD preview:

```bash
# 1. Start backend database
docker compose up -d postgres

# 2. Start FastAPI backend locally
cd backend
source .venv/bin/activate
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload --port 8000

# 3. Run Live AI Pipeline with USB/Built-in Webcam (in separate terminal)
cd ..
source backend/.venv/bin/activate
python -m ai.pipeline.runner --source webcam --index 0
```

---

## 🎯 Current Status

- **M1 Backend Platform**: COMPLETE (FastAPI, PostgreSQL, Alembic, Auth, WebSockets, SHA-256 evidence integrity).
- **M2 Computer Vision & AI**: COMPLETE (YOLOv8n, ByteTrack, PolygonZone, IntrusionEventEngine).
- **M2.6 AI $\rightarrow$ M1 Integration**: COMPLETE (HTTP EventDispatcher, JWT authentication, retry policy, Tactical HUD).
- **M3.1 Security Hardening**: COMPLETE (Model SHA-256 verification, path traversal protection, CORS, brute-force throttling).
- **M3.2 Docker Compose**: COMPLETE (4-tier containerized stack with healthchecks and persistent volumes).
- **Test Suite**: **182 / 182 Tests Passing** (100% pass rate).

---

## 👥 Team Structure & Ownership

- **M1 (Backend Lead)**: FastAPI REST endpoints, PostgreSQL DB, SQLAlchemy ORM, Alembic migrations.
- **M2 (AI/ML Lead)**: YOLO object detection, ByteTrack tracking, Polygon zone engine, Event state machine.
- **M3 (Video/Edge Lead)**: Camera abstraction, OpenCV frame ingestion pipeline, video stream optimization.
- **M4 (Frontend Lead)**: Next.js App Router, Operational Dashboard views, Canvas bounding box overlays, WebSockets.
- **M5 (Security & DevOps Lead)**: JWT Authentication, RBAC, Evidence SHA-256 engine, Docker containerization.
- **M6 (Integration / QA Lead)**: E2E orchestration, test dataset validation, performance benchmarking, SIH presentation story.

---

## ⚙️ Development Guidelines

1. **Do not directly push to `main`**. Use feature branches and pull requests.
2. **Never commit secrets or credentials**.
3. **Follow the phase-gated execution plan** in [`TASKS.md`](file:///Users/hardik/Downloads/IBVAP/TASKS.md).

