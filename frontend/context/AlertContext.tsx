"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { WebSocketAlertMessage, AlertState } from "../types/alert";
import { MOCK_EVENTS } from "../services/mockData";

interface AlertContextType {
  alerts: AlertState[];
  unreadCount: number;
  latestAlert: WebSocketAlertMessage | null;
  activeEvidenceModalId: string | null;
  isAudioMuted: boolean;
  addAlert: (alert: WebSocketAlertMessage) => void;
  markAsRead: (alertId: string) => void;
  markAllAsRead: () => void;
  clearAlerts: () => void;
  openEvidenceModal: (evidenceId: string) => void;
  closeEvidenceModal: () => void;
  toggleAudioMute: () => void;
}

const AlertContext = createContext<AlertContextType | undefined>(undefined);

export function AlertProvider({ children }: { children: React.ReactNode }) {
  const [alerts, setAlerts] = useState<AlertState[]>(() => {
    return MOCK_EVENTS.map((e) => ({
      type: "NEW_ALERT",
      alert_id: `alt-${e.event_id.replace("evt-", "")}`,
      event_id: e.event_id,
      event_type: e.event_type,
      camera_id: e.camera_id,
      camera_name: e.camera_id === "cam-01" ? "Perimeter Sector Alpha" : "North Gate Entrance",
      zone_name: e.zone_name || "Perimeter Exclusion Zone 1",
      track_id: e.track_id,
      class_name: e.class_name,
      confidence: e.confidence,
      severity: e.severity,
      timestamp: e.timestamp,
      evidence_id: e.evidence_id || "evi-33104",
      bbox: e.bbox,
      isRead: false,
    }));
  });

  const [latestAlert, setLatestAlert] = useState<WebSocketAlertMessage | null>(null);
  const [activeEvidenceModalId, setActiveEvidenceModalId] = useState<string | null>(null);
  const [isAudioMuted, setIsAudioMuted] = useState(false);

  const unreadCount = alerts.filter((a) => !a.isRead).length;

  const addAlert = useCallback((newAlertMsg: WebSocketAlertMessage) => {
    const alertWithState: AlertState = {
      ...newAlertMsg,
      isRead: false,
    };

    setAlerts((prev) => [alertWithState, ...prev.slice(0, 49)]); // keep last 50
    setLatestAlert(newAlertMsg);
  }, []);

  const markAsRead = useCallback((alertId: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.alert_id === alertId ? { ...a, isRead: true } : a))
    );
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
        addAlert,
        markAsRead,
        markAllAsRead,
        clearAlerts,
        openEvidenceModal,
        closeEvidenceModal,
        toggleAudioMute,
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

