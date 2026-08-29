"use client";

import React, { useRef, useState } from "react";
import { CanvasOverlay } from "./CanvasOverlay";
import { useCameraContext } from "../../context/CameraContext";
import { useAlerts } from "../../hooks/useAlerts";
import { Maximize2, ShieldAlert } from "lucide-react";

export const LiveVideoPlayer: React.FC = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const { selectedCamera, zones, showZones, showBoundingBoxes, showHud } = useCameraContext();
  const { latestAlert } = useAlerts();

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

  // Sample Heatmap 10x10 Matrix colors (Green / Yellow / Red / Blue / Purple)
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
        {/* Background Thermal Infrared Video / Footage Image */}
        <img
          src="/surveillance-bg.jpg"
          alt="Thermal Surveillance Feed"
          className="absolute inset-0 w-full h-full object-cover select-none filter contrast-125 brightness-90"
        />

        {/* Tactical Scanlines */}
        <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-25 pointer-events-none z-10" />

        {/* Live Canvas Overlay (Corner Reticles, Virtual Fence, Red Target BBox) */}
        <CanvasOverlay
          zones={zones}
          activeAlert={latestAlert}
          showZones={showZones}
          showBoundingBoxes={showBoundingBoxes}
          showHud={showHud}
          cameraId={selectedCamera?.id || "cam-01"}
        />

        {/* Bottom-Left Overlaid Tactical Heatmap Matrix (as seen in image_2.png) */}
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
    </div>
  );
};
