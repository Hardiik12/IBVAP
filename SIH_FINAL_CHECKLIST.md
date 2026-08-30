# IBVAP — Final SIH Presentation Readiness Checklist

Use this checklist immediately prior to, during, and following the live evaluation demonstration.

---

## 1. Pre-Presentation Setup (15 Minutes Prior)
- [ ] **Hardware:** Laptop connected to power; display resolution set to 1920x1080 or native.
- [ ] **PostgreSQL:** Active and accepting connections (`pg_isready -h localhost -p 5432`).
- [ ] **Backend Service:** Running in terminal (`uvicorn app.main:app --port 8000`). Health check passes (`GET /health` $\to$ 200).
- [ ] **Frontend Application:** Running in terminal (`npm run dev`). Loaded at `http://localhost:3000`.
- [ ] **Data State:** Database freshly seeded (`python backend/app/db/seed.py`).
- [ ] **AI Model Check:** YOLO weights present and validated against `AI_MODEL_SHA256`.
- [ ] **Test Video:** Benchmark video present at `data/videos/benchmark/benchmark_1280x720.avi`.
- [ ] **Browser Window:** Opened to Dashboard with DevTools Network tab prepared.
- [ ] **Status Indicators:** Header displays `BACKEND ● CONNECTED | WS: CONNECTED | DB: CONNECTED`.

---

## 2. Live Demonstration Flow
- [ ] **0:00 – 0:30:** Problem definition & border surveillance challenges.
- [ ] **0:30 – 1:30:** Command center architecture & polygon zone geofencing.
- [ ] **1:30 – 2:30:** Real-time intrusion trigger $\to$ instant alert banner and audio chime.
- [ ] **2:30 – 3:30:** Operator alert acknowledgment (`PATCH /api/v1/alerts/{id}`).
- [ ] **3:30 – 5:00:** Forensic evidence modal $\to$ 🟢 VERIFIED $\to$ 🔴 TAMPER DETECTED $\to$ 🟢 RESTORED.
- [ ] **5:00 – 6:00:** Immutable security audit trail (`/audit-logs`).
- [ ] **6:00 – 7:00:** Performance metrics (198+ FPS) and security summary.

---

## 3. Post-Demonstration Teardown
- [ ] Stop AI video runner (`Ctrl + C`).
- [ ] Preserve demonstration evidence captures and audit logs for judge review.
