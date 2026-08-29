"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { WebSocketAlertMessage } from "../types/alert";
import { createMockAlert } from "../services/mockData";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/alerts";

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketAlertMessage) => void;
  autoConnect?: boolean;
  enableSimulatorFallback?: boolean;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { onMessage, autoConnect = true, enableSimulatorFallback = true } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isSimulated, setIsSimulated] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketAlertMessage | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const simIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const onMessageRef = useRef(onMessage);

  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const startSimulator = useCallback(() => {
    if (simIntervalRef.current) return;
    setIsSimulated(true);
    setIsConnected(true);

    // Push simulated test alerts periodically for demo practice
    simIntervalRef.current = setInterval(() => {
      const mockAlert = createMockAlert();
      setLastMessage(mockAlert);
      onMessageRef.current?.(mockAlert);
    }, 25000);
  }, []);

  const stopSimulator = useCallback(() => {
    if (simIntervalRef.current) {
      clearInterval(simIntervalRef.current);
      simIntervalRef.current = null;
    }
    setIsSimulated(false);
  }, []);

  const triggerTestAlert = useCallback(() => {
    const testAlert = createMockAlert();
    setLastMessage(testAlert);
    onMessageRef.current?.(testAlert);
  }, []);

  const connect = useCallback(() => {
    if (typeof window === "undefined") return;

    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setIsSimulated(false);
        stopSimulator();
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data: WebSocketAlertMessage = JSON.parse(event.data);
          if (data.type === "NEW_ALERT") {
            setLastMessage(data);
            onMessageRef.current?.(data);
          }
        } catch {
          // ignore non-json messages
        }
      };

      ws.onerror = () => {
        // Backend not running
      };

      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;

        // Auto Reconnect with backoff
        if (reconnectAttemptsRef.current < 5) {
          const timeout = Math.min(10000, 1000 * Math.pow(1.5, reconnectAttemptsRef.current));
          reconnectAttemptsRef.current += 1;
          reconnectTimeoutRef.current = setTimeout(connect, timeout);
        } else if (enableSimulatorFallback) {
          startSimulator();
        }
      };
    } catch {
      if (enableSimulatorFallback) {
        startSimulator();
      }
    }
  }, [enableSimulatorFallback, startSimulator, stopSimulator]);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      stopSimulator();
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [autoConnect, connect, stopSimulator]);

  return {
    isConnected,
    isSimulated,
    lastMessage,
    triggerTestAlert,
    reconnect: connect,
  };
}
