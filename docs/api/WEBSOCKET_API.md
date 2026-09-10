# IBVAP Real-Time WebSocket API Specification

**WebSocket Gateway:** `ws://localhost:8000/api/v1/ws/events?token=<JWT_ACCESS_TOKEN>`  
**Protocol:** Standard RFC 6455 WebSockets  
**Direction:** Server-to-Client Broadcast (Push Notifications)  

---

## 1. Connection & Authentication

Clients establish a WebSocket connection by supplying a valid JWT bearer token in the `token` query parameter:

```javascript
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/events?token=${token}`);
```

### Authorization Handshake:
1. The server intercepts the HTTP connection upgrade request.
2. The JWT token is validated against `JWT_SECRET_KEY` and expiration.
3. The user identity and active status are verified in PostgreSQL.
4. If authentication fails, the connection is closed with status code `1008` (`WS_1008_POLICY_VIOLATION`).
5. Upon successful handshake, the connection is registered with `WebSocketManager`.

---

## 2. Real-Time Intrusion Alert Payload

When an `INTRUSION` event is created and persisted, the server broadcasts an `INTRUSION_ALERT` JSON payload to all connected clients:

```json
{
  "type": "INTRUSION_ALERT",
  "timestamp": "2026-08-29T20:00:00Z",
  "event": {
    "id": "e4a77a98-8c10-410d-852a-995b28d7a123",
    "event_identifier": "EV-WS-INTRUSION-01",
    "event_type": "INTRUSION",
    "camera_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "zone_id": "c1f77b99-1c0b-4ef8-bb6d-8bb9bd380a22",
    "track_id": 99,
    "timestamp": "2026-08-29T20:00:00Z",
    "severity": "HIGH",
    "status": "NEW",
    "bounding_box": {"x1": 420, "y1": 210, "x2": 510, "y2": 480},
    "position": {"x": 465, "y": 480},
    "metadata": {"confidence": 0.94, "class_name": "person"},
    "created_at": "2026-08-29T20:00:00.123456Z",
    "alert_id": "b1ff8b09-9d21-421e-963b-006c39e8b456"
  },
  "alert": {
    "id": "b1ff8b09-9d21-421e-963b-006c39e8b456",
    "event_id": "e4a77a98-8c10-410d-852a-995b28d7a123",
    "severity": "HIGH",
    "status": "ACTIVE",
    "message": "Intrusion detected on camera a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "created_at": "2026-08-29T20:00:00.123456Z",
    "acknowledged_at": null,
    "acknowledged_by": null
  }
}
```

---

## 3. Client Resilience & Reconnection Protocol

1. **Automatic Reconnection:** `frontend/hooks/useAlerts.ts` implements exponential backoff reconnection if the socket drops.
2. **REST Synchronization:** On reconnect, the client executes `GET /api/v1/alerts?status=ACTIVE` to catch any alerts emitted while offline.
3. **Graceful Disconnect:** When the user logs out or closes the dashboard, the WebSocket connection cleanly detaches without server exception.
