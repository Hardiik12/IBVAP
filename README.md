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

All project documentation, specifications, SIH pitch decks, judge defense cards, demo runbooks, and milestone validation reports are organized in the [`docs/`](file:///Users/hardik/Downloads/IBVAP/docs/) directory:

### 📐 Specifications & Architecture (`docs/specs/`)
- **[`PROJECT.md`](file:///Users/hardik/Downloads/IBVAP/docs/specs/PROJECT.md)** — Master project document, core vision, 16-step demo story, and SIH MVP scope.
- **[`ARCHITECTURE.md`](file:///Users/hardik/Downloads/IBVAP/docs/specs/ARCHITECTURE.md)** — End-to-end dataflow, AI pipeline lifecycle, and evidence hashing architecture.
- **[`PRD.md`](file:///Users/hardik/Downloads/IBVAP/docs/specs/PRD.md)** — Product requirements, personas, and functional requirements.
- **[`API.md`](file:///Users/hardik/Downloads/IBVAP/docs/specs/API.md)** — REST API specifications, WebSocket data contracts, and schema definitions.
- **[`DATABASE.md`](file:///Users/hardik/Downloads/IBVAP/docs/specs/DATABASE.md)** — Relational ERD, table DDLs, and storage strategy.
- **[`DECISIONS.md`](file:///Users/hardik/Downloads/IBVAP/docs/specs/DECISIONS.md)** — Architecture Decision Records (ADRs 001–014).
- **[`REQUIREMENTS.md`](file:///Users/hardik/Downloads/IBVAP/docs/specs/REQUIREMENTS.md)** & **[`TECH_STACK.md`](file:///Users/hardik/Downloads/IBVAP/docs/specs/TECH_STACK.md)** — Hardware/software runtimes and tech selection rationale.
- **[`TASKS.md`](file:///Users/hardik/Downloads/IBVAP/docs/specs/TASKS.md)** — Phased development roadmap and task matrix.

### 🎤 SIH Presentation & Pitch Decks (`docs/sih/presentation/`)
- **[`SIH_PRESENTATION.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/presentation/SIH_PRESENTATION.md)** — Complete 10-slide SIH Internal Round presentation slide deck.
- **[`SIH_LIVE_DEMO_SPOKEN_SCRIPT.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/presentation/SIH_LIVE_DEMO_SPOKEN_SCRIPT.md)** — Synchronized spoken script with timestamp checkpoints.
- **[`SIH_PITCH_3_MIN.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/presentation/SIH_PITCH_3_MIN.md)** & **[`IBVAP_ELEVATOR_PITCH.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/presentation/IBVAP_ELEVATOR_PITCH.md)** — 3-minute, 60s, and 30s pitch formulations.

### 🛡️ Judge Defense & Q&A (`docs/sih/defense/`)
- **[`SIH_JUDGE_QA.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/defense/SIH_JUDGE_QA.md)** & **[`SIH_RAPID_FIRE_QA.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/defense/SIH_RAPID_FIRE_QA.md)** — Defenses for edge compute, accuracy, latency, and security.
- **[`SIH_MOCK_JUDGE_INTERROGATION.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/defense/SIH_MOCK_JUDGE_INTERROGATION.md)** — 15 simulated judge challenges and technical defenses.
- **[`SIH_CODE_DEFENSE_CARD.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/defense/SIH_CODE_DEFENSE_CARD.md)** — File-and-line code defense index.

### 🚀 Demo Runbooks & Command Cards (`docs/sih/demo/`)
- **[`SIH_FINAL_DEMO_RUNBOOK.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/demo/SIH_FINAL_DEMO_RUNBOOK.md)** — Step-by-step presentation execution guide.
- **[`LOCAL_DEMO_STARTUP.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/demo/LOCAL_DEMO_STARTUP.md)** & **[`SIH_DEMO_COMMAND_CARD.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/demo/SIH_DEMO_COMMAND_CARD.md)** — Fast startup commands.
- **[`SIH_DEMO_BACKUP_PLAN.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/demo/SIH_DEMO_BACKUP_PLAN.md)** & **[`SIH_DEMO_FAILURE_PLAYBOOK.md`](file:///Users/hardik/Downloads/IBVAP/docs/sih/demo/SIH_DEMO_FAILURE_PLAYBOOK.md)** — Zero-fail contingency protocols.

### 📊 Milestone Reports & Security Audits (`docs/reports/`)
- **[`FINAL_RELEASE_VALIDATION_REPORT.md`](file:///Users/hardik/Downloads/IBVAP/docs/reports/FINAL_RELEASE_VALIDATION_REPORT.md)** — 12-phase read-only release candidate validation.
- **[`RBAC_SECURITY_CONSISTENCY_AUDIT.md`](file:///Users/hardik/Downloads/IBVAP/docs/reports/RBAC_SECURITY_CONSISTENCY_AUDIT.md)** — Comprehensive RBAC & security consistency audit.
- **[`RBAC_DASHBOARD_VALIDATION.md`](file:///Users/hardik/Downloads/IBVAP/docs/reports/RBAC_DASHBOARD_VALIDATION.md)** — Role-by-role endpoint and WebSocket verification.
- **[`PERFORMANCE_RESULTS.md`](file:///Users/hardik/Downloads/IBVAP/docs/reports/PERFORMANCE_RESULTS.md)** — Benchmark results (185+ FPS, sub-6ms latency).

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

