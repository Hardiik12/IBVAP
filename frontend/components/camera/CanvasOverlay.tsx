"use client";

import React, { useRef, useEffect } from "react";
import { Zone } from "../../types/zone";
import { WebSocketAlertMessage } from "../../types/alert";
import {
  clearCanvas,
  drawViewportGreenReticles,
  drawVirtualFenceLine,
  drawTacticalIntruderBox,
} from "../../utils/canvas";

interface CanvasOverlayProps {
  zones: Zone[];
  activeAlert: WebSocketAlertMessage | null;
  showZones: boolean;
  showBoundingBoxes: boolean;
  showHud: boolean;
  cameraId: string;
}

export const CanvasOverlay: React.FC<CanvasOverlayProps> = ({
  zones,
  activeAlert,
  showZones = true,
  showBoundingBoxes = true,
  showHud = true,
  cameraId,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;

    const render = () => {
      const width = canvas.width;
      const height = canvas.height;

      clearCanvas(ctx, width, height);

      // 1. Draw 4 Green Viewport Corner Reticles (as in image_2.png)
      if (showHud) {
        drawViewportGreenReticles(ctx, width, height);
      }

      // 2. Draw the angled glowing red "VIRTUAL FENCE ===" Laser Line
      if (showZones) {
        drawVirtualFenceLine(ctx, width, height, true);
      }

      // 3. Draw Intruder Red Target Box with Bounding Box ID Callout & Crosshair
      if (showBoundingBoxes) {
        drawTacticalIntruderBox(
          ctx,
          {
            x1: 0.38,
            y1: 0.28,
            x2: 0.51,
            y2: 0.76,
            trackId: activeAlert?.track_id || 1,
            isInsideZone: true,
            isNormalized: true,
          },
          width,
          height
        );
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [zones, activeAlert, showZones, showBoundingBoxes, showHud, cameraId]);

  useEffect(() => {
    const handleResize = () => {
      const canvas = canvasRef.current;
      if (canvas && canvas.parentElement) {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
      }
    };

    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none z-10"
    />
  );
};
