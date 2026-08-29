"use client";

import React from "react";
import { Camera, CameraOff, AlertTriangle, RefreshCw, Play, ShieldAlert } from "lucide-react";
import { Button } from "../ui/Button";
import { UseWebcamReturn } from "../../hooks/useWebcam";

interface WebcamFeedProps {
  webcam: UseWebcamReturn;
  cameraName?: string;
}

export const WebcamFeed: React.FC<WebcamFeedProps> = ({ webcam, cameraName = "MacBook Built-in FaceTime / USB Webcam" }) => {
  const { videoRef, status, errorMessage, startWebcam, toggleWebcam, resolution } = webcam;

  return (
    <div className="relative w-full h-full bg-slate-950 flex items-center justify-center overflow-hidden">
      {/* HTML5 Live Video Element */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className={`absolute inset-0 w-full h-full object-cover select-none transition-opacity duration-300 ${
          status === "active" ? "opacity-100" : "opacity-0 pointer-events-none"
        }`}
      />

      {/* 1. Requesting / Initializing Hardware State */}
      {status === "requesting" && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center p-6 text-center bg-black/90 backdrop-blur-sm">
          <div className="relative mb-4">
            <div className="w-14 h-14 rounded-full border-2 border-blue-500/20 border-t-blue-400 animate-spin" />
            <Camera className="w-6 h-6 text-blue-400 absolute inset-0 m-auto animate-pulse" />
          </div>
          <p className="text-sm font-bold font-mono text-slate-100 tracking-wider">
            INITIALIZING LIVE WEBCAM FEED
          </p>
          <p className="text-xs font-mono text-slate-400 mt-1 max-w-sm">
            Requesting browser video hardware permissions for live perimeter monitoring...
          </p>
        </div>
      )}

      {/* 2. Permission Denied State */}
      {status === "denied" && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center p-6 text-center bg-slate-950/95">
          <div className="w-12 h-12 rounded-xl bg-amber-950/60 border border-amber-600/50 flex items-center justify-center mb-3 text-amber-400 shadow-lg">
            <CameraOff className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold font-mono text-amber-300 uppercase tracking-wide">
            Camera Permission Denied
          </h3>
          <p className="text-xs font-mono text-slate-300 mt-2 max-w-md leading-relaxed">
            {errorMessage ||
              "Browser blocked camera access. Please allow camera permissions in your address bar (lock/camera icon) to view your MacBook webcam."}
          </p>

          <div className="mt-4 flex items-center gap-3">
            <Button
              size="sm"
              variant="primary"
              onClick={() => startWebcam()}
              leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
              className="bg-amber-600 hover:bg-amber-500 text-white font-mono text-xs"
            >
              Retry Camera Access
            </Button>
          </div>
        </div>
      )}

      {/* 3. Camera Hardware Not Found / Error State */}
      {(status === "not-found" || status === "error") && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center p-6 text-center bg-slate-950/95">
          <div className="w-12 h-12 rounded-xl bg-red-950/60 border border-red-600/50 flex items-center justify-center mb-3 text-red-400 shadow-lg">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold font-mono text-red-300 uppercase tracking-wide">
            {status === "not-found" ? "No Camera Detected" : "Hardware Stream Error"}
          </h3>
          <p className="text-xs font-mono text-slate-300 mt-2 max-w-md leading-relaxed">
            {errorMessage || "Unable to acquire video stream from connected camera hardware."}
          </p>

          <div className="mt-4 flex items-center gap-3">
            <Button
              size="sm"
              variant="secondary"
              onClick={() => startWebcam()}
              leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
              className="font-mono text-xs"
            >
              Retry Hardware Check
            </Button>
          </div>
        </div>
      )}

      {/* 4. Paused / Standby State */}
      {status === "paused" && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center p-6 text-center bg-black/90">
          <div className="w-12 h-12 rounded-xl bg-surface-200 border border-white/10 flex items-center justify-center mb-3 text-slate-400">
            <CameraOff className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold font-mono text-slate-200 uppercase tracking-wide">
            Surveillance Stream Paused
          </h3>
          <p className="text-xs font-mono text-slate-400 mt-1 max-w-sm">
            Webcam hardware released. Click resume to restore live video feed.
          </p>
          <div className="mt-4">
            <Button
              size="sm"
              variant="primary"
              onClick={() => toggleWebcam()}
              leftIcon={<Play className="w-3.5 h-3.5" />}
              className="font-mono text-xs"
            >
              Resume Live Feed
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
