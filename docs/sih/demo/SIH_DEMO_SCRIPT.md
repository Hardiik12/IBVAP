# IBVAP — SIH Internal Round Demonstration Script

**Target Duration:** 5–7 Minutes  
**Demonstration Mode:** Localhost Live Integration (FastAPI + PostgreSQL + YOLOv8/ByteTrack + Next.js 14)  

---

## Presentation Timeline

### 0:00 – 0:30 | The Challenge & Value Proposition
- **Narrative:** "Securing expansive border sectors requires autonomous video analytics that detect incursions instantly, maintain verifiable chain-of-custody for forensic evidence, and enforce strict military-grade auditability without false alarms."
- **Key Takeaway:** IBVAP bridges raw computer vision inference to an authenticated, tamper-evident command center workflow.

### 0:30 – 1:30 | Live Surveillance & Polygon Geofencing
- **Action:** Open Dashboard (`http://localhost:3000`). Show `BACKEND ● CONNECTED | WS: CONNECTED | DB: CONNECTED` in header.
- **Narrative:** "Here in our Next.js tactical command center, live surveillance feeds are ingested. Restricted sectors are defined as normalized polygon coordinates rendered via Shapely Point-in-Polygon ray-casting."

### 1:30 – 2:30 | Intrusion Detection & Real-Time Alert Broadcast
- **Action:** Trigger person entry into the restricted zone (via test video or webcam).
- **Outcome:**
  1. YOLOv8 detects bounding box + ByteTrack assigns persistent Track ID.
  2. Intrusion State Machine detects `OUTSIDE` $\to$ `INSIDE` transition.
  3. `EventDispatcher` signs and POSTs event to `/api/v1/events` (HTTP 201).
  4. Backend creates `Event` and `Alert` in PostgreSQL.
  5. `NotificationService` broadcasts JSON over authenticated WebSocket.
  6. **UI updates immediately with audible tone and flashing banner without page reload.**

### 2:30 – 3:30 | Operator Acknowledgment & Chain of Custody
- **Action:** Operator clicks **Acknowledge Alert**.
- **Outcome:** `PATCH /api/v1/alerts/{id}` marks status as `ACKNOWLEDGED`, recording operator ID and timestamp in immutable audit log.

### 3:30 – 5:00 | Cryptographic Evidence Vault & Tamper Detection
- **Action:** Open `/evidence` and click **Inspect & Verify** on the captured frame.
- **Demo Step 1 (Untampered):** Click **Execute Authoritative SHA-256 Verification** $\to$ Shows 🟢 `VERIFIED (EXACT MATCH)`.
- **Demo Step 2 (Tamper Simulation):** Modify 1 byte of the test file on disk $\to$ Click Verify again $\to$ Shows 🔴 `TAMPER DETECTED (MISMATCH)` with exact hash difference.
- **Demo Step 3 (Restoration):** Restore original file $\to$ Click Verify again $\to$ Returns to 🟢 `VERIFIED`.

### 5:00 – 6:00 | Immutable Forensic Audit Trail & RBAC
- **Action:** Navigate to `/audit-logs`.
- **Narrative:** "Every authentication attempt, intrusion alert, operator acknowledgement, and SHA-256 integrity verification is recorded with actor ID and UTC timestamp in an immutable audit ledger."

### 6:00 – 7:00 | Performance, Security & Conclusion
- **Highlights:**
  - **198+ FPS** video processing throughput.
  - **100% Fail-Closed** model integrity check (`AI_MODEL_SHA256`).
  - **Argon2id + JWT + TOTP MFA** security baseline.
  - **183 / 183 automated regression tests passing.**
- **Closing Statement:** "IBVAP delivers a proven, reliable, and verifiable AI surveillance platform ready for operational deployment."
