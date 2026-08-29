"use client";

import { useState, useEffect, useRef, useCallback } from "react";

export type WebcamStatus =
  | "idle"
  | "requesting"
  | "active"
  | "paused"
  | "denied"
  | "not-found"
  | "error";

export interface UseWebcamOptions {
  autoStart?: boolean;
  idealWidth?: number;
  idealHeight?: number;
  facingMode?: "user" | "environment";
}

export interface UseWebcamReturn {
  videoRef: React.RefObject<HTMLVideoElement>;
  stream: MediaStream | null;
  status: WebcamStatus;
  errorMessage: string | null;
  resolution: { width: number; height: number };
  startWebcam: () => Promise<boolean>;
  stopWebcam: () => void;
  toggleWebcam: () => void;
  captureFrame: () => string | null;
}

export function useWebcam(options: UseWebcamOptions = {}): UseWebcamReturn {
  const {
    autoStart = true,
    idealWidth = 1280,
    idealHeight = 720,
    facingMode = "user",
  } = options;

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [stream, setStream] = useState<MediaStream | null>(null);
  const [status, setStatus] = useState<WebcamStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [resolution, setResolution] = useState({ width: 0, height: 0 });

  // Stop all media tracks and release hardware
  const stopWebcam = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch {
          // Ignore track stop errors
        }
      });
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setStream(null);
    setStatus("paused");
  }, []);

  // Request browser media stream
  const startWebcam = useCallback(async (): Promise<boolean> => {
    // Check if mediaDevices API is available
    if (typeof window === "undefined" || !navigator?.mediaDevices?.getUserMedia) {
      setStatus("error");
      setErrorMessage("MediaDevices API is not supported in this browser or context.");
      return false;
    }

    // Stop existing stream before starting a new one
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    setStatus("requesting");
    setErrorMessage(null);

    const primaryConstraints: MediaStreamConstraints = {
      audio: false,
      video: {
        width: { ideal: idealWidth },
        height: { ideal: idealHeight },
        facingMode: facingMode,
      },
    };

    const fallbackConstraints: MediaStreamConstraints = {
      audio: false,
      video: true,
    };

    let mediaStream: MediaStream | null = null;

    try {
      // First attempt with optimal resolution constraints
      mediaStream = await navigator.mediaDevices.getUserMedia(primaryConstraints);
    } catch (err: any) {
      // Fallback if overconstrained
      if (err.name === "OverconstrainedError" || err.name === "ConstraintNotSatisfiedError") {
        try {
          mediaStream = await navigator.mediaDevices.getUserMedia(fallbackConstraints);
        } catch (fallbackErr: any) {
          handleMediaError(fallbackErr);
          return false;
        }
      } else {
        handleMediaError(err);
        return false;
      }
    }

    if (!mediaStream) {
      setStatus("error");
      setErrorMessage("Failed to acquire camera stream.");
      return false;
    }

    streamRef.current = mediaStream;
    setStream(mediaStream);

    // Attach stream to video element
    if (videoRef.current) {
      videoRef.current.srcObject = mediaStream;
      videoRef.current.onloadedmetadata = () => {
        if (videoRef.current) {
          videoRef.current.play().catch(() => {
            // Autoplay policy fallback
          });
          setResolution({
            width: videoRef.current.videoWidth || idealWidth,
            height: videoRef.current.videoHeight || idealHeight,
          });
        }
      };
    }

    setStatus("active");
    return true;
  }, [idealWidth, idealHeight, facingMode]);

  // Error classifier for clear operational feedback
  const handleMediaError = (err: any) => {
    console.warn("Webcam access error:", err);
    if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
      setStatus("denied");
      setErrorMessage(
        "Camera access was denied by your browser. Please click the camera/lock icon in your address bar to allow camera access, then click 'Retry Hardware Access'."
      );
    } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
      setStatus("not-found");
      setErrorMessage(
        "No video camera device was detected on your MacBook. Please ensure your built-in FaceTime camera or USB webcam is connected."
      );
    } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
      setStatus("error");
      setErrorMessage(
        "Camera hardware is busy or locked by another macOS application (e.g., FaceTime, Zoom, Photo Booth). Please close competing apps and retry."
      );
    } else {
      setStatus("error");
      setErrorMessage(err.message || "An unknown error occurred while initializing webcam.");
    }
  };

  const toggleWebcam = useCallback(() => {
    if (status === "active") {
      stopWebcam();
    } else {
      startWebcam();
    }
  }, [status, startWebcam, stopWebcam]);

  // Frame capture utility for future AI Python Pipeline Integration
  const captureFrame = useCallback((): string | null => {
    if (!videoRef.current || status !== "active") return null;
    const video = videoRef.current;
    if (video.videoWidth === 0 || video.videoHeight === 0) return null;

    try {
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      if (!ctx) return null;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      return canvas.toDataURL("image/jpeg", 0.85);
    } catch {
      return null;
    }
  }, [status]);

  // Auto-start on mount and clean release on unmount
  useEffect(() => {
    if (autoStart) {
      startWebcam();
    }

    return () => {
      // Ensure all tracks are cleanly stopped and camera hardware is released
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => {
          try {
            track.stop();
          } catch {
            // Ignore track stop errors
          }
        });
        streamRef.current = null;
      }
    };
  }, [autoStart, startWebcam]);

  return {
    videoRef,
    stream,
    status,
    errorMessage,
    resolution,
    startWebcam,
    stopWebcam,
    toggleWebcam,
    captureFrame,
  };
}
