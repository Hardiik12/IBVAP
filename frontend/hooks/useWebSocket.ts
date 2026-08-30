"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { WebSocketAlertMessage } from "../types/alert";
import { authService } from "../services/authService";

const getWebSocketUrl = (token: string | null): string => {
  let wsBase = process.env.NEXT_PUBLIC_WS_URL;
  if (!wsBase) {
    if (typeof window !== "undefined") {
      const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.hostname;
      const port = "8000"; // FastAPI backend port
      wsBase = `${proto}//${host}:${port}/api/v1/ws/events`;
    } else {
      wsBase = "ws://localhost:8000/api/v1/ws/events";
    }
  }

  if (token) {
    const separator = wsBase.includes("?") ? "&" : "?";
    return `${wsBase}${separator}token=${encodeURIComponent(token)}`;
  }
  return wsBase;
};

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketAlertMessage) => void;
  autoConnect?: boolean;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { onMessage, autoConnect = true } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<WebSocketAlertMessage | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const onMessageRef = useRef(onMessage);

  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const mapBackendPayloadToAlert = (data: any): WebSocketAlertMessage | null => {
    if (!data || typeof data !== "object") return null;

    if (data.type === "INTRUSION_ALERT" || data.type === "EVENT_CREATED" || data.type === "NEW_ALERT") {
      const evt = data.event || {};
      const alt = data.alert || {};
      const meta = evt.metadata || evt.event_metadata || {};

      return {
        type: "NEW_ALERT",
        alert_id: alt.id || `alt-${evt.id || Date.now()}`,
        event_id: evt.id || `evt-${Date.now()}`,
        event_type: evt.event_type || "INTRUSION",
        camera_id: evt.camera_id || "cam-01",
        camera_name: meta.camera_name || "Main Perimeter Camera 01",
        zone_name: meta.zone_name || "Perimeter Restricted Zone",
        track_id: evt.track_id || 1,
        class_name: meta.class_name || "person",
        confidence: meta.confidence || 0.88,
        severity: alt.severity || evt.severity || "CRITICAL",
        timestamp: data.timestamp || evt.timestamp || new Date().toISOString(),
        evidence_id: meta.evidence_id || evt.id || `evi-${Date.now()}`,
        bbox: evt.bounding_box || [0.1, 0.2, 0.3, 0.4],
      };
    }

    return null;
  };

  const triggerTestAlert = useCallback(() => {
    const testAlert: WebSocketAlertMessage = {
      type: "NEW_ALERT",
      alert_id: `alt-test-${Date.now()}`,
      event_id: `evt-test-${Date.now()}`,
      event_type: "INTRUSION",
      camera_id: "cam-01",
      camera_name: "Main Perimeter Camera 01",
      zone_name: "Perimeter Exclusion Zone A",
      track_id: Math.floor(Math.random() * 90) + 10,
      class_name: "person",
      confidence: 0.94,
      severity: "CRITICAL",
      timestamp: new Date().toISOString(),
      evidence_id: `evi-${Date.now()}`,
      bbox: [0.35, 0.25, 0.65, 0.85],
    };
    setLastMessage(testAlert);
    onMessageRef.current?.(testAlert);
  }, []);

  const connect = useCallback(() => {
    if (typeof window === "undefined") return;

    if (
      wsRef.current &&
      (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    const token = authService.getToken();
    if (!token) {
      setConnectionError("No active JWT session. Please log in.");
      setIsConnected(false);
      return;
    }

    try {
      const url = getWebSocketUrl(token);
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setConnectionError(null);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const raw = JSON.parse(event.data);
          const mapped = mapBackendPayloadToAlert(raw);
          if (mapped) {
            setLastMessage(mapped);
            onMessageRef.current?.(mapped);
          }
        } catch {
          // Non-JSON or ping message
        }
      };

      ws.onerror = () => {
        setConnectionError("WebSocket connection error");
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        wsRef.current = null;

        if (event.code === 1008) {
          setConnectionError("Policy Violation (Token Expired or Invalid). Re-authenticating...");
          authService.logout();
          return;
        }

        // Auto-reconnect with exponential backoff (max 10s)
        if (reconnectAttemptsRef.current < 10) {
          const delay = Math.min(10000, 1000 * Math.pow(1.5, reconnectAttemptsRef.current));
          reconnectAttemptsRef.current += 1;
          reconnectTimeoutRef.current = setTimeout(connect, delay);
        }
      };
    } catch (err: any) {
      setConnectionError(err?.message || "Failed to initialize WebSocket");
    }
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [autoConnect, connect]);

  return {
    isConnected,
    connectionError,
    lastMessage,
    triggerTestAlert,
    reconnect: connect,
  };
}
