from fastapi import APIRouter
from app.api.routes import cameras, zones, events, alerts, evidence, auth, users, audit_logs, ws, detection

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Logs"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["Cameras"])
api_router.include_router(zones.router, tags=["Zones"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(evidence.router, tags=["Evidence"])
api_router.include_router(detection.router, prefix="/detection", tags=["AI Detection"])
api_router.include_router(ws.router, prefix="/ws", tags=["WebSocket"])

