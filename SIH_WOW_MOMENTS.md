# IBVAP — Top 3 Demonstration "WOW Moments"

These are the 3 pivotal demonstration moments that prove engineering depth and differentiate IBVAP from standard academic hackathon projects.

---

## 🌟 WOW MOMENT 1: Instant Incursion Alert with Zero Page Reload

### What to Demonstrate:
The tracked intruder breaches the restricted polygon line $\to$ the UI immediately triggers a flashing red alert card and native audio chime within sub-10 milliseconds without page refresh.

### What to Say:
> *"Watch how the state machine catches the single frame of boundary breach, commits to PostgreSQL, and pushes this alert over authenticated WebSockets in under 10 milliseconds. Zero page reload, zero polling overhead."*

### Why Judges Care:
Proves real-time distributed engineering rather than a static web interface displaying cached historical database rows.

### Technical Mechanism:
`IntrusionEngine` $\to$ `EventDispatcher` (HTTP POST + JWT) $\to$ `FastAPI` (SQLAlchemy ACID commit) $\to$ `NotificationService` $\to$ `WebSocketManager` push $\to$ Next.js `AlertProvider` deduplication and React state render.

### Backup Method if Demo Hangs:
Refresh browser window $\to$ Next.js immediately hydrates the persisted alert from PostgreSQL via REST.

---

## 🌟 WOW MOMENT 2: Live Forensic Evidence Tamper Detection

### What to Demonstrate:
Verify original snapshot (🟢 `VERIFIED`) $\to$ Inject 1 byte into the file on disk $\to$ Re-verify in UI $\to$ UI instantly turns red displaying 🔴 `TAMPER DETECTED (MISMATCH)`.

### What to Say:
> *"In legal and military forensics, video files without mathematical integrity can be contested. We just altered 1 byte on disk—the backend recalculates the SHA-256 binary digest and immediately flags evidence tampering."*

### Why Judges Care:
Provides concrete mathematical proof of evidence custody, which is universally absent in standard commercial and open-source CCTV systems.

### Technical Mechanism:
`EvidenceIntegrityService` reads raw disk binary stream via `hashlib.sha256()`, compares the computed 64-char hexadecimal digest to the immutable PostgreSQL database record, and logs the verification result to `audit_logs`.

### Backup Method if File Missing:
Click **Generate Server-Side Hash** on another existing snapshot to demonstrate dynamic hash generation.

---

## 🌟 WOW MOMENT 3: Fail-Closed AI Model Integrity & Security Posture

### What to Demonstrate:
Show the security test suite execution (`pytest backend/tests/api/test_security_audit.py`) running in 0.61s and passing 7/7 threat tests, including brute force lockout, path traversal blocking, and model checksum validation.

### What to Say:
> *"Security in IBVAP is mathematically verified. If someone replaces the YOLO weights file with a backdoored model, our engine computes its SHA-256 on startup and fails closed, aborting execution immediately."*

### Why Judges Care:
Shows mature defense-grade engineering and awareness of adversarial supply-chain vulnerabilities in AI models.

### Technical Mechanism:
`validate_model_checksum` computes SHA-256 of `yolov8n.pt` and raises `RuntimeError` if it does not match `AI_MODEL_SHA256`.

### Backup Method:
Reference Slide 7 of `SIH_FINAL_PRESENTATION.pptx` showing the full 15-vector threat model matrix.
