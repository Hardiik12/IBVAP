# IBVAP — Local Demonstration Startup Guide (No Docker Required)

This guide documents the exact startup commands to run the complete IBVAP surveillance stack locally on macOS / Linux.

---

## 1. Prerequisites
- Python 3.10+ (with virtual environment at `backend/.venv`)
- Node.js 18+ & npm
- PostgreSQL running locally on port 5432 (or SQLite local fallback if configured)

---

## 2. Step-by-Step Startup Sequence

### Step 1: Start PostgreSQL (if not already running)
```bash
# macOS Homebrew PostgreSQL
brew services start postgresql@16
# or confirm running:
pg_isready -h localhost -p 5432
```

### Step 2: Launch FastAPI Backend
Open **Terminal 1**:
```bash
cd /Users/hardik/Downloads/IBVAP/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Health Check:* Open `http://localhost:8000/health` or `http://localhost:8000/docs` in your browser.

---

### Step 3: Launch Next.js Tactical Frontend
Open **Terminal 2**:
```bash
cd /Users/hardik/Downloads/IBVAP/frontend
npm run dev
```
*Access UI:* Open `http://localhost:3000` in your browser and log in:
- **Username:** `admin` (or `operator`)
- **Password:** Configured demo operator password

---

### Step 4: Launch AI Video Pipeline
Open **Terminal 3**:
```bash
cd /Users/hardik/Downloads/IBVAP
PYTHONPATH=. backend/.venv/bin/python ai/pipeline/runner.py --source VIDEO_FILE --video-path data/videos/benchmark/benchmark_1280x720.avi
```
*(Or use live webcam by passing `--source WEBCAM`)*

---

## 3. Service Verification Checklist
- [x] Backend responds `{"status":"healthy","database":"connected"}` on `GET /health`
- [x] Frontend Header badge displays: `BACKEND ● CONNECTED | WS: CONNECTED | DB: CONNECTED`
- [x] Moving inside the restricted polygon triggers an instant alert card and audio cue without page reload.
