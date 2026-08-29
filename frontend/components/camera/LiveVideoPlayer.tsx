"use client";

import React, { useRef, useState } from "react";
import { CanvasOverlay } from "./CanvasOverlay";
import { WebcamFeed } from "./WebcamFeed";
import { CameraControls } from "./CameraControls";
import { useWebcam } from "../../hooks/useWebcam";
import { useAIDetection } from "../../hooks/useAIDetection";
import { useCameraContext } from "../../context/CameraContext";
import { useAlerts } from "../../hooks/useAlerts";
import { Maximize2, Video, VideoOff, Cpu } from "lucide-react";

export const LiveVideoPlayer: React.FC = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const { selectedCamera, zones, showZones, showBoundingBoxes, showHud } = useCameraContext();
  const { latestAlert, addAlert } = useAlerts();

  // 1. Initialize browser webcam stream
  const webcam = useWebcam({
    autoStart: true,
    idealWidth: 1280,
    idealHeight: 720,
    facingMode: "user",
  });

  // 2. Real-time Python YOLOv8 Detector & Tracker + Automatic Evidence Capture on Breach
  const { detections, inferenceMs } = useAIDetection({
    videoRef: webcam.videoRef,
    isEnabled: webcam.status === "active",
    zones,
    cameraId: selectedCamera?.id || "cam-01",
    confidenceThreshold: 0.3,
    intervalMs: 130, // ~7-8 FPS continuous AI vision stream
    onIntrusion: (item, evidenceRecord) => {
      // Dispatch real intrusion event to alert system with the REAL captured evidence ID
      addAlert({
        type: "NEW_ALERT",
        alert_id: `alt-${Math.floor(Math.random() * 90000) + 10000}`,
        event_id: evidenceRecord.event_id,
        event_type: "INTRUSION",
        camera_id: selectedCamera?.id || "cam-01",
        camera_name: selectedCamera?.name || "MacBook Webcam",
        zone_name: item.zone_name || "Perimeter Exclusion Zone 1",
        track_id: item.track_id,
        class_name: item.class_name,
        confidence: item.confidence,
        severity: "CRITICAL",
        timestamp: evidenceRecord.captured_at,
        evidence_id: evidenceRecord.evidence_id,
        bbox: item.bbox,
      });
    },
  });

  const [isFullscreen, setIsFullscreen] = useState(false);

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  // Sample Heatmap 10x10 Matrix colors
  const heatmapGrid = [
    ["#10b981", "#10b981", "#f59e0b", "#f59e0b", "#ef4444", "#ef4444", "#ef4444", "#3b82f6", "#3b82f6", "#3b82f6"],
    ["#10b981", "#10b981", "#f59e0b", "#f59e0b", "#ef4444", "#ef4444", "#ef4444", "#3b82f6", "#3b82f6", "#3b82f6"],
    ["#10b981", "#f59e0b", "#f59e0b", "#ef4444", "#ef4444", "#ef4444", "#ef4444", "#3b82f6", "#3b82f6", "#1e293b"],
    ["#10b981", "#f59e0b", "#ef4444", "#ef4444", "#ef4444", "#ef4444", "#3b82f6", "#3b82f6", "#1e293b", "#1e293b"],
    ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#ef4444", "#3b82f6", "#3b82f6", "#1e293b", "#1e293b", "#1e293b"],
    ["#3b82f6", "#3b82f6", "#10b981", "#f59e0b", "#3b82f6", "#3b82f6", "#1e293b", "#1e293b", "#1e293b", "#1e293b"],
  ];

  return (
    <div
      ref={containerRef}
      className="surveillance-card flex flex-col overflow-hidden shadow-2xl relative border border-white/15 bg-black rounded-lg"
    >
      {/* Video Viewport */}
      <div className="relative aspect-[16/9] w-full bg-black overflow-hidden flex items-center justify-center">
        {/* Real MacBook / USB Webcam Video Stream */}
        <WebcamFeed webcam={webcam} cameraName={selectedCamera?.name} />

        {/* Tactical Scanlines */}
        <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-25 pointer-events-none z-10" />

        {/* Live Canvas Overlay (Corner Reticles, Virtual Fence, REAL YOLOv8 Dynamic Bounding Boxes) */}
        {webcam.status === "active" && (
          <CanvasOverlay
            zones={zones}
            activeAlert={latestAlert}
            detections={detections}
            showZones={showZones}
            showBoundingBoxes={showBoundingBoxes}
            showHud={showHud}
            cameraId={selectedCamera?.id || "cam-01"}
          />
        )}

        {/* Top-Right Live Stream HUD Telemetry & Webcam Controls */}
        <div className="absolute top-3 right-3 z-20 flex items-center gap-2">
          {/* AI Inference Telemetry Pill */}
          {webcam.status === "active" && (
            <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-md bg-black/75 backdrop-blur-md border border-white/20 text-xs font-mono shadow-md text-slate-300">
              <Cpu className="w-3.5 h-3.5 text-blue-400" />
              <span>YOLOv8: <strong className="text-emerald-400">{inferenceMs}ms</strong></span>
              <span className="text-slate-600">|</span>
              <span>DETECTED: <strong className="text-slate-100">{detections.length}</strong></span>
            </div>
          )}

          {/* Live Webcam Status Pill */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-black/75 backdrop-blur-md border border-white/20 text-xs font-mono shadow-md">
            <span
              className={`w-2 h-2 rounded-full ${
                webcam.status === "active"
                  ? "bg-emerald-500 animate-pulse"
                  : webcam.status === "requesting"
                  ? "bg-amber-500 animate-ping"
                  : "bg-red-500"
              }`}
            />
            <span className="text-[11px] font-bold text-slate-200 uppercase tracking-wider">
              {webcam.status === "active"
                ? "REAL WEBCAM LIVE"
                : webcam.status === "requesting"
                ? "INITIALIZING..."
                : webcam.status === "paused"
                ? "PAUSED"
                : "OFFLINE"}
            </span>
            {webcam.status === "active" && webcam.resolution.width > 0 && (
              <span className="text-[10px] text-slate-400 pl-1 border-l border-white/10 hidden md:inline">
                {webcam.resolution.width}x{webcam.resolution.height}
              </span>
            )}
          </div>

          {/* Toggle Webcam Power / Mute Video Button */}
          <button
            onClick={webcam.toggleWebcam}
            className={`p-1.5 rounded-md backdrop-blur-md border transition text-xs font-mono flex items-center gap-1 ${
              webcam.status === "active"
                ? "bg-emerald-950/70 border-emerald-500/50 text-emerald-300 hover:bg-emerald-900/80"
                : "bg-surface-200/80 border-white/20 text-slate-300 hover:bg-surface-100"
            }`}
            title={webcam.status === "active" ? "Pause Webcam Feed" : "Start Webcam Feed"}
          >
            {webcam.status === "active" ? <Video className="w-3.5 h-3.5" /> : <VideoOff className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Bottom-Left Overlaid Tactical Heatmap Matrix */}
        <div className="absolute bottom-4 left-4 z-20 p-1.5 rounded bg-black/80 backdrop-blur-md border border-white/20 shadow-lg">
          <div className="flex flex-col gap-0.5">
            {heatmapGrid.map((row, rIdx) => (
              <div key={rIdx} className="flex gap-0.5">
                {row.map((color, cIdx) => (
                  <div
                    key={cIdx}
                    style={{ backgroundColor: color }}
                    className="w-2.5 h-2 rounded-[1px] opacity-80"
                  />
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Fullscreen Button */}
        <button
          onClick={toggleFullscreen}
          className="absolute bottom-3 right-3 z-20 p-1.5 rounded bg-black/60 hover:bg-black/90 border border-white/20 text-slate-300 hover:text-white transition"
          title="Toggle Fullscreen"
        >
          <Maximize2 className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Embedded Tactical Controls Bar */}
      <CameraControls />
    </div>
  );
};
