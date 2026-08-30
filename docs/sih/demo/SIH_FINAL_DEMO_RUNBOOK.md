# IBVAP — SIH Final Demonstration Master Runbook

**Target Duration:** Exact 5 Minutes  
**Demonstration Mode:** Localhost Live Interactive Pipeline (PostgreSQL + FastAPI + YOLOv8 + Next.js 14)  

---

## 1. Step-by-Step Chronological Demonstration Script

### [00:00 – 00:30] Session Authentication & Platform Health
- **Presenter Action:** Open `http://localhost:3000/login`, enter operator credentials (`admin` / demo password), click Log In.
- **Visual Display:** Immediate redirect to `/dashboard`. Point to top-right system status badge: `BACKEND ● CONNECTED | WS: CONNECTED | DB: CONNECTED`.
- **Narrative:** "We log in as an authorized operator. The tactical command center instantly hydrates, establishing a real-time authenticated WebSocket connection to our FastAPI backend."

### [00:30 – 01:15] Surveillance Viewport & Polygon Geofencing
- **Presenter Action:** Point out the live video viewport and the green normalized polygon perimeter.
- **Visual Display:** 2D polygon geofence rendered over the video stream.
- **Narrative:** "Here in our surveillance viewport, restricted border sectors are defined using arbitrary 2D polygon geometries. Normalized coordinates make this geofence independent of camera resolution or angle."

### [01:15 – 02:00] AI Detection & Persistent Tracking
- **Presenter Action:** Launch the AI runner in Terminal:
  ```bash
  PYTHONPATH=. backend/.venv/bin/python ai/pipeline/runner.py --source VIDEO_FILE --video-path data/videos/benchmark/benchmark_1280x720.avi
  ```
- **Visual Display:** Person bounding boxes appear with confidence scores and persistent ByteTrack Track ID `#1`.
- **Narrative:** "YOLOv8 detects perimeter targets while ByteTrack maintains persistent Kalman-filtered identities, surviving occlusions and momentary camera obstructions."

### [02:00 – 02:45] Intrusion Trigger & Real-Time Alert Card
- **Presenter Action:** The tracked target crosses into the restricted polygon zone.
- **Visual Display:**
  1. Target ground foot-point crosses polygon boundary.
  2. State machine transitions from `OUTSIDE` $\to$ `INSIDE`.
  3. `EventDispatcher` signs and POSTs event to `/api/v1/events`.
  4. Flashing `CRITICAL` alert card appears in the UI with an audible chime without page reload.
- **Narrative:** "The moment the intruder's foot-point breaches the boundary polygon, our state machine fires an intrusion event. Sub-10ms WebSocket delivery pushes the alert directly to our screen with an audible chime."

### [02:45 – 03:15] Operator Acknowledgment
- **Presenter Action:** Click **Acknowledge Alert**.
- **Visual Display:** Alert card status updates to `ACKNOWLEDGED` via `PATCH /api/v1/alerts/{id}`.
- **Narrative:** "The operator acknowledges the incident, logging their identity and UTC timestamp permanently to the audit ledger."

### [03:15 – 04:30] Forensic Evidence Vault & SHA-256 Verification
- **Presenter Action:** Navigate to `/evidence`, locate the incursion snapshot, and open the inspection modal.
- **Visual Display:** High-resolution capture frame, 64-character SHA-256 hash.
- **Action:** Click **Execute Authoritative SHA-256 Verification**.
- **Result:** Shows 🟢 `VERIFIED (EXACT MATCH)` — Disk binary matches database hash.
- **Narrative:** "Our evidence vault locks down evidentiary chain of custody. The backend recalculates the SHA-256 hash directly from physical disk bytes, mathematically proving the snapshot is genuine."

### [04:30 – 04:50] Live Tamper Detection Demonstration
- **Presenter Action:** Modify 1 byte of the evidence file on disk:
  ```bash
  echo "tamper" >> data/evidence/<capture_id>.jpg
  ```
- **Action:** Click **Execute Verification** again in the UI.
- **Result:** UI immediately flags 🔴 `MISMATCH (TAMPER DETECTED)` showing the conflicting SHA-256 hash digests.
- **Narrative:** "If an internal adversary modifies even a single pixel or byte of the evidence file on disk, our verification engine instantly detects the discrepancy and flags evidence tampering."

### [04:50 – 05:00] Evidence Restoration & Audit Trail
- **Presenter Action:** Restore the original image file and verify again $\to$ returns to 🟢 `VERIFIED`. Open `/audit-logs` to show the complete immutable audit ledger.
- **Narrative:** "Restoring the original bytes returns the state to verified. Every action is permanently recorded in our append-only audit trail. This is IBVAP—closed-loop, real-time, and cryptographically verified border intelligence."

---

## 2. Contingency & Failover Procedures

| Threat / Blocker | Immediate Reaction | Recovery Command |
|---|---|---|
| **Backend Crashes** | Switch to terminal and restart FastAPI | `uvicorn app.main:app --port 8000 --reload` |
| **WebSocket Closes** | Refresh browser window | Re-hydrates from PostgreSQL and re-authenticates socket |
| **Database Lock** | Reseed test database | `PYTHONPATH=. backend/.venv/bin/python backend/app/db/seed.py` |
| **Camera Hardware Failure** | Switch to pre-bundled benchmark video | Run with `--source VIDEO_FILE` on `benchmark_1280x720.avi` |
