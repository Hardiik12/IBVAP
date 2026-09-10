# IBVAP — SIH Team Role Defense Master Card

This guide equips every team presenter with their core domain mastery, important file references, architectural concepts, and expected judge defense questions.

---

## 1. AI & Computer Vision Lead
- **Core Mastery:** YOLOv8 bounding box inference, ByteTrack Kalman trajectory tracking, ground foot-point extraction $[x_{center}, y_{bottom}]$, and Shapely Point-in-Polygon (PIP) ray-casting geofencing.
- **Important Files:** [`ai/detection/detector.py`](file:///Users/hardik/Downloads/IBVAP/ai/detection/detector.py), [`ai/tracking/tracker.py`](file:///Users/hardik/Downloads/IBVAP/ai/tracking/tracker.py), [`ai/zones/polygon_zone.py`](file:///Users/hardik/Downloads/IBVAP/ai/zones/polygon_zone.py), [`ai/events/intrusion_engine.py`](file:///Users/hardik/Downloads/IBVAP/ai/events/intrusion_engine.py).
- **Core Concepts:** Jordan Curve Theorem, Kalman filter velocity prediction, 2-stage association matching.
- **3 Expected Judge Questions:**
  1. *Why ByteTrack over DeepSORT?* $\to$ "ByteTrack matches low-score boxes via Kalman filtering without heavy appearance models, achieving 198+ FPS."
  2. *How is false positive zone crossing prevented?* $\to$ "By evaluating the bottom-center foot-point contact coordinate rather than the bounding box centroid."
  3. *What happens during frame-to-frame occlusion?* $\to$ "ByteTrack predicts velocity state for up to 30 buffer frames before dropping track identity."
- **20-Second Pitch:** "I lead our computer vision pipeline: high-throughput YOLOv8 detection paired with ByteTrack trajectory tracking and Shapely polygon ray-casting, transforming pixels into verified spatial intrusions at 198 FPS."

---

## 2. Backend & API Platform Lead
- **Core Mastery:** FastAPI asynchronous REST architecture, Pydantic v2 validation schemas, dependency injection, and JWT middleware.
- **Important Files:** [`backend/app/main.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/main.py), [`backend/app/api/deps.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/api/deps.py), [`backend/app/services/event_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/event_service.py), [`backend/app/services/alert_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/alert_service.py).
- **Core Concepts:** Dependency injection (`Depends`), async non-blocking route execution, deterministic `event_identifier` idempotency.
- **3 Expected Judge Questions:**
  1. *Why FastAPI over Django/Flask?* $\to$ "Native Python async/await concurrency, automatic OpenAPI documentation, and sub-millisecond route dispatch latency."
  2. *How is event idempotency enforced?* $\to$ "By deriving a unique `event_identifier` from camera ID, track ID, and timestamp window, rejecting duplicates with HTTP 409."
  3. *How are database transactions isolated?* $\to$ "Async SQLAlchemy sessions wrap event and alert generation in single ACID transactions."
- **20-Second Pitch:** "I architected our FastAPI backend: non-blocking asynchronous endpoints, strict Pydantic schemas, and sub-65ms event-to-database persistence with idempotency protections."

---

## 3. Database & Forensics Lead
- **Core Mastery:** PostgreSQL relational schema design, foreign key constraints, UTC ISO-8601 normalization, server-authoritative SHA-256 evidence hashing, and append-only audit logging.
- **Important Files:** [`backend/app/models/`](file:///Users/hardik/Downloads/IBVAP/backend/app/models/), [`backend/app/services/evidence_integrity_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/evidence_integrity_service.py), [`backend/app/services/audit_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/audit_service.py).
- **Core Concepts:** Cryptographic preimage resistance, binary stream hashing, foreign key cascading, immutable audit logging.
- **3 Expected Judge Questions:**
  1. *How is evidence tampering detected?* $\to$ "Recalculates the disk file SHA-256 hash upon request; any altered byte flags 🔴 `MISMATCH`."
  2. *Can the stored hash be tampered with in the database?* $\to$ "The hash column is immutable post-creation, and any database modification causes a mismatch with physical disk bytes."
  3. *Why PostgreSQL instead of MongoDB?* $\to$ "Strict ACID guarantees for audit trails and relational constraints linking Events $\to$ Alerts $\to$ Evidence."
- **20-Second Pitch:** "I manage data persistence and forensics: relational PostgreSQL schema design, server-authoritative SHA-256 evidence verification, and immutable audit logs."

---

## 4. Security & Cryptography Lead
- **Core Mastery:** Argon2id password hashing, 15-minute scoped JWT Bearer tokens, TOTP RFC-6238 MFA, 4-tier RBAC, fail-closed model integrity (`AI_MODEL_SHA256`), and path traversal protection (`resolve_path_safely`).
- **Important Files:** [`backend/app/core/security.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/core/security.py), [`backend/app/services/auth_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/auth_service.py), [`ai/detection/model_validator.py`](file:///Users/hardik/Downloads/IBVAP/ai/detection/model_validator.py), [`backend/tests/api/test_security_audit.py`](file:///Users/hardik/Downloads/IBVAP/backend/tests/api/test_security_audit.py).
- **Core Concepts:** Defense-in-depth, Fail-Closed design, Argon2id memory-hard key derivation, Least Privilege.
- **3 Expected Judge Questions:**
  1. *What happens if an adversary alters the AI model weights?* $\to$ "Fail-closed check compares SHA-256 on startup; a mismatch raises `RuntimeError` and terminates."
  2. *How are credentials protected against brute-force?* $\to$ "Argon2id key derivation combined with sliding-window IP rate limiting."
  3. *How is path traversal prevented on evidence requests?* $\to$ "`resolve_path_safely` canonicalizes paths under `EVIDENCE_ROOT`, blocking `../` directory escapes with HTTP 400."
- **20-Second Pitch:** "I implemented our defense-in-depth security: Argon2id, JWT, 4-tier RBAC, fail-closed model integrity, and 15 threat-modeled protections verified by 7 automated security tests."

---

## 5. Frontend & UI/UX Lead
- **Core Mastery:** Next.js 14 App Router, TypeScript, React Context state management, Tailwind dark tactical styling, Web Audio API sound synthesis, and real-time WebSocket lifecycle.
- **Important Files:** [`frontend/app/page.tsx`](file:///Users/hardik/Downloads/IBVAP/frontend/app/page.tsx), [`frontend/context/AlertContext.tsx`](file:///Users/hardik/Downloads/IBVAP/frontend/context/AlertContext.tsx), [`frontend/hooks/useWebSocket.ts`](file:///Users/hardik/Downloads/IBVAP/frontend/hooks/useWebSocket.ts), [`frontend/components/evidence/HashVerifier.tsx`](file:///Users/hardik/Downloads/IBVAP/frontend/components/evidence/HashVerifier.tsx).
- **Core Concepts:** Global single-socket management, exponential backoff reconnection, zero synthetic mock fallbacks.
- **3 Expected Judge Questions:**
  1. *Why Next.js 14?* $\to$ "Type-safe routing, server-side static page generation, and modular React component architecture."
  2. *How is WebSocket alert flooding prevented in the UI?* $\to$ "Centralized deduplication in `AlertProvider` filtering on `alert_id` and `event_id`."
  3. *Are any screens using mock data?* $\to$ "Zero. All routes consume live `/api/v1` backend endpoints with clean offline notices on network drop."
- **20-Second Pitch:** "I built our Next.js tactical command center: real-time WebSocket alert ingestion, dark tactical HUD styling, Web Audio warning chimes, and interactive SHA-256 evidence inspection."

---

## 6. Integration & Quality Assurance Lead
- **Core Mastery:** End-to-end pipeline integration, automated regression testing (183 tests), performance benchmarking (198.58 FPS), failure simulation, and local startup orchestration.
- **Important Files:** [`LOCAL_DEMO_STARTUP.md`](file:///Users/hardik/Downloads/IBVAP/LOCAL_DEMO_STARTUP.md), [`SIH_FINAL_COMMAND_CARD.md`](file:///Users/hardik/Downloads/IBVAP/SIH_FINAL_COMMAND_CARD.md), [`backend/tests/`](file:///Users/hardik/Downloads/IBVAP/backend/tests/), [`ai/tests/`](file:///Users/hardik/Downloads/IBVAP/ai/tests/).
- **Core Concepts:** Deterministic pipeline repeatability, graceful degradation, benchmark validation.
- **3 Expected Judge Questions:**
  1. *How do you know the system won't crash during the demo?* $\to$ "We run 183 automated regression tests with 100% pass rate and rehearsed the exact live flow in 5m 25s."
  2. *Why run locally without Docker?* $\to$ "To demonstrate raw native Python/Node.js performance without virtualization bottlenecks."
  3. *How fast does the system recover from crashes?* $\to$ "Backend restarts and UI re-hydrates in under 3 seconds with zero data loss."
- **20-Second Pitch:** "I ensure system stability: 183 automated regression tests passing, 198+ FPS benchmark validation, zero-Docker native execution, and rehearsed 5-minute live demo flows."

---

## 7. Product & Presentation Lead
- **Core Mastery:** Strategic narrative, problem-solution alignment, timekeeping (7–10m presentation, 5m demo), judge defense coordination, and impact articulation.
- **Important Files:** [`SIH_PRESENTATION.md`](../presentation/SIH_PRESENTATION.md), [`SIH_FINAL_PRESENTATION.pptx`](../presentation/SIH_FINAL_PRESENTATION.pptx), [`SIH_FINAL_DEMO_RUNBOOK.md`](../demo/SIH_FINAL_DEMO_RUNBOOK.md), [`SIH_JUDGE_QA.md`](../judge-qa/SIH_JUDGE_QA.md).
- **Core Concepts:** Clear problem framing, crisp technical storytelling, seamless transitions between slides and live code.
- **20-Second Pitch:** "I orchestrate our presentation: framing the critical national security problem, showcasing our 18-slide tactical deck, and demonstrating our working platform to prove mission readiness."
