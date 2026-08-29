"use client";

import React, { useState } from "react";
import { Check, X, Edit3, ChevronUp, Radio } from "lucide-react";
import { useAlerts } from "../../hooks/useAlerts";

export const TacticalStack: React.FC = () => {
  const { openEvidenceModal } = useAlerts();
  const [annotation, setAnnotation] = useState("Suspect heading east...");

  // 20-segment LED bar
  const totalSegments = 20;
  const activeSegments = 15; // 75%

  return (
    <div className="flex flex-col gap-3.5 h-full">
      {/* 1. THREAT LEVEL CARD */}
      <div className="surveillance-card border border-white/15 bg-surface-200/90 rounded-lg p-4 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono font-bold tracking-wider text-slate-300">
            THREAT LEVEL
          </span>
          <span className="text-xs font-mono text-red-400 font-bold">(75%)</span>
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
          <span>Intrusions/hr: <strong className="text-slate-100">12</strong></span>
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
              <span className="text-[11px] font-mono text-slate-400">(3 Pending)</span>
            </div>
            <ChevronUp className="w-4 h-4 text-slate-400 cursor-pointer hover:text-white" />
          </div>

          {/* Alert Item 1: INTRUSION (Red Glowing Card) */}
          <div className="p-3 rounded-lg bg-red-950/40 border border-red-600 shadow-[0_0_15px_rgba(239,68,68,0.25)] space-y-2.5">
            <div className="flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-1.5 font-bold text-red-400">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                <span>INTRUSION</span>
              </div>
              <span className="text-slate-400">14:27:35</span>
            </div>

            <div className="text-xs font-mono text-slate-300">
              Area: <strong className="text-slate-100">SECTOR-4 | CAM-01</strong>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2 pt-1">
              <button
                onClick={() => openEvidenceModal("evi-33104")}
                className="flex-1 flex items-center justify-center gap-1 py-1.5 px-3 rounded bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-mono font-bold text-xs shadow-[0_0_10px_rgba(16,185,129,0.4)] transition"
              >
                <Check className="w-3.5 h-3.5 stroke-[3]" />
                <span>CONFIRM</span>
              </button>

              <button className="flex-1 flex items-center justify-center gap-1 py-1.5 px-3 rounded bg-surface-100 hover:bg-surface-50 border border-white/10 text-slate-300 font-mono text-xs transition">
                <X className="w-3.5 h-3.5" />
                <span>FALSE</span>
              </button>
            </div>

            {/* Annotation Box */}
            <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded bg-black/50 border border-white/10 text-[11px] font-mono text-slate-400">
              <Edit3 className="w-3 h-3 text-slate-500 shrink-0" />
              <input
                type="text"
                value={annotation}
                onChange={(e) => setAnnotation(e.target.value)}
                placeholder="Annotate incident..."
                className="bg-transparent border-none text-slate-200 placeholder-slate-500 focus:outline-none w-full text-[11px]"
              />
            </div>
          </div>

          {/* Alert Item 2: VEHICLE (Amber Card) */}
          <div className="p-3 rounded-lg bg-amber-950/25 border border-amber-600/70 space-y-2">
            <div className="flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-1.5 font-bold text-amber-400">
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                <span>VEHICLE</span>
              </div>
              <span className="text-slate-400">14:26:10</span>
            </div>

            <div className="text-xs font-mono text-slate-300">
              Area: <strong className="text-slate-100">SECTOR-4</strong>
            </div>

            <div className="flex items-center gap-2 pt-0.5">
              <button
                onClick={() => openEvidenceModal("evi-33106")}
                className="flex-1 flex items-center justify-center gap-1 py-1.5 px-3 rounded bg-emerald-500/90 hover:bg-emerald-400 text-slate-950 font-mono font-bold text-xs transition"
              >
                <Check className="w-3.5 h-3.5 stroke-[3]" />
                <span>CONFIRM</span>
              </button>

              <button className="flex-1 flex items-center justify-center gap-1 py-1.5 px-3 rounded bg-surface-100 hover:bg-surface-50 border border-white/10 text-slate-300 font-mono text-xs transition">
                <X className="w-3.5 h-3.5" />
                <span>FALSE</span>
              </button>
            </div>
          </div>

          {/* Alert Item 3: RESOLVED (Gray Card) */}
          <div className="p-2.5 rounded-lg bg-surface-100/60 border border-white/10 flex items-center justify-between text-xs font-mono text-slate-400">
            <div className="flex items-center gap-1.5">
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-slate-300 font-bold">RESOLVED</span>
              <span className="text-slate-500">| Area: SECTOR-2</span>
            </div>
            <span>14:20:01</span>
          </div>
        </div>

        {/* Bottom Info Bar */}
        <div className="pt-3 border-t border-white/10 flex items-center justify-between text-[11px] font-mono text-slate-500">
          <span>AI v2.4</span>
          <span>UPTIME: 48m</span>
        </div>
      </div>
    </div>
  );
};
