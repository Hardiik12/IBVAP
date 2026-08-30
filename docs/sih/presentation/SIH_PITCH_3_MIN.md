# IBVAP — 3-Minute Rapid Technical Pitch

**Target Duration:** Exact 3 Minutes (180 Seconds)  
**Tone:** Confident, Technically Precise, Impact-Driven  

---

### [0:00 – 0:30] Problem Statement
"Good morning, respected judges. In border security, human operators monitoring hundreds of CCTV screens suffer visual fatigue within 20 minutes, leading to critical incursion blind spots. Traditional motion alarms create overwhelming false positive noise, while unverified CCTV video files lack mathematical proof of custody in forensic investigations."

### [0:30 – 1:00] The IBVAP Solution
"We built **IBVAP — the Intelligent Border Video Analytics Platform**. IBVAP bridges raw computer vision inference to an authenticated, tamper-evident command center. It autonomously detects boundary intrusions, filters false alarms through state-machine geofencing, and guarantees digital evidence integrity with server-authoritative SHA-256 cryptographic hashing."

### [1:00 – 1:40] Architecture & Pipeline
"Our architecture is built on five decoupled stages:
1. **AI Computer Vision:** High-throughput YOLOv8 detects targets; ByteTrack maintains persistent Kalman-filtered identities during occlusion; Shapely ray-casting evaluates foot-point containment inside arbitrary polygon boundaries.
2. **State Machine:** Intrusion alerts trigger strictly upon `OUTSIDE`-to-`INSIDE` transitions, completely eliminating alert spam while an intruder remains in the zone.
3. **Authenticated Event Dispatch:** Signed JWT HTTP POST commits the event to PostgreSQL in under 65 milliseconds."

### [1:40 – 2:10] Real-Time Streaming & Command Center
"Upon database commit, our `NotificationService` pushes live alerts over an authenticated WebSocket directly to our Next.js tactical command center in under 10 milliseconds. Operators receive instant visual banners, audio chimes, and bounding box telemetry with zero page reloads."

### [2:10 – 2:35] Cryptographic Forensics & Security
"When an incursion occurs, IBVAP captures the raw frame and computes its SHA-256 digest immediately. In our evidence vault, an operator can execute an on-demand integrity check. If even a single pixel or byte of the evidence file is altered on disk, our backend immediately flags it as 🔴 `TAMPER DETECTED`, providing indisputable proof of custody."

### [2:35 – 3:00] Empirical Results & Conclusion
"IBVAP is not a concept—it is a verified, frozen platform:
- **198.58 FPS** AI processing throughput on 720p video.
- **183 / 183 automated regression tests passing.**
- **Zero synthetic mock data in production paths.**

IBVAP delivers autonomous, real-time, and legally verifiable border intelligence. Thank you, and we welcome your questions."
