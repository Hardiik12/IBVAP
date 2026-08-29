import logging
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    In-memory connection manager for broadcasting real-time security event & alert notifications
    to active operational dashboard clients.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept an incoming WebSocket connection and register it.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Unregister a disconnected WebSocket client safely.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total active connections: {len(self.active_connections)}")

    async def broadcast(self, message_data: Dict[str, Any]) -> None:
        """
        Broadcast a JSON payload to all connected clients.
        Automatically cleans up closed or unresponsive client connections without interrupting others.
        """
        disconnected_clients: List[WebSocket] = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message_data)
            except (WebSocketDisconnect, RuntimeError, Exception) as exc:
                logger.warning(f"Error broadcasting to WebSocket client, scheduling removal: {exc}")
                disconnected_clients.append(connection)

        for dead_client in disconnected_clients:
            self.disconnect(dead_client)


# Singleton connection manager instance
websocket_manager = WebSocketManager()
