# IBVAP — SIH Demonstration Multi-Tier Backup & Contingency Plan

This document outlines the three-tier operational strategy ensuring flawless demonstration delivery regardless of hardware, power, or environment constraints.

---

## Tier Summary Matrix

| Level | Mode | Execution Environment | Use Case |
|---|---|---|---|
| **Level A** | **Live Interactive System** | Full stack running natively on localhost (PostgreSQL + FastAPI + YOLOv8 + Next.js 14) | Primary preferred presentation mode |
| **Level B** | **Controlled Offline Benchmark** | Deterministic video runner with seeded database state | Fallback if camera stream or live webcam input is unavailable |
| **Level C** | **Offline Visual Evidence Deck** | High-resolution pre-recorded demonstration video & architectural slide deck | Emergency fallback in case of catastrophic laptop hardware/power failure |

---

## 1. Level A: Primary Live Presentation Flow
- **Components:** Live webcam or RTSP feed, active FastAPI backend, live Next.js command center.
- **Workflow:** Real-time physical entry into camera frame $\to$ instant alert banner and chime $\to$ operator acknowledgment $\to$ live SHA-256 tamper demo.
- **Prerequisites:** PostgreSQL on port 5432, backend on port 8000, frontend on port 3000.

---

## 2. Level B: Controlled Video File Demonstration
- **Trigger:** Insufficient lighting, space constraints, or webcam hardware disconnection.
- **Execution Command:**
  ```bash
  PYTHONPATH=. backend/.venv/bin/python ai/pipeline/runner.py --source VIDEO_FILE --video-path data/videos/benchmark/benchmark_1280x720.avi
  ```
- **Outcome:** Processes 300 frames of deterministic video in ~1.5s (**198 FPS**), triggering intrusion event and live dashboard alert.

---

## 3. Level C: Emergency Visual Deck & Pre-Recorded Capture
- **Trigger:** Complete local service crash or presentation hardware failure.
- **Assets Available:**
  - Complete pre-recorded 1080p MP4 demonstration video of full end-to-end intrusion and tamper detection workflow.
  - Slide deck ([`SIH_PRESENTATION.md`](file:///Users/hardik/Downloads/IBVAP/SIH_PRESENTATION.md)) detailing architecture, empirical benchmarks (198.58 FPS), and security proofs.
