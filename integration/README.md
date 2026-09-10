# IBVAP System Integration & Orchestration Architecture

This directory documents the integration contracts and cross-tier orchestration of the IBVAP platform.

## Integration Architecture & Module Map

All active integration components are modularized across the production codebase:

| Integration Domain | Primary Implementation Location | Data Contracts / Protocols |
| :--- | :--- | :--- |
| **AI $\rightarrow$ Backend Event Dispatch** | [`ai/events/dispatcher.py`](file:///Users/hardik/Downloads/IBVAP/ai/events/dispatcher.py) | `EventPayload`, JWT Auth, Exponential Backoff |
| **Video $\rightarrow$ AI Pipeline Ingestion** | [`ai/camera/`](file:///Users/hardik/Downloads/IBVAP/ai/camera/), [`ai/pipeline/runner.py`](file:///Users/hardik/Downloads/IBVAP/ai/pipeline/runner.py) | `CameraSource`, OpenCV BGR frame pipeline |
| **Backend $\rightarrow$ Frontend REST Client** | [`frontend/services/`](file:///Users/hardik/Downloads/IBVAP/frontend/services/) | Axios REST Client, JWT Interceptors |
| **Real-Time Live Event Gateway** | [`backend/app/api/routes/ws.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/api/routes/ws.py), [`frontend/hooks/useAlerts.ts`](file:///Users/hardik/Downloads/IBVAP/frontend/hooks/useAlerts.ts) | WebSockets (`ws://...`), JSON Broadcast |
| **Docker Multi-Tier Orchestration** | Root [`docker-compose.yml`](file:///Users/hardik/Downloads/IBVAP/docker-compose.yml) | Multi-container stack (Postgres, Backend, AI, Frontend) |
| **E2E & Live Integration Tests** | [`backend/tests/integration/`](file:///Users/hardik/Downloads/IBVAP/backend/tests/integration/) | Full-pipeline dispatch & verification test battery |
| **Development & Seed Automation** | [`scripts/development/`](file:///Users/hardik/Downloads/IBVAP/scripts/development/), [`scripts/database/`](file:///Users/hardik/Downloads/IBVAP/scripts/database/) | Shell orchestration scripts |

For full details and audit logs, see [`docs/reports/INTEGRATION_DIRECTORY_AUDIT.md`](file:///Users/hardik/Downloads/IBVAP/docs/reports/INTEGRATION_DIRECTORY_AUDIT.md).
