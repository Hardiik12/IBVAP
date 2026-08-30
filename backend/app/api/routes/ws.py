import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.models.enums import UserRole
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_ROLES = {
    UserRole.OPERATOR,
    UserRole.ANALYST,
    UserRole.ADMINISTRATOR,
    UserRole.AUDITOR
}


async def handle_ws_connection(websocket: WebSocket, token: Optional[str], db: Session):
    if not token:
        logger.warning("WebSocket connection rejected: missing token.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
        return

    payload = security.decode_access_token(token)
    if not payload or "sub" not in payload:
        logger.warning("WebSocket connection rejected: invalid or expired token.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token")
        return


    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active or user.role not in ALLOWED_ROLES:
        logger.warning(f"WebSocket connection rejected: user {payload.get('sub')} inactive or unauthorized.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Unauthorized or inactive user")
        return

    # Connect and register client
    await websocket_manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as err:
        logger.debug(f"WebSocket connection loop terminated: {err}")
        websocket_manager.disconnect(websocket)


@router.websocket("/events")
async def websocket_events_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time security event and alert notifications (/api/v1/ws/events).
    """
    await handle_ws_connection(websocket, token, db)


@router.websocket("/alerts")
async def websocket_alerts_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for alerts matching API.md (/api/v1/ws/alerts).
    """
    await handle_ws_connection(websocket, token, db)
