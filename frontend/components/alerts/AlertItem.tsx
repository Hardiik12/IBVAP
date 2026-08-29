"use client";

import React, { useState, useEffect } from "react";
import { AlertState } from "../../types/alert";
import { Badge } from "../ui/Badge";
import { formatTimeAgo } from "../../utils/formatters";
import { FileSearch, CheckCircle2 } from "lucide-react";
import { useAlerts } from "../../hooks/useAlerts";

interface AlertItemProps {
  alert: AlertState;
}

export const AlertItem: React.FC<AlertItemProps> = ({ alert }) => {
  const { markAsRead, openEvidenceModal } = useAlerts();
  const [, setTick] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setTick((t) => t + 1);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`p-3.5 rounded-lg border transition-all ${
        alert.isRead
          ? "bg-surface-200/40 border-surface-border text-slate-400"
          : "bg-surface-100 border-slate-700 text-slate-200 shadow-sm shadow-blue-500/5"
      }`}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <Badge severity={alert.severity}>{alert.severity}</Badge>
          <span className="text-xs font-mono font-bold text-slate-300">
            TRACK #{alert.track_id}
          </span>
        </div>
        <span className="text-[11px] font-mono text-slate-400 font-bold" suppressHydrationWarning>
          {formatTimeAgo(alert.timestamp)}
        </span>
      </div>

      <div className="text-xs text-slate-300 mb-2.5">
        <p className="font-medium text-slate-200">{alert.zone_name}</p>
        <p className="text-slate-400 text-[11px] font-mono">
          Camera: {alert.camera_name || alert.camera_id} • Object: {alert.class_name || "person"}
        </p>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-surface-border/60">
        <button
          onClick={() => openEvidenceModal(alert.evidence_id)}
          className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-mono font-medium transition"
        >
          <FileSearch className="w-3.5 h-3.5" />
          <span>Inspect Evidence</span>
        </button>

        {!alert.isRead ? (
          <button
            onClick={() => markAsRead(alert.alert_id)}
            className="flex items-center gap-1 text-[11px] text-slate-500 hover:text-slate-300 font-mono transition"
            title="Mark as Acknowledged"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Ack</span>
          </button>
        ) : (
          <span className="text-[10px] font-mono text-slate-500">ACKNOWLEDGED</span>
        )}
      </div>
    </div>
  );
};
