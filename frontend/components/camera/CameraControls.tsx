"use client";

import React from "react";
import { useCameraContext } from "../../context/CameraContext";
import { ShieldAlert, Scan, Eye, Radio, RefreshCw } from "lucide-react";
import { Button } from "../ui/Button";

export const CameraControls: React.FC = () => {
  const {
    showZones,
    showBoundingBoxes,
    showHud,
    toggleZones,
    toggleBoundingBoxes,
    toggleHud,
    refreshCameras,
    isLoading,
  } = useCameraContext();

  return (
    <div className="flex items-center justify-between px-4 py-2.5 bg-surface-100/80 border-t border-surface-border text-xs font-mono">
      <div className="flex items-center gap-2">
        <span className="text-slate-400 font-semibold mr-1">OVERLAYS:</span>

        {/* Zones Toggle */}
        <button
          onClick={toggleZones}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded border transition ${
            showZones
              ? "bg-amber-950/70 border-amber-600 text-amber-300"
              : "bg-surface-200 border-surface-border text-slate-500"
          }`}
        >
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>FENCE POLYGONS</span>
        </button>

        {/* Bounding Boxes Toggle */}
        <button
          onClick={toggleBoundingBoxes}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded border transition ${
            showBoundingBoxes
              ? "bg-emerald-950/70 border-emerald-600 text-emerald-300"
              : "bg-surface-200 border-surface-border text-slate-500"
          }`}
        >
          <Scan className="w-3.5 h-3.5" />
          <span>AI BOUNDING BOXES</span>
        </button>

        {/* HUD Telemetry Toggle */}
        <button
          onClick={toggleHud}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded border transition ${
            showHud
              ? "bg-blue-950/70 border-blue-600 text-blue-300"
              : "bg-surface-200 border-surface-border text-slate-500"
          }`}
        >
          <Eye className="w-3.5 h-3.5" />
          <span>HUD TELEMETRY</span>
        </button>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={refreshCameras}
          disabled={isLoading}
          className="text-slate-400 hover:text-slate-200 transition p-1 hover:bg-surface-200 rounded"
          title="Refresh Camera Sources"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
        </button>
      </div>
    </div>
  );
};
