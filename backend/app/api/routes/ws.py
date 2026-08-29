import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core import security
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


@router.websocket("/events")
async def websocket_events_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time security event and alert notifications.
    Requires valid JWT access token passed via query parameter (`?token=<jwt_access_token>`).
    """
    # 1. Check token presence
    if not token:
        logger.warning("WebSocket connection attempt missing token query parameter.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
        return

    # 2. Decode and validate JWT token
    payload = security.decode_access_token(token)
    if not payload or "sub" not in payload:
        logger.warning("WebSocket connection attempt with invalid/expired token.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token")
        return

    # 3. Retrieve user and verify active status
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        logger.warning(f"WebSocket connection attempt by inactive or missing user: {user_id}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User account is inactive or missing")
        return

    # 4. Enforce role-based access control
    if user.role not in ALLOWED_ROLES:
        logger.warning(f"WebSocket connection attempt by user {user.username} with unauthorized role: {user.role}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Insufficient permissions")
        return

    # 5. Connect and register client
    await websocket_manager.connect(websocket)

    try:
        while True:
            # Maintain active connection and listen for client ping/messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as err:
        logger.debug(f"WebSocket connection loop terminated: {err}")
        websocket_manager.disconnect(websocket)
