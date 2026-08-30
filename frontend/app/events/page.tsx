"use client";

import React, { useState, useEffect } from "react";
import { EventTable } from "../../components/events/EventTable";
import { ClearLogsModal } from "../../components/events/ClearLogsModal";
import { eventService } from "../../services/eventService";
import { cameraService } from "../../services/cameraService";
import { IntrusionEvent } from "../../types/event";
import { Camera } from "../../types/camera";
import { useAuth } from "../../context/AuthContext";
import {
  ListOrdered,
  Download,
  Trash2,
  CheckCircle2,
  AlertCircle,
  ShieldAlert,
} from "lucide-react";
import { Button } from "../../components/ui/Button";

export default function EventsPage() {
  const { user } = useAuth();
  const [events, setEvents] = useState<IntrusionEvent[]>([]);
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modal and action states
  const [isClearModalOpen, setIsClearModalOpen] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [toastMessage, setToastMessage] = useState<{
    text: string;
    type: "success" | "error";
  } | null>(null);

  const isAdmin = user?.role === "ADMINISTRATOR";

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [evts, cams] = await Promise.all([
          eventService.getEvents(),
          cameraService.getCameras(),
        ]);
        setEvents(evts);
        setCameras(cams);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  // Auto-dismiss toast after 4 seconds
  useEffect(() => {
    if (toastMessage) {
      const timer = setTimeout(() => {
        setToastMessage(null);
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [toastMessage]);

  const handleClearLogsConfirm = async () => {
    if (!isAdmin) {
      setToastMessage({
        text: "Access Denied: Only Administrators can clear audit logs.",
        type: "error",
      });
      setIsClearModalOpen(false);
      return;
    }

    setIsClearing(true);
    try {
      await eventService.clearEvents();
      // Immediately clear state to display empty state
      setEvents([]);
      setIsClearModalOpen(false);
      setToastMessage({
        text: "Audit logs cleared successfully",
        type: "success",
      });
    } catch (err: any) {
      console.error("Failed to clear audit logs:", err);
      const errDetail =
        err.response?.data?.detail || err.message || "Failed to clear logs.";
      setToastMessage({
        text: `Clear Failed: ${errDetail}`,
        type: "error",
      });
      setIsClearModalOpen(false);
    } finally {
      setIsClearing(false);
    }
  };

  const exportJsonLog = () => {
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(events, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute(
      "download",
      `ibvap_events_${new Date().toISOString().slice(0, 10)}.json`
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl relative">
      {/* Temporary Notification Toast */}
      {toastMessage && (
        <div className="fixed top-6 right-6 z-50 animate-in slide-in-from-top-4 duration-300">
          <div
            className={`flex items-center gap-3 px-5 py-3.5 rounded-xl border font-mono text-xs shadow-2xl backdrop-blur-xl ${
              toastMessage.type === "success"
                ? "bg-emerald-950/90 border-emerald-500/60 text-emerald-300 shadow-[0_0_30px_rgba(16,185,129,0.3)]"
                : "bg-red-950/90 border-red-500/60 text-red-300 shadow-[0_0_30px_rgba(239,68,68,0.3)]"
            }`}
          >
            {toastMessage.type === "success" ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
            )}
            <span className="font-semibold">{toastMessage.text}</span>
          </div>
        </div>
      )}

      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <ListOrdered className="w-5 h-5 text-blue-400" />
            <span>Forensic Event Audit Log</span>
          </h1>
          <p className="text-xs font-mono text-slate-400 mt-1">
            Immutable log of all detected boundary crossings and state machine transitions
          </p>
        </div>

        {/* Header Action Buttons */}
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            onClick={exportJsonLog}
            disabled={events.length === 0}
            leftIcon={<Download className="w-4 h-4" />}
          >
            Export JSON Audit
          </Button>

          {/* Clearly Visible Clear Logs Button */}
          {isAdmin && (
            <button
              onClick={() => setIsClearModalOpen(true)}
              disabled={events.length === 0}
              title={
                events.length === 0
                  ? "No logs to clear"
                  : "Permanently delete all audit log records"
              }
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-red-950/40 hover:bg-red-900/60 disabled:opacity-40 disabled:cursor-not-allowed border border-red-800/80 hover:border-red-600 text-red-300 hover:text-red-100 text-xs font-mono font-medium transition cursor-pointer shadow-[0_0_15px_rgba(239,68,68,0.15)]"
            >
              <Trash2 className="w-3.5 h-3.5 text-red-400" />
              <span>Clear Logs</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Event Table */}
      <EventTable events={events} cameras={cameras} />

      {/* Confirmation Modal */}
      <ClearLogsModal
        isOpen={isClearModalOpen}
        onClose={() => setIsClearModalOpen(false)}
        onConfirm={handleClearLogsConfirm}
        isClearing={isClearing}
      />
    </div>
  );
}
