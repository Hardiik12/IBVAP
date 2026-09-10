# IBVAP — Final Documentation Structure Specification

**Document Version:** 1.0.0 — Final  
**Date:** 2026-09-10  
**Status:** 🟢 Complete & Verified  

---

## 1. Final Documentation Hierarchy

```
docs/
│
├── README.md                             # Master documentation portal
├── FINAL_DOCUMENTATION_STRUCTURE.md      # Documentation structure specification
│
├── architecture/                         # Subsystem & System Blueprints
│   ├── system/SYSTEM_ARCHITECTURE.md     # 4-tier high-level system architecture
│   ├── backend/BACKEND_ARCHITECTURE.md   # FastAPI backend & database layer
│   ├── frontend/FRONTEND_ARCHITECTURE.md # Next.js 14 command dashboard
│   └── ai/AI_ARCHITECTURE.md             # Computer vision pipeline & event lifecycle
│
├── api/                                  # API Data Contracts & Endpoint Specs
│   ├── REST_API.md                       # Complete OpenAPI REST endpoint specification
│   ├── WEBSOCKET_API.md                  # Real-time WebSocket streaming specification
│   └── API_REFERENCE.md                  # Summary table & data schemas
│
├── ai/                                   # Computer Vision & Machine Learning
│   ├── AI_PIPELINE.md                    # Pipeline runner & frame orchestration
│   ├── OBJECT_DETECTION.md               # YOLOv8n detector & class filtering
│   ├── TRACKING.md                       # ByteTrack multi-object tracking
│   ├── GEOFENCING.md                     # Ray-casting PIP polygon geofence engine
│   ├── INTRUSION_ENGINE.md               # Intrusion state machine & suppression
│   └── AI_VALIDATION.md                  # Ground truth disclosure & accuracy limits
│
├── database/                             # Database Schemas & Relational Design
│   ├── DATABASE_SCHEMA.md                # Table definitions, foreign keys & indexes
│   ├── DATABASE_DDL.sql                  # Raw PostgreSQL SQL schema creation script
│   └── DATABASE_SCHEMA_AUDIT.md          # Live database schema verification report
│
├── security/                             # Security, Forensics & Cryptography
│   ├── SECURITY_ARCHITECTURE.md          # Defense-in-depth, Argon2id, JWT, MFA
│   ├── THREAT_MODEL.md                   # Threat matrix (T-01 to T-15) & mitigations
│   ├── EVIDENCE_INTEGRITY.md             # SHA-256 evidence hashing & tamper test
│   └── SECURITY_TESTING.md               # Security test battery and execution
│
├── deployment/                           # Deployment & Operations
│   ├── LOCAL_SETUP.md                    # Native local development setup guide
│   ├── DOCKER_SETUP.md                   # Docker Compose containerized deployment
│   ├── PRODUCTION_DEPLOYMENT.md          # Production hardening & TLS guidelines
│   └── CONFIGURATION.md                  # Master environment variables reference
│
├── testing/                              # Testing Methodologies & Logs
│   ├── TESTING_STRATEGY.md               # Multi-tier testing methodology
│   ├── TEST_RESULTS.md                   # 187/187 passing test execution log
│   ├── PERFORMANCE.md                    # 185+ FPS throughput benchmark report
│   └── E2E_VALIDATION.md                 # Full pipeline end-to-end integration
│
├── research/                             # Literature & Reference Papers
│   ├── YOLO/YOLO_RESEARCH.md             # YOLO object detection research
│   ├── ByteTrack/TRACKING_RESEARCH.md    # Multi-object tracking research
│   ├── Edge_AI/EDGE_VS_CLOUD.md          # Edge vs cloud trade-off analysis
│   ├── Surveillance/PROBLEM_STUDY.md     # Border surveillance operational study
│   └── References/RESEARCH_INDEX.md      # Literature review index
│
├── reports/                              # Milestone, Audit & Release Reports
│   ├── audits/                           # Technical debt & architecture audits
│   ├── milestones/                       # Historical milestone reports (M3.3–M3.10)
│   ├── security/                         # RBAC consistency & credential audits
│   ├── performance/                      # Benchmark logs & accuracy audits
│   └── release/                          # Final release verification & release notes
│
├── sih/                                  # Smart India Hackathon Presentation & Demo
│   ├── presentation/                     # Slide deck PPTX, pitches, spoken script
│   ├── demo/                             # Live demo runbooks, checklists, playbooks
│   ├── defense/                          # Judge defense cards & role assignments
│   ├── judge-qa/                         # Technical Q&A & rapid-fire answers
│   └── submission/                       # SIH presentation readiness checklists
│
└── specs/                                # Master Specifications & Requirements
    ├── PRD.md                            # Product requirements document
    ├── REQUIREMENTS.md                   # System hardware & software requirements
    ├── ARCHITECTURE.md                   # High-level technical architecture
    ├── DECISIONS.md                      # Architecture Decision Records (ADR 001-014)
    ├── PROJECT.md                        # Master project vision & SIH scope
    ├── TASKS.md                          # Phased roadmap & execution matrix
    └── TECH_STACK.md                     # Technology selection rationale
```

---

## 2. Directory Locations for Key Domains

| Category | Primary Directory | Description |
| :--- | :--- | :--- |
| **Master Index** | `docs/README.md` | Central portal linking to all categories |
| **System Architecture** | `docs/architecture/` | Blueprints for System, Backend, Frontend, and AI |
| **APIs & Contracts** | `docs/api/` | REST, WebSocket, and data contracts |
| **Computer Vision / AI**| `docs/ai/` | YOLO, ByteTrack, Geofencing, State Machine |
| **Database & Schemas** | `docs/database/` | DDL script, table schemas, and schema audits |
| **Security & Forensics**| `docs/security/` | Threat models, Argon2id, SHA-256 evidence hashing |
| **Deployment Guides** | `docs/deployment/` | Local setup, Docker Compose, Production, Config |
| **Testing & Results** | `docs/testing/` | Test strategy, 187/187 results, 185+ FPS benchmarks |
| **SIH 2026 Assets** | `docs/sih/` | PPTX decks, pitches, demo runbooks, judge Q&A |
| **Reports & Milestones**| `docs/reports/` | Audits, historical milestones (M3.3–M3.10), release |
| **Core Specs & PRD** | `docs/specs/` | PRD, Requirements, Tasks, Decisions (ADRs) |
