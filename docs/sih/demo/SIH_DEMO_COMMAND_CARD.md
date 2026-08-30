# IBVAP — SIH Quick-Reference Demo Command Card

Keep this single-page cheat sheet visible on screen during live presentation setup.

---

### Terminal 1: Database Check & Seeding
```bash
pg_isready -h localhost -p 5432
PYTHONPATH=. backend/.venv/bin/python backend/app/db/seed.py
```

### Terminal 2: FastAPI Backend
```bash
cd /Users/hardik/Downloads/IBVAP/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Verify:* `http://localhost:8000/health`

### Terminal 3: Next.js Command Center
```bash
cd /Users/hardik/Downloads/IBVAP/frontend
npm run dev
```
*Verify:* `http://localhost:3000` (Log in with `admin`)

### Terminal 4: AI Video Incursion Runner
```bash
cd /Users/hardik/Downloads/IBVAP
PYTHONPATH=. backend/.venv/bin/python ai/pipeline/runner.py --source VIDEO_FILE --video-path data/videos/benchmark/benchmark_1280x720.avi
```

---

### Emergency Panic Reset (1 Command)
```bash
pkill -f "uvicorn" || true; pkill -f "next-server" || true; PYTHONPATH=. backend/.venv/bin/python backend/app/db/seed.py
```
