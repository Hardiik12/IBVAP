# IBVAP — Guidelines & Protocols for AI Coding Agents

All AI coding assistants (including Antigravity, Claude Code, OpenAI Codex, or human pair programmers) working on this repository MUST strictly follow the directives in this document.

---

## 1. Primary Rule & Source of Truth

> **[`docs/specs/PROJECT.md`](docs/specs/PROJECT.md) is the SINGLE MASTER SOURCE OF TRUTH.**
> Before modifying any architecture, schema, or module code, you MUST read `docs/specs/PROJECT.md` to confirm the scope of the SIH Internal-Round MVP.

For documentation index and structure specifications, consult:
- **Master Documentation Portal:** [`docs/README.md`](docs/README.md)
- **Documentation Tree Specification:** [`docs/FINAL_DOCUMENTATION_STRUCTURE.md`](docs/FINAL_DOCUMENTATION_STRUCTURE.md)

---

## 2. Golden Principles for AI Agents

1. **Frozen Release Candidate Rule**: The IBVAP application is a frozen SIH release candidate with 187/187 automated passing tests. Do NOT modify backend code, AI models, frontend components, database schemas, or API behavior unless specifically directed by the user.
2. **Phase-Gated Execution**: Implement ONLY the requested phase in [`docs/specs/TASKS.md`](docs/specs/TASKS.md). Do NOT automatically proceed to future phases without explicit instruction.
3. **Inspect Before Modifying**: Use code search and file viewing tools to inspect existing interfaces before writing new code.
4. **Preserve Working Interfaces**: Do not break existing data contracts (`NormalizedDetection`, `Track`, `EventPayload`, `CameraRead`).
5. **Never Guess or Fabricate Numbers**: Never fabricate benchmark figures (FPS, latency, precision, hash speed). Report only empirically measured results.
6. **No Scope Creep**: Do NOT add blockchain, Kubernetes, cloud microservices, ANPR, or mass facial recognition to the MVP unless explicitly commanded.
7. **No Silent Failure Suppression**: Do not mask errors with empty `try/except: pass` blocks or return dummy fallback data.
8. **Empirical Verification**: Run the automated test suite (`backend/.venv/bin/pytest -v`) after making changes to confirm 100% functionality.

---

## 3. Repository & Documentation Structure Rules

1. **Clean Root Directory**: The repository root must contain ONLY high-level entry files:
   - `README.md`, `SECURITY.md`, `AGENTS.md`, `LICENSE`
   - `.env`, `.env.example`, `.gitignore`, `docker-compose.yml`, `pytest.ini`
   - Top-level project directories: `ai/`, `backend/`, `frontend/`, `data/`, `docs/`, `scripts/`, `tools/`, `integration/`
2. **Canonical Documentation Locations**:
   - **Architecture:** `docs/architecture/{system,backend,frontend,ai}/`
   - **APIs & Contracts:** `docs/api/` (`REST_API.md`, `WEBSOCKET_API.md`, `API_REFERENCE.md`)
   - **AI & Vision:** `docs/ai/` (`AI_PIPELINE.md`, `OBJECT_DETECTION.md`, `TRACKING.md`, `GEOFENCING.md`, `INTRUSION_ENGINE.md`, `AI_VALIDATION.md`)
   - **Database:** `docs/database/` (`DATABASE_SCHEMA.md`, `DATABASE_DDL.sql`, `DATABASE_SCHEMA_AUDIT.md`)
   - **Security:** `docs/security/` (`SECURITY_ARCHITECTURE.md`, `THREAT_MODEL.md`, `EVIDENCE_INTEGRITY.md`, `SECURITY_TESTING.md`)
   - **Deployment:** `docs/deployment/` (`LOCAL_SETUP.md`, `DOCKER_SETUP.md`, `PRODUCTION_DEPLOYMENT.md`, `CONFIGURATION.md`)
   - **Testing:** `docs/testing/` (`TESTING_STRATEGY.md`, `TEST_RESULTS.md`, `PERFORMANCE.md`, `E2E_VALIDATION.md`)
   - **SIH Assets:** `docs/sih/` (`presentation/`, `demo/`, `defense/`, `judge-qa/`, `submission/`)
   - **Reports:** `docs/reports/` (`audits/`, `milestones/`, `security/`, `performance/`, `release/`)
   - **Specs & PRD:** `docs/specs/` (`PRD.md`, `REQUIREMENTS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `PROJECT.md`, `TASKS.md`)
3. **Preserve Historical Documentation**: Historical milestone reports (`docs/reports/milestones/`) and earlier test counts (171/171, 182/182, 183/183) must remain historically accurate and never rewritten.

---

## 4. Step-by-Step Task Protocol

When asked to work on a task:
1. **Identify Target Scope**: Map the user's request to the relevant documentation or codebase component in `docs/specs/TASKS.md`.
2. **Check Dependencies**: Verify that prerequisite systems and database tables are available.
3. **Execute Minimal Edit**: Write clean, modular, and typed code or documentation satisfying the explicit requirement.
4. **Verify Implementation**: Execute test suite (`backend/.venv/bin/pytest`) or linters.
5. **Report & Stop**: Summarize changes, share empirical test results, update relevant documentation, and STOP execution.
