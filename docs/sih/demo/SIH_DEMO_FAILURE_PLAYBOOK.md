# IBVAP — SIH Demo Failure Playbook & Troubleshooting Matrix

This playbook provides immediate tactical recovery commands for common issues during a live evaluation demonstration.

---

## Troubleshooting Matrix

| Symptom | Probable Cause | Diagnostic Command | Immediate Fix / Recovery |
|---|---|---|---|
| **Frontend displays `BACKEND ● OFFLINE`** | FastAPI backend is not running or crashed | `curl -s http://localhost:8000/health` | Restart backend in terminal: `uvicorn app.main:app --port 8000 --reload` |
| **Frontend displays `WS: OFFLINE`** | Token expired or WebSocket disconnected | Check DevTools Network $\to$ WS tab | Refresh browser page to re-authenticate and re-establish socket handshake |
| **Login fails with `ACCESS DENIED`** | Incorrect password or unseeded database | `python backend/app/db/seed.py` | Run database seed script to re-populate default role credentials |
| **AI fails with `RuntimeError: Model Checksum Mismatch`** | Incorrect `AI_MODEL_SHA256` environment variable | `echo $AI_MODEL_SHA256` | Verify `.env` matches official YOLO model SHA-256 digest |
| **No alerts generated upon video run** | Camera ID or zone geometry unassociated | Check terminal output of `ai/pipeline/runner.py` | Confirm camera ID is `cam-webcam-01` and restricted polygon is configured |
| **Port 8000 or 3000 in use** | Stale background process holding port | `lsof -i :8000` or `lsof -i :3000` | Terminate stale process: `kill -9 <PID>` and restart service |
| **Evidence verification returns `FILE_NOT_FOUND`** | Evidence snapshot directory missing | `ls -la data/evidence/` | Create directory: `mkdir -p data/evidence` |

---

## 1-Minute Panic Recovery Command
If the demonstration environment enters an unexpected state:

```bash
# 1. Kill stale background instances
pkill -f "uvicorn" || true
pkill -f "next-server" || true

# 2. Reseed database
PYTHONPATH=. backend/.venv/bin/python backend/app/db/seed.py

# 3. Launch Backend & Frontend
(cd backend && source .venv/bin/activate && uvicorn app.main:app --port 8000 --reload &)
(cd frontend && npm run dev &)
```
