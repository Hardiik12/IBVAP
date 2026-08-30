# IBVAP — Live Demonstration Spoken Script & Action Guide

**Target Duration:** Exact 5 Minutes  
**Demonstration Mode:** Native Localhost Pipeline (PostgreSQL + FastAPI + YOLOv8 + Next.js 14)  

---

### [00:00 – 00:30] Session Initialization & Platform Health
- **ACTION:** Presenter opens browser to `http://localhost:3000/login`, enters `admin` / demo password, and clicks Log In.
- **SPOKEN:**
  > *"We begin by authenticating into our tactical command center. Upon login, the client acquires a cryptographically signed 15-minute JWT bearer token and establishes a persistent WebSocket connection to our FastAPI backend. Notice our top-right telemetry indicator: Backend is Connected, WebSocket is Live, and PostgreSQL is Connected. All data you see is live from our database with zero synthetic mock fallbacks."*

---

### [00:30 – 01:15] Surveillance Viewport & Polygon Geofencing
- **ACTION:** Presenter clicks on the Dashboard video viewport and highlights the green polygon perimeter boundary.
- **SPOKEN:**
  > *"In our primary surveillance viewport, border exclusion sectors are defined using arbitrary 2D polygon geometries. We store normalized coordinates between 0.0 and 1.0, making our geofence completely independent of physical camera resolution or aspect ratio. Ray-casting calculations run at the edge in real time."*

---

### [01:15 – 02:00] AI Detection & Persistent Tracking
- **ACTION:** Presenter switches to Terminal 4 and launches the AI runner:
  ```bash
  PYTHONPATH=. backend/.venv/bin/python ai/pipeline/runner.py --source VIDEO_FILE --video-path data/videos/benchmark/benchmark_1280x720.avi
  ```
- **SPOKEN:**
  > *"Now we start the AI pipeline. YOLOv8 detects targets with high confidence while ByteTrack assigns a persistent Kalman-filtered Track ID. Even if an intruder is momentarily occluded behind terrain or another person, ByteTrack maintains their identity across frames, operating at over 198 frames per second."*

---

### [02:00 – 02:45] Boundary Incursion & Real-Time Alert
- **ACTION:** Person foot-point crosses the polygon boundary line on screen. Flashing alert card appears with an audible chime.
- **SPOKEN:**
  > *"Watch the boundary line: the moment the target's ground foot-point crosses into the polygon, our state machine transitions from OUTSIDE to INSIDE. It generates exactly ONE event—preventing alert flooding while the target remains inside. The AI EventDispatcher signs the payload and POSTs to our backend. In under 10 milliseconds, our WebSocket pushes this critical alert card directly onto our screen with an audible chime, without any page reload."*

---

### [02:45 – 03:15] Operator Acknowledgment
- **ACTION:** Presenter clicks **Acknowledge Alert** on the active card.
- **SPOKEN:**
  > *"The operator takes operational ownership by clicking 'Acknowledge'. This dispatches a PATCH request to our backend, updating the alert status in PostgreSQL and recording the operator's user ID and UTC timestamp permanently in our immutable audit trail."*

---

### [03:15 – 04:30] Evidence Vault & SHA-256 Verification
- **ACTION:** Presenter navigates to `/evidence`, clicks on the newly captured incursion snapshot, and opens the inspection modal. Clicks **Execute Authoritative SHA-256 Verification**.
- **SPOKEN:**
  > *"We now open the Evidence Vault. At the exact millisecond of intrusion, the backend captured this high-resolution frame and computed its SHA-256 hash. When I click 'Verify Integrity', our backend re-reads the physical disk bytes and recalculates the hash. As you can see: 🟢 VERIFIED — Exact Match. This guarantees legal chain of custody."*

---

### [04:30 – 04:50] Live Tamper Detection Demonstration
- **ACTION:** Presenter runs a quick 1-line tamper injection command in terminal:
  ```bash
  echo "tamper" >> data/evidence/<capture_id>.jpg
  ```
  Presenter clicks **Execute Verification** again in the UI modal.
- **SPOKEN:**
  > *"Now, let's simulate an adversary altering the evidence file directly on the server filesystem. We append data to the file on disk and click Verify again. Instantly: 🔴 TAMPER DETECTED — MISMATCH. The system detects the altered hash and flags the discrepancy immediately."*

---

### [04:50 – 05:00] Restoration & Forensic Audit Trail
- **ACTION:** Presenter restores original file, re-verifies 🟢 `VERIFIED`, and navigates to `/audit-logs`.
- **SPOKEN:**
  > *"Restoring the original bytes returns the state to verified. Finally, we navigate to the Audit Log: every login, zone modification, alert acknowledgment, and evidence verification is permanently recorded with actor ID and timestamps. This is IBVAP: autonomous, real-time, and cryptographically verified border intelligence. Thank you."*
