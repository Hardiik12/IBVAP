"use client";

import React from "react";
import { useHealthCheck } from "../../hooks/useHealthCheck";
import { Activity, ShieldCheck, AlertTriangle } from "lucide-react";

export const SystemStatusBadge: React.FC = () => {
  const { health, isHealthy } = useHealthCheck();

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-100 border border-surface-border text-xs font-mono">
      <div className="flex items-center gap-1.5">
        <span
          className={`w-2 h-2 rounded-full ${
            isHealthy ? "bg-emerald-400 animate-pulse" : "bg-amber-400"
          }`}
        />
        <span className="text-slate-300 font-medium">
          {health?.status === "healthy" || health?.status === "ok" ? "SYSTEM NORMAL" : "DEGRADED"}
        </span>

      </div>

      <span className="text-slate-600">|</span>

      <span className="text-slate-400">
        DB: <span className="text-emerald-400">{health?.database || "CONNECTED"}</span>
      </span>

      {health?.fps !== undefined && (
        <>
          <span className="text-slate-600">|</span>
          <span className="text-slate-400">
            FPS: <span className="text-blue-400">{health.fps.toFixed(1)}</span>
          </span>
        </>
      )}
    </div>
  );
};
