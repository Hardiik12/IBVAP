# IBVAP — Master Demonstration Command Card

**Platform:** macOS Darwin / Linux Localhost  
**Hardware:** Native Python 3.13 + Node.js v20 (No Docker Required)  

---

## 1. Startup Commands (4 Terminals)

### Terminal 1: Database Check & Reset
```bash
# Verify PostgreSQL is active
pg_isready -h localhost -p 5432
# Seed demo roles, cameras, and zones
PYTHONPATH=. backend/.venv/bin/python backend/app/db/seed.py
```

### Terminal 2: FastAPI Backend Platform
```bash
cd /Users/hardik/Downloads/IBVAP/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Health Check:* `http://localhost:8000/health` $\to$ `{"status":"healthy","database":"connected"}`

### Terminal 3: Next.js Tactical Command Center
```bash
cd /Users/hardik/Downloads/IBVAP/frontend
npm run dev
```
*Browser URL:* `http://localhost:3000` (Log in with `admin` / demo credentials)

### Terminal 4: AI Computer Vision Incursion Runner
```bash
cd /Users/hardik/Downloads/IBVAP
# Video File Benchmark Run:
PYTHONPATH=. backend/.venv/bin/python ai/pipeline/runner.py --source VIDEO_FILE --video-path data/videos/benchmark/benchmark_1280x720.avi
# Or Live Webcam Run:
PYTHONPATH=. backend/.venv/bin/python ai/pipeline/runner.py --source WEBCAM
```

---

## 2. Automated Test & Regression Execution
```bash
# Run full 183-test backend & AI regression baseline
backend/.venv/bin/pytest backend/tests/ ai/tests/ -q
# Run frontend type and build validation
cd frontend && npm run lint && npx tsc --noEmit && npm run build
```

---

## 3. 1-Line Emergency Panic Reset
```bash
pkill -f "uvicorn" || true; pkill -f "next-server" || true; PYTHONPATH=. backend/.venv/bin/python backend/app/db/seed.py
```
