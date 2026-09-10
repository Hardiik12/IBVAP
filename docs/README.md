# IBVAP Technical Documentation Portal

Welcome to the central technical documentation portal for the **Intelligent Border Video Analytics Platform (IBVAP)** — Smart India Hackathon 2026 (Problem Statement SIH26187).

---

## 📚 Documentation Index

### 1. 🏗️ Architecture Blueprints (`docs/architecture/`)
- **[System Architecture](architecture/system/SYSTEM_ARCHITECTURE.md)** — High-level 4-tier system design, dataflow pipelines, and network topology.
- **[Backend Architecture](architecture/backend/BACKEND_ARCHITECTURE.md)** — FastAPI services, dependency injection, and middleware.
- **[AI Pipeline Architecture](architecture/ai/AI_ARCHITECTURE.md)** — Computer vision pipeline, frame ingestion, and event lifecycle.
- **[Frontend Architecture](architecture/frontend/FRONTEND_ARCHITECTURE.md)** — Next.js 14 App Router, context providers, and component hierarchy.

---

### 2. 🔌 API Specifications (`docs/api/`)
- **[REST API Specification](api/REST_API.md)** — Complete OpenAPI endpoint specifications, request/response JSON schemas, and status codes.
- **[WebSocket API Specification](api/WEBSOCKET_API.md)** — Real-time event streaming protocol, authentication handshake, and payloads.
- **[API Quick Reference](api/API_REFERENCE.md)** — Summary table of routes, roles, and core data contracts.

---

### 3. 🧠 Computer Vision & AI (`docs/ai/`)
- **[AI Pipeline Overview](ai/AI_PIPELINE.md)** — End-to-end CV inference lifecycle and CLI execution options.
- **[Object Detection](ai/OBJECT_DETECTION.md)** — YOLOv8n detector wrapper, confidence thresholds, and COCO surveillance classes.
- **[Multi-Object Tracking](ai/TRACKING.md)** — ByteTrack spatial association, Kalman filtering, and foot coordinate extraction.
- **[Polygon Geofencing](ai/GEOFENCING.md)** — Ray-casting Point-in-Polygon (PIP) mathematical geofencing.
- **[Intrusion State Machine](ai/INTRUSION_ENGINE.md)** — `OUTSIDE -> INSIDE` transition state machine and alert suppression.
- **[AI Validation & Limitations](ai/AI_VALIDATION.md)** — Ground truth disclosure, throughput benchmarks, and accuracy roadmap.

---

### 4. 🗄️ Database & Schemas (`docs/database/`)
- **[Database Schema Specification](database/DATABASE_SCHEMA.md)** — Relational ERD, table definitions, foreign keys, and indexes.
- **[Database DDL Script](database/DATABASE_DDL.sql)** — Raw SQL schema definitions for all 7 PostgreSQL tables.
- **[Database Schema Audit](database/DATABASE_SCHEMA_AUDIT.md)** — Schema verification report against production PostgreSQL.

---

### 5. 🛡️ Security & Forensics (`docs/security/`)
- **[Security Architecture](security/SECURITY_ARCHITECTURE.md)** — Multi-layer defense-in-depth, Argon2id hashing, and JWT tokens.
- **[Threat Model Matrix (T-01 to T-15)](security/THREAT_MODEL.md)** — Comprehensive threat analysis and IBVAP mitigations.
- **[Evidence Integrity & Forensics](security/EVIDENCE_INTEGRITY.md)** — Server-authoritative SHA-256 evidence hashing and live tamper detection.
- **[Security Testing Guide](security/SECURITY_TESTING.md)** — Automated test battery for auth, RBAC, biometrics, and audit logging.

---

### 6. 🚀 Deployment & Operations (`docs/deployment/`)
- **[Local Development Setup](deployment/LOCAL_SETUP.md)** — Native macOS/Linux setup guide for local development.
- **[Docker Deployment Guide](deployment/DOCKER_SETUP.md)** — Multi-container Docker Compose setup instructions.
- **[Production Deployment](deployment/PRODUCTION_DEPLOYMENT.md)** — TLS termination, database hardening, and reverse proxy guidelines.
- **[Configuration Reference](deployment/CONFIGURATION.md)** — Master table of environment variables and runtime settings.

---

### 7. 🧪 Testing & Performance (`docs/testing/`)
- **[Testing Strategy](testing/TESTING_STRATEGY.md)** — Multi-tier test methodology across unit, API, integration, and E2E suites.
- **[Test Results Log](testing/TEST_RESULTS.md)** — 187/187 passing test verification results.
- **[Performance & Benchmark Results](testing/PERFORMANCE.md)** — 185+ FPS throughput and sub-6ms latency benchmarks.
- **[E2E Pipeline Validation](testing/E2E_VALIDATION.md)** — End-to-end integration and dispatch validation scenarios.

---

### 8. 🏆 SIH Presentation & Judging (`docs/sih/`)
- **[Presentation Deck & Pitches](sih/presentation/)** — `SIH_FINAL_PRESENTATION.pptx`, 10-slide deck, and 3-min / 60s / 30s pitches.
- **[Demo Runbooks & Startup](sih/demo/)** — 16-step live demonstration runbook, startup commands, and contingency playbooks.
- **[Defense & Limitations](sih/defense/)** — Code defense cards, honest limitations cards, and team role assignments.
- **[Judge Q&A & Interrogation](sih/judge-qa/)** — Technical Q&A, rapid-fire responses, and mock judge simulations.
- **[Submission Checklists](sih/submission/)** — Final presentation and submission readiness checklists.

---

### 9. 🔬 Research & Literature (`docs/research/`)
- **[YOLO Detection Research](research/YOLO/YOLO_RESEARCH.md)** — Deep-learning object detection comparative analysis.
- **[ByteTrack Research](research/ByteTrack/TRACKING_RESEARCH.md)** — Multi-object tracking algorithms for surveillance.
- **[Edge AI vs Cloud](research/Edge_AI/EDGE_VS_CLOUD.md)** — Edge inference architecture for remote border posts.
- **[Surveillance Problem Study](research/Surveillance/PROBLEM_STUDY.md)** — Operational border challenges and existing systems analysis.

---

### 10. 📊 Milestone & Audit Reports (`docs/reports/`)
- **[Audits](reports/audits/)** — Backup/restore analysis, integration reality check, mock data audit.
- **[Milestones](reports/milestones/)** — Milestone reports (M3.3 through M3.10).
- **[Security Audits](reports/security/)** — RBAC consistency, demo credential audits, user experience reviews.
- **[Performance Audits](reports/performance/)** — Benchmark logs, AI accuracy audits.
- **[Release Records](reports/release/)** — Final release verification, release notes, and documentation report.
