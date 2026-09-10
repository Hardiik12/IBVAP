# IBVAP Release Notes — v1.0.0-sih (Frozen Release Candidate)

**Release Date:** 2026-09-10  
**Tag:** `v1.0.0-sih`  
**Problem Statement:** Smart India Hackathon 2026 (SIH26187)  
**Status:** 🟢 **Production/Demonstration Frozen**  

---

## 1. Verified Release Metrics

- **Automated Test Suite:** **187 / 187 Passed (100%)** in 10.51s
- **Backend Endpoints:** 12 route modules across REST and WebSockets
- **Database Schema:** 7 PostgreSQL relational tables with Alembic migrations (001, 002, 003)
- **Frontend Pages:** 16 static routes prerendered in Next.js 14 App Router
- **AI Processing Throughput:** 185+ FPS measured on 1280x720 video with live HUD overlay

---

## 2. Included Capabilities

1. **AI Computer Vision Pipeline:**
   - YOLOv8n object detection (persons, vehicles)
   - ByteTrack persistent tracking with Kalman state estimation
   - Ray-casting polygon geofencing on feet coordinates
   - Deterministic `OUTSIDE -> INSIDE` intrusion state machine
2. **FastAPI Operational Backend:**
   - REST API for cameras, zones, events, alerts, evidence, audit logs, and users
   - High-performance real-time WebSocket alert hub (`ws://.../ws/events`)
   - Server-authoritative SHA-256 evidence hashing and on-demand verification
3. **Multi-Factor Security & RBAC:**
   - Memory-hard Argon2id password hashing
   - Scoped JWT access tokens
   - RFC 6238 TOTP Multi-Factor Authentication
   - 1-to-1 SFace facial biometric login verification
   - 4-role RBAC (`ADMINISTRATOR`, `OPERATOR`, `ANALYST`, `AUDITOR`)
   - Append-only immutable audit trail
4. **Next.js 14 Command Center:**
   - Real-time WebSocket alarm feed with audible chimes
   - Interactive polygon boundary canvas drawing
   - Forensic evidence vault with 1-click tamper check
   - Fleet camera management and audit log inspection

---

## 3. Explicit Boundaries & Limitations

- **Camera Ingestion:** Native support for USB webcams, local video files, and synthetic streams. Real-world physical RTSP cameras are simulated via video streams.
- **AI Accuracy Evaluation:** Pre-trained COCO dataset weights are utilized. **"Formal precision/recall/mAP validation is not established."**
- **Evidence Storage:** Single-frame high-resolution JPEG snapshots with SHA-256 hashes.
