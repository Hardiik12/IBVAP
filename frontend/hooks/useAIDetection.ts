"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { AIDetectionItem } from "../types/detection";
import { Zone } from "../types/zone";
import { aiDetectionService } from "../services/aiDetectionService";

interface UseAIDetectionOptions {
  videoRef: React.RefObject<HTMLVideoElement>;
  isEnabled?: boolean;
  zones?: Zone[];
  cameraId?: string;
  confidenceThreshold?: number;
  intervalMs?: number;
  onIntrusion?: (item: AIDetectionItem) => void;
}

export function useAIDetection(options: UseAIDetectionOptions) {
  const {
    videoRef,
    isEnabled = true,
    zones = [],
    cameraId = "cam-01",
    confidenceThreshold = 0.3,
    intervalMs = 120, // ~8 FPS inference rate
    onIntrusion,
  } = options;

  const [detections, setDetections] = useState<AIDetectionItem[]>([]);
  const [inferenceMs, setInferenceMs] = useState<number>(0);
  const [aiFps, setAiFps] = useState<number>(0);
  const [isInferring, setIsInferring] = useState<boolean>(false);

  const isBusyRef = useRef<boolean>(false);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const prevInsideTracksRef = useRef<Set<number>>(new Set());
  const frameCountRef = useRef<number>(0);
  const lastFpsCalcRef = useRef<number>(Date.now());

  // Capture video frame into base64 JPEG
  const grabFrameBase64 = useCallback((): string | null => {
    const video = videoRef.current;
    if (!video || video.readyState < 2 || video.videoWidth === 0 || video.videoHeight === 0) {
      return null;
    }

    if (!canvasRef.current) {
      canvasRef.current = document.createElement("canvas");
    }

    const canvas = canvasRef.current;
    // Scale down to 640px width for low latency inference transfer
    const targetWidth = Math.min(640, video.videoWidth);
    const scale = targetWidth / video.videoWidth;
    const targetHeight = Math.round(video.videoHeight * scale);

    canvas.width = targetWidth;
    canvas.height = targetHeight;

    const ctx = canvas.getContext("2d");
    if (!ctx) return null;

    ctx.drawImage(video, 0, 0, targetWidth, targetHeight);
    return canvas.toDataURL("image/jpeg", 0.7);
  }, [videoRef]);

  // Main inference step
  const processFrame = useCallback(async () => {
    if (!isEnabled || isBusyRef.current) return;

    const b64Image = grabFrameBase64();
    if (!b64Image) return;

    isBusyRef.current = true;
    setIsInferring(true);

    try {
      const response = await aiDetectionService.detectFrame({
        image: b64Image,
        cameraId,
        confidenceThreshold,
        zones,
      });

      setDetections(response.detections);
      setInferenceMs(response.inference_ms);

      // Track FPS
      frameCountRef.current += 1;
      const now = Date.now();
      const elapsed = (now - lastFpsCalcRef.current) / 1000;
      if (elapsed >= 1.0) {
        setAiFps(Number((frameCountRef.current / elapsed).toFixed(1)));
        frameCountRef.current = 0;
        lastFpsCalcRef.current = now;
      }

      // Check for new intrusion transitions
      const currentInside = new Set<number>();
      for (const item of response.detections) {
        if (item.is_inside_zone) {
          currentInside.add(item.track_id);
          // If newly entered zone, fire intrusion alert
          if (!prevInsideTracksRef.current.has(item.track_id)) {
            if (onIntrusion) {
              onIntrusion(item);
            }
          }
        }
      }
      prevInsideTracksRef.current = currentInside;
    } catch {
      // Network or inference skip
    } finally {
      isBusyRef.current = false;
      setIsInferring(false);
    }
  }, [isEnabled, grabFrameBase64, cameraId, confidenceThreshold, zones, onIntrusion]);

  // Inference interval loop
  useEffect(() => {
    if (!isEnabled) {
      setDetections([]);
      return;
    }

    const intervalId = setInterval(processFrame, intervalMs);
    return () => clearInterval(intervalId);
  }, [isEnabled, intervalMs, processFrame]);

  return {
    detections,
    inferenceMs,
    aiFps,
    isInferring,
  };
}
