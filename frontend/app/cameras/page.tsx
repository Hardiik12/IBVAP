"use client";

import React from "react";
import { useCameraContext } from "../../context/CameraContext";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { Video, ShieldAlert, CheckCircle, Radio, Settings2 } from "lucide-react";
import { Button } from "../../components/ui/Button";

export default function CamerasPage() {
  const { cameras, selectedCamera, selectCamera, zones } = useCameraContext();

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Video className="w-5 h-5 text-blue-400" />
            <span>Camera Sources & Restricted Zones</span>
          </h1>
          <p className="text-xs font-mono text-slate-400 mt-1">
            Manage video input streams (Webcam, Video File, Phone IP) and polygon fence geometries
          </p>
        </div>
      </div>

      {/* Cameras Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {cameras.map((cam) => {
          const isSelected = selectedCamera?.id === cam.id;
          const camZones = zones.filter((z) => z.camera_id === cam.id || z.camera_id === "cam-01");

          return (
            <Card
              key={cam.id}
              className={`bg-surface-200 border transition-all ${
                isSelected ? "border-blue-500 shadow-md shadow-blue-500/10" : "border-surface-border"
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-lg bg-blue-950/60 border border-blue-800/80 flex items-center justify-center text-blue-400">
                    <Video className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm text-slate-100">{cam.name}</h3>
                    <p className="text-xs font-mono text-slate-400">ID: {cam.id}</p>
                  </div>
                </div>
                <Badge status={cam.status}>{cam.status}</Badge>
              </div>

              {/* Technical Telemetry */}
              <div className="bg-surface-300 border border-surface-border rounded-lg p-3 space-y-2 text-xs font-mono text-slate-300 mb-4">
                <div className="flex justify-between">
                  <span className="text-slate-500">SOURCE TYPE:</span>
                  <span>{cam.source_type.toUpperCase()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">INDEX / PATH:</span>
                  <span className="truncate max-w-[200px] text-slate-400">{cam.source_index}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">STREAM RESOLUTION:</span>
                  <span>{cam.resolution || "1280x720"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">CURRENT THROUGHPUT:</span>
                  <span className="text-emerald-400">{cam.fps || 30} FPS</span>
                </div>
              </div>

              {/* Associated Restricted Zones */}
              <div className="space-y-2 mb-4">
                <div className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                  <span>CONFIGURED POLYGON ZONES ({camZones.length})</span>
                </div>
                {camZones.map((z) => (
                  <div
                    key={z.id}
                    className="p-2 rounded bg-surface-100 border border-surface-border flex items-center justify-between text-xs font-mono"
                  >
                    <span className="text-slate-200">{z.name}</span>
                    <span className="text-slate-500">{z.polygon.length} points (Normalized)</span>
                  </div>
                ))}
              </div>

              {/* Switch Active Feed Button */}
              <Button
                variant={isSelected ? "primary" : "secondary"}
                size="sm"
                className="w-full"
                onClick={() => selectCamera(cam.id)}
                disabled={cam.status !== "ACTIVE"}
              >
                {isSelected ? "Currently Monitoring" : "Switch to this Feed"}
              </Button>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
