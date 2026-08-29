"use client";

import React, { useRef, useEffect } from "react";
import { Zone } from "../../types/zone";
import { WebSocketAlertMessage } from "../../types/alert";
import { AIDetectionItem } from "../../types/detection";
import {
  clearCanvas,
  drawViewportGreenReticles,
  drawVirtualFenceLine,
  drawPolygonZone,
  drawTacticalIntruderBox,
} from "../../utils/canvas";

interface CanvasOverlayProps {
  zones: Zone[];
  activeAlert: WebSocketAlertMessage | null;
  detections?: AIDetectionItem[];
  showZones: boolean;
  showBoundingBoxes: boolean;
  showHud: boolean;
  cameraId: string;
}

export const CanvasOverlay: React.FC<CanvasOverlayProps> = ({
  zones,
  activeAlert,
  detections = [],
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

      // 1. Draw 4 Green Viewport Corner Reticles
      if (showHud) {
        drawViewportGreenReticles(ctx, width, height);
      }

      // 2. Draw Configured Restricted Polygon Zones & Virtual Fence Line
      if (showZones) {
        if (zones && zones.length > 0) {
          zones.forEach((z) => {
            drawPolygonZone(
              ctx,
              {
                polygon: z.polygon,
                name: z.name,
                isAlertActive: !!activeAlert || detections.some((d) => d.is_inside_zone),
              },
              width,
              height
            );
          });
        }
        // Glowing Tactical Virtual Fence laser line
        const hasBreach = detections.some((d) => d.is_inside_zone) || !!activeAlert;
        drawVirtualFenceLine(ctx, width, height, hasBreach);
      }

      // 3. Draw REAL YOLOv8 Detections (Bounding Boxes + Labels + Track IDs + Ground Reference Points)
      if (showBoundingBoxes) {
        if (detections && detections.length > 0) {
          // Render each real detected object dynamically
          detections.forEach((item) => {
            drawTacticalIntruderBox(
              ctx,
              {
                x1: item.bbox[0],
                y1: item.bbox[1],
                x2: item.bbox[2],
                y2: item.bbox[3],
                className: item.class_name,
                confidence: item.confidence,
                trackId: item.track_id,
                isInsideZone: item.is_inside_zone,
                isNormalized: true,
              },
              width,
              height
            );
          });
        } else if (activeAlert && activeAlert.bbox) {
          // Fallback to active alert bounding box if present
          const bbox = activeAlert.bbox;
          drawTacticalIntruderBox(
            ctx,
            {
              x1: bbox[0],
              y1: bbox[1],
              x2: bbox[2],
              y2: bbox[3],
              className: activeAlert.class_name || "person",
              confidence: activeAlert.confidence || 0.92,
              trackId: activeAlert.track_id || 1,
              isInsideZone: true,
              isNormalized: true,
            },
            width,
            height
          );
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [zones, activeAlert, detections, showZones, showBoundingBoxes, showHud, cameraId]);

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
