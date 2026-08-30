"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { WebSocketAlertMessage, AlertState } from "../types/alert";
import { alertService } from "../services/alertService";
import { eventService } from "../services/eventService";
import { useWebSocket } from "../hooks/useWebSocket";

interface AlertContextType {
  alerts: AlertState[];
  unreadCount: number;
  latestAlert: WebSocketAlertMessage | null;
  activeEvidenceModalId: string | null;
  isAudioMuted: boolean;
  isWsConnected: boolean;
  wsError: string | null;
  addAlert: (alert: WebSocketAlertMessage) => void;
  markAsRead: (alertId: string) => void;
  markAllAsRead: () => void;
  clearAlerts: () => void;
  openEvidenceModal: (evidenceId: string) => void;
  closeEvidenceModal: () => void;
  toggleAudioMute: () => void;
  refreshAlerts: () => Promise<void>;
  triggerTestAlert: () => void;
}

const AlertContext = createContext<AlertContextType | undefined>(undefined);

export function AlertProvider({ children }: { children: React.ReactNode }) {
  const [alerts, setAlerts] = useState<AlertState[]>([]);
  const [latestAlert, setLatestAlert] = useState<WebSocketAlertMessage | null>(null);
  const [activeEvidenceModalId, setActiveEvidenceModalId] = useState<string | null>(null);
  const [isAudioMuted, setIsAudioMuted] = useState(false);

  const refreshAlerts = useCallback(async () => {
    try {
      const realAlerts = await alertService.getAlerts({ limit: 50 });
      if (realAlerts && realAlerts.length > 0) {
        setAlerts(realAlerts);
        return;
      }

      const events = await eventService.getEvents({ limit: 30 });
      const mappedAlerts: AlertState[] = events.map((e) => ({
        type: "NEW_ALERT",
        alert_id: `alt-${e.event_id}`,
        event_id: e.event_id,
        event_type: e.event_type,
        camera_id: e.camera_id,
        camera_name: "Main Perimeter Camera 01",
        zone_name: e.zone_name || "Perimeter Restricted Zone",
        track_id: e.track_id,
        class_name: e.class_name,
        confidence: e.confidence,
        severity: e.severity,
        timestamp: e.timestamp,
        evidence_id: e.evidence_id || e.event_id,
        bbox: e.bbox,
        isRead: !!e.acknowledged,
      }));
      setAlerts(mappedAlerts);
    } catch {
      // Backend not ready yet or unauthenticated
    }
  }, []);

  useEffect(() => {
    refreshAlerts();
  }, [refreshAlerts]);

  const unreadCount = alerts.filter((a) => !a.isRead).length;

  const addAlert = useCallback((newAlertMsg: WebSocketAlertMessage) => {
    const alertWithState: AlertState = {
      ...newAlertMsg,
      isRead: false,
    };

    setAlerts((prev) => {
      // Avoid duplicate alert cards for identical alert_id or event_id
      const exists = prev.some(
        (a) =>
          a.alert_id === alertWithState.alert_id ||
          (alertWithState.event_id && a.event_id === alertWithState.event_id)
      );
      if (exists) return prev;
      return [alertWithState, ...prev.slice(0, 99)];
    });
    setLatestAlert(newAlertMsg);
  }, []);

  const { isConnected: isWsConnected, connectionError: wsError, triggerTestAlert } = useWebSocket({
    onMessage: addAlert,
    autoConnect: true,
  });

  const markAsRead = useCallback(async (alertId: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.alert_id === alertId ? { ...a, isRead: true } : a))
    );
    try {
      await alertService.acknowledgeAlert(alertId);
    } catch {
      // Silently handle if error / unauthorized
    }
  }, []);

  const markAllAsRead = useCallback(() => {
    setAlerts((prev) => prev.map((a) => ({ ...a, isRead: true })));
  }, []);

  const clearAlerts = useCallback(() => {
    setAlerts([]);
    setLatestAlert(null);
  }, []);

  const openEvidenceModal = useCallback((evidenceId: string) => {
    setActiveEvidenceModalId(evidenceId);
  }, []);

  const closeEvidenceModal = useCallback(() => {
    setActiveEvidenceModalId(null);
  }, []);

  const toggleAudioMute = useCallback(() => {
    setIsAudioMuted((prev) => !prev);
  }, []);

  return (
    <AlertContext.Provider
      value={{
        alerts,
        unreadCount,
        latestAlert,
        activeEvidenceModalId,
        isAudioMuted,
        isWsConnected,
        wsError,
        addAlert,
        markAsRead,
        markAllAsRead,
        clearAlerts,
        openEvidenceModal,
        closeEvidenceModal,
        toggleAudioMute,
        refreshAlerts,
        triggerTestAlert,
      }}
    >
      {children}
    </AlertContext.Provider>
  );
}

export function useAlertContext(): AlertContextType {
  const context = useContext(AlertContext);
  if (!context) {
    throw new Error("useAlertContext must be used within an AlertProvider");
  }
  return context;
}

export const useAlerts = useAlertContext;
