"use client";

import React from "react";
import { Monitor, Cpu, Radio, Target, Camera } from "lucide-react";

export const TacticalFooter: React.FC = () => {
  return (
    <footer className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 pt-1 text-xs font-mono">
      {/* Card 1: CPU LOAD */}
      <div className="surveillance-card border border-amber-500/30 bg-surface-200/80 rounded-lg p-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Monitor className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <span className="text-[11px] text-slate-400 font-bold block">CPU LOAD:</span>
            {/* Orange Progress Bar */}
            <div className="w-24 h-2 rounded-full bg-surface-100 overflow-hidden border border-amber-500/30">
              <div className="h-full bg-amber-500 rounded-full w-[58%]" />
            </div>
          </div>
        </div>
        <span className="text-sm font-bold text-amber-400">58%</span>
      </div>

      {/* Card 2: AI MODEL STATUS */}
      <div className="surveillance-card border border-emerald-500/30 bg-surface-200/80 rounded-lg p-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Cpu className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <span className="text-[11px] text-slate-400 font-bold block">AI MODEL STATUS:</span>
            {/* Green Progress Bar */}
            <div className="w-24 h-2 rounded-full bg-surface-100 overflow-hidden border border-emerald-500/30">
              <div className="h-full bg-emerald-400 rounded-full w-[100%]" />
            </div>
          </div>
        </div>
        <div className="text-right">
          <span className="text-[11px] text-emerald-400 font-bold flex items-center gap-1 justify-end">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            OK
          </span>
          <span className="text-[11px] text-slate-400">100%</span>
        </div>
      </div>

      {/* Card 3: SIGNAL STRENGTH */}
      <div className="surveillance-card border border-cyan-500/30 bg-surface-200/80 rounded-lg p-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Radio className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <span className="text-[11px] text-slate-400 font-bold block">SIGNAL STRENGTH:</span>
            {/* Dual Cyan Bars */}
            <div className="w-24 h-2 rounded-full bg-surface-100 overflow-hidden border border-cyan-500/30">
              <div className="h-full bg-cyan-400 rounded-full w-[85%]" />
            </div>
          </div>
        </div>
        <span className="text-sm font-bold text-cyan-400">85%</span>
      </div>

      {/* Card 4: TELEMETRY TOTALS */}
      <div className="surveillance-card border border-white/15 bg-surface-200/80 rounded-lg p-3 flex items-center justify-around text-slate-300">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-blue-400" />
          <div>
            <span className="text-[10px] text-slate-500 block">Total Detections:</span>
            <strong className="text-sm text-slate-100 font-bold font-mono">12</strong>
          </div>
        </div>

        <div className="h-6 w-[1px] bg-white/10" />

        <div className="flex items-center gap-2">
          <Camera className="w-4 h-4 text-purple-400" />
          <div>
            <span className="text-[10px] text-slate-500 block">Screenshots:</span>
            <strong className="text-sm text-slate-100 font-bold font-mono">8</strong>
          </div>
        </div>
      </div>
    </footer>
  );
};
