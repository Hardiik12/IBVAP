"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { AIDetectionItem } from "../types/detection";
import { Zone } from "../types/zone";
import { EvidenceRecord } from "../types/evidence";
import { aiDetectionService } from "../services/aiDetectionService";
import { evidenceService } from "../services/evidenceService";

interface UseAIDetectionOptions {
  videoRef: React.RefObject<HTMLVideoElement>;
  isEnabled?: boolean;
  zones?: Zone[];
  cameraId?: string;
  confidenceThreshold?: number;
  intervalMs?: number;
  onIntrusion?: (item: AIDetectionItem, evidence: EvidenceRecord) => void;
}

export function useAIDetection(options: UseAIDetectionOptions) {
  const {
    videoRef,
    isEnabled = true,
    zones = [],
    cameraId = "cam-01",
    confidenceThreshold = 0.3,
    intervalMs = 130, // ~7-8 FPS continuous inference stream
    onIntrusion,
  } = options;

  const [detections, setDetections] = useState<AIDetectionItem[]>([]);
  const [inferenceMs, setInferenceMs] = useState<number>(0);
  const [aiFps, setAiFps] = useState<number>(0);
  const [isInferring, setIsInferring] = useState<boolean>(false);

  const isBusyRef = useRef<boolean>(false);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const highResCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const prevInsideTracksRef = useRef<Set<number>>(new Set());
  const frameCountRef = useRef<number>(0);
  const lastFpsCalcRef = useRef<number>(Date.now());

  // Capture lightweight frame (640px) for fast inference transfer
  const grabInferenceFrame = useCallback((): string | null => {
    const video = videoRef.current;
    if (!video || video.readyState < 2 || video.videoWidth === 0 || video.videoHeight === 0) {
      return null;
    }

    if (!canvasRef.current) {
      canvasRef.current = document.createElement("canvas");
    }

    const canvas = canvasRef.current;
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

  // Capture full-resolution raw snapshot for forensic evidence storage & SHA-256 hashing
  const grabHighResEvidenceFrame = useCallback((): string | null => {
    const video = videoRef.current;
    if (!video || video.readyState < 2 || video.videoWidth === 0 || video.videoHeight === 0) {
      return null;
    }

    if (!highResCanvasRef.current) {
      highResCanvasRef.current = document.createElement("canvas");
    }

    const canvas = highResCanvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    if (!ctx) return null;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.9);
  }, [videoRef]);

  // Main inference step
  const processFrame = useCallback(async () => {
    if (!isEnabled || isBusyRef.current) return;

    const b64Image = grabInferenceFrame();
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

      // Compute FPS
      frameCountRef.current += 1;
      const now = Date.now();
      const elapsed = (now - lastFpsCalcRef.current) / 1000;
      if (elapsed >= 1.0) {
        setAiFps(Number((frameCountRef.current / elapsed).toFixed(1)));
        frameCountRef.current = 0;
        lastFpsCalcRef.current = now;
      }

      // Check for POSITIVE transition: OUTSIDE -> INSIDE
      const currentInside = new Set<number>();
      for (const item of response.detections) {
        if (item.is_inside_zone) {
          currentInside.add(item.track_id);

          // If subject just breached the zone edge:
          if (!prevInsideTracksRef.current.has(item.track_id)) {
            // 1. Immediately capture the current raw webcam frame at this exact moment
            const evidenceSnapshot = grabHighResEvidenceFrame();
            if (evidenceSnapshot) {
              try {
                // 2. Ingest real evidence snapshot to backend and compute real SHA-256 hash
                const evidenceRecord = await evidenceService.captureRealEvidence({
                  image: evidenceSnapshot,
                  camera_id: cameraId,
                  zone_id: item.zone_id,
                  zone_name: item.zone_name,
                  track_id: item.track_id,
                  class_name: item.class_name,
                  confidence: item.confidence,
                  bbox: item.bbox,
                  timestamp: new Date().toISOString(),
                });

                // 3. Dispatch real intrusion alert with real evidence_id
                if (onIntrusion) {
                  onIntrusion(item, evidenceRecord);
                }
              } catch (err) {
                console.error("Failed to persist real intrusion evidence:", err);
              }
            }
          }
        }
      }
      prevInsideTracksRef.current = currentInside;
    } catch {
      // Skip dropped frame
    } finally {
      isBusyRef.current = false;
      setIsInferring(false);
    }
  }, [isEnabled, grabInferenceFrame, grabHighResEvidenceFrame, cameraId, confidenceThreshold, zones, onIntrusion]);

  // Inference loop
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
