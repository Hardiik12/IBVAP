"use client";

import React from "react";
import { useHealthCheck } from "../../hooks/useHealthCheck";
import { useAlerts } from "../../hooks/useAlerts";

export const SystemStatusBadge: React.FC = () => {
  const { health, isHealthy } = useHealthCheck();
  const { isWsConnected } = useAlerts();

  const isOffline = !health || health.status === "offline";
  const isNormal = isHealthy || health?.status === "healthy" || health?.status === "ok";

  let badgeColor = "bg-emerald-400 animate-pulse";
  let statusText = "BACKEND ● CONNECTED";
  let dbColor = "text-emerald-400";
  let dbText = health?.database?.toUpperCase() || "CONNECTED";

  if (isOffline) {
    badgeColor = "bg-rose-500";
    statusText = "BACKEND ● OFFLINE";
    dbColor = "text-rose-400";
    dbText = "DISCONNECTED";
  } else if (!isNormal) {
    badgeColor = "bg-amber-400";
    statusText = "BACKEND ● DEGRADED";
    dbColor = "text-amber-400";
  }

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-100 border border-surface-border text-xs font-mono">
      <div className="flex items-center gap-1.5">
        <span className={`w-2 h-2 rounded-full ${badgeColor}`} />
        <span
          className={`font-semibold ${
            isOffline ? "text-rose-400" : isNormal ? "text-slate-300" : "text-amber-300"
          }`}
        >
          {statusText}
        </span>
      </div>

      <span className="text-slate-600">|</span>

      <span className="text-slate-400">
        WS:{" "}
        <span className={isWsConnected ? "text-emerald-400 font-semibold" : "text-slate-500"}>
          {isWsConnected ? "CONNECTED" : "OFFLINE"}
        </span>
      </span>

      <span className="text-slate-600">|</span>

      <span className="text-slate-400">
        DB: <span className={dbColor}>{dbText}</span>
      </span>

      {health?.fps !== undefined && !isOffline && (
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
