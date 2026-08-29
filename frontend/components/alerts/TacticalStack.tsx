"use client";

import React, { useState } from "react";
import { Check, X, Edit3, ChevronUp, Radio } from "lucide-react";
import { useAlerts } from "../../hooks/useAlerts";
import { formatTimeAgo } from "../../utils/formatters";

export const TacticalStack: React.FC = () => {
  const { alerts, latestAlert, openEvidenceModal } = useAlerts();
  const [annotation, setAnnotation] = useState("Suspect heading east...");

  // 20-segment LED bar
  const totalSegments = 20;
  const activeSegments = alerts.length > 0 ? Math.min(20, Math.max(8, alerts.length * 4)) : 15;

  // Real alerts to display (up to 3)
  const displayAlerts = alerts.slice(0, 3);

  return (
    <div className="flex flex-col gap-3.5 h-full">
      {/* 1. THREAT LEVEL CARD */}
      <div className="surveillance-card border border-white/15 bg-surface-200/90 rounded-lg p-4 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono font-bold tracking-wider text-slate-300">
            THREAT LEVEL
          </span>
          <span className="text-xs font-mono text-red-400 font-bold">
            {alerts.length > 0 ? `(${Math.min(95, alerts.length * 20 + 35)}%)` : "(75%)"}
          </span>
        </div>

        {/* Segmented LED Bar */}
        <div className="flex items-center gap-1">
          {Array.from({ length: totalSegments }).map((_, idx) => (
            <div
              key={idx}
              className={`h-4 flex-1 rounded-[1.5px] transition-all ${
                idx < activeSegments
                  ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]"
                  : "bg-red-950/40 border border-red-900/40"
              }`}
            />
          ))}
        </div>

        <div className="flex items-center justify-between text-xs font-mono text-slate-400">
          <span>Active Alerts: <strong className="text-slate-100">{alerts.length || 3}</strong></span>
        </div>

        {/* Sparkline Wave Chart with Glowing Peak Dot */}
        <div className="relative pt-1">
          <svg viewBox="0 0 200 40" className="w-full h-10 overflow-visible">
            {/* Wave Grid Lines */}
            <line x1="0" y1="20" x2="200" y2="20" stroke="rgba(255,255,255,0.06)" strokeDasharray="3,3" />
            <line x1="0" y1="35" x2="200" y2="35" stroke="rgba(255,255,255,0.06)" />

            {/* Sparkline Path */}
            <path
              d="M 0,30 Q 20,25 35,28 T 70,32 T 105,22 T 140,26 T 170,8 T 200,28"
              fill="none"
              stroke="#38bdf8"
              strokeWidth="2"
              className="filter drop-shadow-[0_0_6px_rgba(56,189,248,0.5)]"
            />
            {/* Peak Alert Dot */}
            <circle cx="170" cy="8" r="4" fill="#ef4444" className="animate-ping" />
            <circle cx="170" cy="8" r="3" fill="#ef4444" />
          </svg>
        </div>
      </div>

      {/* 2. TACTICAL FEED CARD */}
      <div className="surveillance-card border border-white/15 bg-surface-200/90 rounded-lg p-4 flex-1 flex flex-col justify-between">
        <div className="space-y-3">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-white/10 pb-2.5">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold tracking-wider text-slate-200">
                TACTICAL FEED
              </span>
              <span className="text-[11px] font-mono text-slate-400">
                ({alerts.length || 3} Incidents)
              </span>
            </div>
            <ChevronUp className="w-4 h-4 text-slate-400 cursor-pointer hover:text-white" />
          </div>

          {/* Render Real Alerts if present, or initial tactical cards */}
          {displayAlerts.length > 0 ? (
            displayAlerts.map((alt, idx) => (
              <div
                key={alt.alert_id || idx}
                className="p-3 rounded-lg bg-red-950/40 border border-red-600 shadow-[0_0_15px_rgba(239,68,68,0.25)] space-y-2.5 animate-fade-in"
              >
                <div className="flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center gap-1.5 font-bold text-red-400">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                    <span>{alt.event_type || "INTRUSION"}</span>
                    {alt.track_id && <span className="text-[10px] text-slate-400">#{alt.track_id}</span>}
                  </div>
                  <span className="text-slate-400 text-[10px]" suppressHydrationWarning>
                    {formatTimeAgo(alt.timestamp)}
                  </span>
                </div>

                <div className="text-xs font-mono text-slate-300">
                  Area: <strong className="text-slate-100">{alt.zone_name || "SECTOR-4 | CAM-01"}</strong>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-2 pt-1">
                  <button
                    onClick={() => openEvidenceModal(alt.evidence_id)}
                    className="flex-1 flex items-center justify-center gap-1 py-1.5 px-3 rounded bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-mono font-bold text-xs shadow-[0_0_10px_rgba(16,185,129,0.4)] transition"
                  >
                    <Check className="w-3.5 h-3.5 stroke-[3]" />
                    <span>VERIFY EVIDENCE</span>
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="p-3 rounded-lg bg-red-950/40 border border-red-600 shadow-[0_0_15px_rgba(239,68,68,0.25)] space-y-2.5">
              <div className="flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-1.5 font-bold text-red-400">
                  <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                  <span>INTRUSION SYSTEM ACTIVE</span>
                </div>
                <span className="text-slate-400">READY</span>
              </div>
              <div className="text-xs font-mono text-slate-300">
                Area: <strong className="text-slate-100">RESTRICTED ZONE (SECTOR 4)</strong>
              </div>
              <div className="text-[11px] font-mono text-slate-400">
                Move inside the virtual zone to trigger instant webcam evidence capture.
              </div>
            </div>
          )}
        </div>

        {/* Bottom Info Bar */}
        <div className="pt-3 border-t border-white/10 flex items-center justify-between text-[11px] font-mono text-slate-500">
          <span>AI v2.4 (YOLOv8)</span>
          <span>WEBCAM FORENSICS: ACTIVE</span>
        </div>
      </div>
    </div>
  );
};
