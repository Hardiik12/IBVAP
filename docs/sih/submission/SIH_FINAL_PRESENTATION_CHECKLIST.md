# IBVAP — Final SIH Presentation & Demonstration Master Checklist

Keep this checklist active immediately before, during, and after the judging presentation.

---

## 1. Pre-Presentation Setup (15 Minutes Prior)
- [ ] **Power & Display:** Laptop plugged into AC power; display mirrored or extended at 1920x1080 resolution.
- [ ] **PostgreSQL Service:** Active on port 5432 (`pg_isready -h localhost -p 5432`).
- [ ] **FastAPI Backend:** Active on port 8000 (`uvicorn app.main:app`). Health endpoint verified (`http://localhost:8000/health`).
- [ ] **Next.js Frontend:** Active on port 3000 (`npm run dev`). Loaded in Chrome/Safari.
- [ ] **Database Seeding:** Fresh database state initialized (`python backend/app/db/seed.py`).
- [ ] **AI Model Check:** YOLO weights file `data/models/yolov8n.pt` present and verified.
- [ ] **Test Video Asset:** Benchmark video present at `data/videos/benchmark/benchmark_1280x720.avi`.
- [ ] **Evidence Directory:** `data/evidence/` directory present and writable.
- [ ] **Presentation Opened:** `SIH_FINAL_PRESENTATION.pptx` opened and ready on Slide 1.
- [ ] **Backup Assets:** Pre-recorded backup video and `SIH_PRESENTATION.md` accessible offline.
- [ ] **Telemetry Status:** Header badge displays `BACKEND ● CONNECTED | WS: CONNECTED | DB: CONNECTED`.

---

## 2. During Live Demonstration (5 Minutes)
- [ ] **[00:00 – 00:30]** Log in with operator credentials $\to$ show active telemetry indicators.
- [ ] **[00:30 – 01:15]** Explain primary viewport and normalized polygon geofence.
- [ ] **[01:15 – 02:00]** Start AI runner $\to$ showcase YOLOv8 detection and persistent ByteTrack ID.
- [ ] **[02:00 – 02:45]** Trigger polygon breach $\to$ showcase instant alert card and audible chime.
- [ ] **[02:45 – 03:15]** Operator acknowledges alert $\to$ status updates to `ACKNOWLEDGED` via PATCH.
- [ ] **[03:15 – 04:30]** Navigate to `/evidence` $\to$ click verify $\to$ showcase 🟢 `VERIFIED (EXACT MATCH)`.
- [ ] **[04:30 – 04:50]** Execute 1-byte tamper in terminal $\to$ click verify $\to$ showcase 🔴 `TAMPER DETECTED (MISMATCH)`.
- [ ] **[04:50 – 05:00]** Restore original file $\to$ re-verify 🟢 $\to$ open `/audit-logs` to show immutable ledger.

---

## 3. Post-Demonstration & Defense
- [ ] Stop AI runner cleanly (`Ctrl + C`).
- [ ] Present team members using [`SIH_TEAM_ROLE_CARD.md`](file:///Users/hardik/Downloads/IBVAP/SIH_TEAM_ROLE_CARD.md).
- [ ] Answer judge technical questions using [`SIH_MOCK_JUDGE_INTERROGATION.md`](file:///Users/hardik/Downloads/IBVAP/SIH_MOCK_JUDGE_INTERROGATION.md) and [`SIH_CODE_DEFENSE_CARD.md`](file:///Users/hardik/Downloads/IBVAP/SIH_CODE_DEFENSE_CARD.md).
- [ ] State limitations honestly using [`SIH_HONEST_LIMITATIONS.md`](file:///Users/hardik/Downloads/IBVAP/SIH_HONEST_LIMITATIONS.md).
- [ ] Explain scalability roadmap using [`SCALABILITY_ROADMAP.md`](file:///Users/hardik/Downloads/IBVAP/SCALABILITY_ROADMAP.md).
