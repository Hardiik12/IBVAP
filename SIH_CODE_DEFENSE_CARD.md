# IBVAP — "Show Me The Code" Defense Master Card

Use this master index during judge code review sessions to navigate directly to authoritative implementation files.

---

## 1. Computer Vision & AI Subsystem

| Architectural Claim | Key Implementation File | Specific Method / Symbol |
|---|---|---|
| **YOLOv8 Detection** | [`ai/detection/detector.py`](file:///Users/hardik/Downloads/IBVAP/ai/detection/detector.py) | `YOLODetector.detect(frame)` |
| **Model Integrity Check** | [`ai/detection/model_validator.py`](file:///Users/hardik/Downloads/IBVAP/ai/detection/model_validator.py) | `validate_model_checksum(model_path)` |
| **ByteTrack Tracking** | [`ai/tracking/tracker.py`](file:///Users/hardik/Downloads/IBVAP/ai/tracking/tracker.py) | `ByteTrackTracker.update(detections, frame)` |
| **Polygon Zone Engine** | [`ai/zones/polygon_zone.py`](file:///Users/hardik/Downloads/IBVAP/ai/zones/polygon_zone.py) | `PolygonZone.contains_point(point)` |
| **Foot-Point Extraction** | [`ai/zones/polygon_zone.py`](file:///Users/hardik/Downloads/IBVAP/ai/zones/polygon_zone.py) | `extract_foot_point(bbox)` |
| **Intrusion State Machine** | [`ai/events/intrusion_engine.py`](file:///Users/hardik/Downloads/IBVAP/ai/events/intrusion_engine.py) | `IntrusionEngine.process_tracks(tracks, frame)` |
| **AI Event Dispatcher** | [`ai/events/dispatcher.py`](file:///Users/hardik/Downloads/IBVAP/ai/events/dispatcher.py) | `EventDispatcher.dispatch_event(event_data)` |
| **Pipeline Runner** | [`ai/pipeline/runner.py`](file:///Users/hardik/Downloads/IBVAP/ai/pipeline/runner.py) | `PipelineRunner.run()` |

---

## 2. Backend Platform & API Subsystem

| Architectural Claim | Key Implementation File | Specific Method / Symbol |
|---|---|---|
| **FastAPI App Factory** | [`backend/app/main.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/main.py) | `create_application()` |
| **Event Persistence** | [`backend/app/services/event_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/event_service.py) | `EventService.create_event(db, payload)` |
| **Alert Management** | [`backend/app/services/alert_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/alert_service.py) | `AlertService.create_alert_for_event()` |
| **Post-Commit Broadcast** | [`backend/app/services/notification_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/notification_service.py) | `NotificationService.notify_event_created()` |
| **WebSocket Route & Auth**| [`backend/app/api/routes/ws.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/api/routes/ws.py) | `websocket_events(websocket, token)` |
| **In-Process WS Manager** | [`backend/app/services/websocket_manager.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/websocket_manager.py) | `WebSocketManager.broadcast_json(data)` |
| **Pydantic Schemas** | [`backend/app/schemas/`](file:///Users/hardik/Downloads/IBVAP/backend/app/schemas/) | `EventCreate`, `AlertResponse`, `EvidenceResponse` |

---

## 3. Security, Auth & Forensics Subsystem

| Architectural Claim | Key Implementation File | Specific Method / Symbol |
|---|---|---|
| **Argon2id Password Hash** | [`backend/app/core/security.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/core/security.py) | `get_password_hash(password)` |
| **JWT Token Minting** | [`backend/app/core/security.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/core/security.py) | `create_access_token(subject, role)` |
| **RBAC Authorization** | [`backend/app/api/deps.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/api/deps.py) | `require_role(allowed_roles)` |
| **TOTP MFA Validation** | [`backend/app/services/auth_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/auth_service.py) | `AuthService.verify_totp(user, code)` |
| **Evidence SHA-256 Check** | [`backend/app/services/evidence_integrity_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/evidence_integrity_service.py) | `EvidenceIntegrityService.verify_integrity()` |
| **Path Traversal Guard** | [`backend/app/services/evidence_integrity_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/evidence_integrity_service.py) | `resolve_path_safely(path)` |
| **Immutable Audit Trail** | [`backend/app/services/audit_service.py`](file:///Users/hardik/Downloads/IBVAP/backend/app/services/audit_service.py) | `AuditService.log_action(db, action, ...)` |
| **Security Audit Suite** | [`backend/tests/api/test_security_audit.py`](file:///Users/hardik/Downloads/IBVAP/backend/tests/api/test_security_audit.py) | Full threat model regression suite |

---

## 4. Frontend Command Center Subsystem

| Architectural Claim | Key Implementation File | Specific Method / Symbol |
|---|---|---|
| **Tactical Dashboard** | [`frontend/app/page.tsx`](file:///Users/hardik/Downloads/IBVAP/frontend/app/page.tsx) | Live monitoring HUD & Alert Feed |
| **Global WebSocket Stream**| [`frontend/context/AlertContext.tsx`](file:///Users/hardik/Downloads/IBVAP/frontend/context/AlertContext.tsx) | `AlertProvider` socket subscription & deduplication |
| **WebSocket Client Hook** | [`frontend/hooks/useWebSocket.ts`](file:///Users/hardik/Downloads/IBVAP/frontend/hooks/useWebSocket.ts) | `useWebSocket(url, token)` with reconnect |
| **Health Telemetry Badge** | [`frontend/components/layout/SystemStatusBadge.tsx`](file:///Users/hardik/Downloads/IBVAP/frontend/components/layout/SystemStatusBadge.tsx) | `BACKEND ● CONNECTED \| WS \| DB` |
| **Evidence Hash Verifier** | [`frontend/components/evidence/HashVerifier.tsx`](file:///Users/hardik/Downloads/IBVAP/frontend/components/evidence/HashVerifier.tsx) | Interactive SHA-256 verification widget |
| **Protected Route Guard** | [`frontend/components/layout/AppShell.tsx`](file:///Users/hardik/Downloads/IBVAP/frontend/components/layout/AppShell.tsx) | Client-side session guard & redirect |
