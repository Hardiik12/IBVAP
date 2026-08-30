# IBVAP — Live Demo Recovery & Troubleshooting Guide

This document provides quick-fix commands and diagnostic steps for all possible runtime issues during SIH presentations.

---

## 1. Fast Diagnostic Commands

```bash
# Check all container status and health
docker compose ps

# View aggregated logs across all 4 services
docker compose logs --tail=50 -f

# Inspect specific service logs
docker compose logs --tail=100 backend
docker compose logs --tail=100 ai
docker compose logs --tail=100 frontend
docker compose logs --tail=100 postgres
```

---

## 2. Common Failure Modes & Quick Fixes

### Issue 1: Port `8000` or `3000` Already In Use
* **Symptom**: `docker compose up` fails with `bind: address already in use`.
* **Fix**:
  ```bash
  # Identify process occupying port
  lsof -i :8000 -i :3000
  
  # Kill lingering local uvicorn or next.js processes
  kill -9 $(lsof -t -i :8000 -i :3000)
  
  # Restart Docker Compose
  docker compose up -d
  ```

---

### Issue 2: Backend Container Unhealthy
* **Symptom**: `ibvap-backend` status shows `(unhealthy)` or exits.
* **Fix**:
  ```bash
  # Inspect backend startup errors
  docker compose logs backend
  
  # Verify PostgreSQL is accepting connections
  docker compose exec postgres pg_isready -U ibvap -d ibvap
  
  # Re-run database migrations and seeding
  docker compose exec backend alembic upgrade head
  docker compose exec backend python -m app.db.seed
  
  # Restart backend
  docker compose restart backend
  ```

---

### Issue 3: AI Container Exited after Video Completion (Normal Behavior)
* **Symptom**: `docker compose ps` shows `ibvap-ai` Exited (0).
* **Explanation**: In `VIDEO_FILE` mode, the AI container processes all video frames and exits cleanly on EOF.
* **Restart AI Video Loop**:
  ```bash
  docker compose restart ai
  ```

---

### Issue 4: WebSocket Connection Disconnected in Browser
* **Symptom**: Live alerts not updating in dashboard UI.
* **Fix**:
  1. Confirm backend is reachable: `curl http://localhost:8000/health`.
  2. Refresh the browser page (`Cmd + Shift + R` or `Ctrl + F5`).
  3. Re-login as `operator_user` to refresh the cached JWT access token.

---

### Issue 5: Model Checksum Mismatch (`RuntimeError: Model integrity verification failed`)
* **Symptom**: `ibvap-ai` fails closed with checksum mismatch.
* **Fix**:
  ```bash
  # Option A: Blank out AI_MODEL_SHA256 for auto-verification in dev
  # Edit .env: AI_MODEL_SHA256=
  
  # Option B: Set exact valid checksum for yolov8n.pt
  # Edit .env: AI_MODEL_SHA256=f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36
  
  docker compose up -d ai
  ```

---

### Issue 6: Clean Reset (Complete Fresh State)
* **Symptom**: Corrupted test data or need a clean demo slate.
* **Fix**:
  ```bash
  # 1. Stop and remove containers and database volume
  docker compose down -v

  # 2. Re-launch and re-seed clean database
  docker compose up -d

  # 3. Verify healthy startup
  docker compose ps
  ```
