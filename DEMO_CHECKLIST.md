# IBVAP — SIH Internal Round Demo Checklist

This checklist guarantees a 100% reproducible live demonstration of the **Intelligent Border Video Analytics Platform (IBVAP)**.

---

## 1. Pre-Demo Setup (10 Minutes Prior to Presentation)

- [ ] **Docker Engine Running**: Confirm Docker Desktop / Engine is active.
  ```bash
  docker info
  ```
- [ ] **Environment Configuration**: Verify `.env` file exists and is populated.
  ```bash
  cp .env.example .env
  ```
- [ ] **Model Weights Present**: Confirm YOLOv8 weights are available and validated.
  ```bash
  ls -lh yolov8n.pt models/yolov8n.pt 2>/dev/null || true
  ```
- [ ] **Demo Video Ingestion Asset**: Verify test video is in `./data/videos/test/sample_test.mp4`.
  ```bash
  ls -lh data/videos/test/sample_test.mp4
  ```
- [ ] **Port Availability**: Ensure host ports `8000` (Backend API), `3000` (Dashboard UI), and `5432` (PostgreSQL) are free.
  ```bash
  lsof -i :8000 -i :3000 || true
  ```
- [ ] **Start Clean Docker Compose Stack**:
  ```bash
  docker compose down
  docker compose up -d
  ```
- [ ] **Verify Container Health**:
  ```bash
  docker compose ps
  ```
  *Expected Output*: `ibvap-postgres` (healthy), `ibvap-backend` (healthy), `ibvap-frontend` (Up), `ibvap-ai` (Up).

---

## 2. During Live Demo (16-Step SIH Presentation Narrative)

- [ ] **Step 1 — Open Dashboard**: Navigate to `http://localhost:3000` in browser.
- [ ] **Step 2 — Operator Login**: Log in using `operator_user` / `OperatorSecret123!`.
- [ ] **Step 3 — Camera Feed Ingestion**: Point out active camera (`cam-webcam-01` / `Main Perimeter Camera 01`).
- [ ] **Step 4 — Spatial Restricted Zone**: Highlight defined polygon zone (`Perimeter Restricted Zone A`).
- [ ] **Step 5 — AI Detection & Tracking**: Demonstrate YOLOv8 human bounding box and ByteTrack persistent Track ID.
- [ ] **Step 6 — Outside Zone State**: Show target moving in free sector (`OUTSIDE` state).
- [ ] **Step 7 — Spatial Intrusion Boundary Transition**: Show target crossing polygon boundary with bottom-center reference point.
- [ ] **Step 8 — State Machine Event Trigger**: Explain transition `OUTSIDE -> INSIDE` generating deterministic event.
- [ ] **Step 9 — Duplicate Suppression**: Show that persistent track staying inside zone does NOT flood duplicate alerts (`INSIDE -> INSIDE`).
- [ ] **Step 10 — JWT Authenticated Ingestion**: Explain AI EventDispatcher HTTP dispatch to Backend (`POST /api/v1/events` with Bearer token).
- [ ] **Step 11 — Real-Time Alert Broadcast**: Observe instantaneous red notification banner on Dashboard via WebSocket (`INTRUSION_ALERT`).
- [ ] **Step 12 — Evidence Snapshot Capture**: Open alert evidence drawer showing captured snapshot.
- [ ] **Step 13 — Cryptographic Integrity Verification**: Click **"Verify Hash"** button $\rightarrow$ System displays green **`VERIFIED`** badge.
- [ ] **Step 14 — Tamper Detection Demonstration**: Trigger live file byte mutation $\rightarrow$ Re-verify $\rightarrow$ System displays red **`MISMATCH`** warning.
- [ ] **Step 15 — Cryptographic Restoration**: Restore original evidence bytes $\rightarrow$ System re-establishes green **`VERIFIED`** status.
- [ ] **Step 16 — Immutable Audit Log**: Open Audit Trail tab showing timestamped records (`LOGIN`, `EVENT_CREATED`, `ALERT_ACK`, `EVIDENCE_VERIFIED`).

---

## 3. Fallback & Backup Plan (Zero Downtime Guarantee)

If Docker environment fails during live presentation:

1. **Fallback 1 — Local Native Ingestion Mode (Hardware Webcam)**:
   ```bash
   # Terminal 1: Backend
   cd backend && source .venv/bin/activate
   uvicorn app.main:app --port 8000 --reload

   # Terminal 2: Live AI Webcam Pipeline
   cd .. && source backend/.venv/bin/activate
   python -m ai.pipeline.runner --source webcam --index 0
   ```
2. **Fallback 2 — Local Standalone Next.js Dashboard**:
   ```bash
   cd frontend
   npm run dev
   ```
3. **Fallback 3 — Automated Demonstration Verification Script**:
   ```bash
   backend/.venv/bin/python scratch_e2e_test.py
   ```
