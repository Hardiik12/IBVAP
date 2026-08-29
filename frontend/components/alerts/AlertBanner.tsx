"use client";

import React, { useState, useEffect } from "react";
import { useAlerts } from "../../hooks/useAlerts";
import { ShieldAlert, ArrowRight } from "lucide-react";
import { formatTimeAgo } from "../../utils/formatters";

export const AlertBanner: React.FC = () => {
  const { latestAlert, openEvidenceModal } = useAlerts();
  const [, setTick] = useState(0);

  // Live timer tick to continuously refresh relative time display every 2 seconds
  useEffect(() => {
    if (!latestAlert) return;
    const interval = setInterval(() => {
      setTick((t) => t + 1);
    }, 2000);
    return () => clearInterval(interval);
  }, [latestAlert]);

  if (!latestAlert) return null;

  return (
    <div className="bg-red-950/90 border-b border-red-800 text-red-100 px-6 py-2.5 flex items-center justify-between shadow-lg shadow-red-950/50 backdrop-blur-md animate-fade-in">
      <div className="flex items-center gap-3">
        <span className="p-1.5 rounded bg-red-900 text-red-300 animate-pulse">
          <ShieldAlert className="w-5 h-5" />
        </span>
        <div>
          <span className="font-bold text-sm text-red-200">
            SECURITY BREACH DETECTED:
          </span>{" "}
          <span className="text-xs text-red-300 font-mono">
            Track #{latestAlert.track_id} ({latestAlert.class_name || "person"}) entered{" "}
            <strong>{latestAlert.zone_name}</strong>
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <span className="text-xs font-mono text-red-400 font-bold" suppressHydrationWarning>
          {formatTimeAgo(latestAlert.timestamp)}
        </span>

        <button
          onClick={() => openEvidenceModal(latestAlert.evidence_id)}
          className="flex items-center gap-1.5 text-xs font-bold px-3 py-1 rounded bg-red-600 hover:bg-red-500 text-white transition shadow-sm"
        >
          <span>Verify Evidence</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
