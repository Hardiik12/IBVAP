# IBVAP Docker Compose Deployment Guide

**Container Architecture:** Multi-service orchestration managing 4 discrete containers:
1. `ibvap-postgres` (PostgreSQL 15 Alpine with persistent named volume)
2. `ibvap-backend` (FastAPI Python 3.12 Backend API)
3. `ibvap-ai` (Headless YOLOv8n + ByteTrack AI Pipeline)
4. `ibvap-frontend` (Next.js 14 Node.js 20 Multi-Stage Production Container)

---

## 1. Quickstart Commands

```bash
# 1. Configure Environment
cp .env.example .env

# 2. Build and Launch Stack in Background
docker compose up --build -d

# 3. View Live Aggregated Logs
docker compose logs -f

# 4. Check Service Health
docker compose ps

# 5. Stop All Containers (Preserves DB Data)
docker compose down

# 6. Reset Database Cleanly
docker compose down -v
```

---

## 2. Port Bindings & Endpoints

| Container | Internal Port | Host Port | Endpoint / Purpose |
| :--- | :---: | :---: | :--- |
| **Frontend** | `3000` | `3000` | `http://localhost:3000` (Command Dashboard) |
| **Backend** | `8000` | `8000` | `http://localhost:8000/docs` (REST & WebSocket) |
| **Postgres** | `5432` | `5432` | Internal bridge network (`ibvap-network`) |
