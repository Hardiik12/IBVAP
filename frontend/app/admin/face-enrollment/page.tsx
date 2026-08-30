"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import {
  Scan,
  Shield,
  ShieldCheck,
  Camera,
  CheckCircle2,
  AlertTriangle,
  ArrowLeft,
  RefreshCw,
  Sparkles,
  UserPlus,
} from "lucide-react";

export default function FaceEnrollmentPage() {
  const { enrollFace, pendingUsername, logout } = useAuth();
  const router = useRouter();

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [samples, setSamples] = useState<string[]>([]);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [cameraActive, setCameraActive] = useState<boolean>(false);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);

  const instructions = [
    "Look directly into the camera lens with neutral expression.",
    "Turn head slightly to the left / tilt upward.",
    "Turn head slightly to the right / smile naturally.",
  ];

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  }, []);

  const startCamera = useCallback(async () => {
    try {
      setErrorMessage(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: "user",
        },
        audio: false,
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setCameraActive(true);
      }
    } catch (err: any) {
      console.error("Camera access error:", err);
      setErrorMessage("CAMERA ACCESS REQUIRED — Please enable webcam permissions.");
    }
  }, []);

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, [startCamera, stopCamera]);

  const captureFrame = (): string | null => {
    if (!videoRef.current || !canvasRef.current) return null;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext("2d");
    if (!ctx) return null;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.95);
  };

  const handleTakeSample = () => {
    const frame = captureFrame();
    if (!frame) return;

    const newSamples = [...samples, frame];
    setSamples(newSamples);

    if (newSamples.length < 3) {
      setCurrentStep(newSamples.length);
    } else {
      // All 3 samples captured -> Submit enrollment
      submitEnrollment(newSamples);
    }
  };

  const submitEnrollment = async (collectedSamples: string[]) => {
    setIsProcessing(true);
    setErrorMessage(null);

    try {
      await enrollFace(collectedSamples);
      setIsCompleted(true);
      stopCamera();
    } catch (err: any) {
      console.error("Enrollment error:", err);
      setIsProcessing(false);
      setErrorMessage(
        err.response?.data?.error?.message ||
          "Enrollment failed: Unable to detect a clean single face in all samples. Please retry."
      );
      setSamples([]);
      setCurrentStep(0);
    }
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col items-center justify-center p-4 relative overflow-hidden font-sans select-none">
      {/* Tactical Grid Background */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a15_1px,transparent_1px),linear-gradient(to_bottom,#0f172a15_1px,transparent_1px)] bg-[size:4rem_4rem] pointer-events-none" />

      {/* Main Container */}
      <div className="relative z-10 w-full max-w-2xl bg-[#0b1120]/95 backdrop-blur-xl border border-cyan-900/40 rounded-2xl shadow-[0_0_50px_rgba(6,182,212,0.15)] overflow-hidden flex flex-col">
        {/* Header Bar */}
        <div className="px-6 py-4 border-b border-cyan-900/30 bg-slate-900/60 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-cyan-950/80 border border-cyan-500/40 rounded-lg">
              <UserPlus className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-widest text-cyan-400 uppercase font-mono">
                BIOMETRIC PROFILE ENROLLMENT
              </h1>
              <p className="text-xs text-slate-400">
                AUTHORIZED OPERATOR ENROLLMENT PROTOCOL
              </p>
            </div>
          </div>

          <span className="text-xs font-mono px-2.5 py-1 bg-cyan-950/80 border border-cyan-700/50 rounded-full text-cyan-300">
            SAMPLE {Math.min(samples.length + 1, 3)} / 3
          </span>
        </div>

        {/* Instructions Banner */}
        <div className="px-6 py-3 bg-cyan-950/20 border-b border-cyan-900/20 flex flex-col gap-1 text-xs text-slate-300">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-cyan-300">
              OPERATOR: {pendingUsername || "ADMIN"}
            </span>
            <span className="text-slate-400">MULTI-ANGLE 128-D FEATURE EXTRACTION</span>
          </div>
          <p className="text-[11px] text-slate-400">
            👉 {instructions[currentStep] || "Processing biometric profile..."}
          </p>
        </div>

        {/* Video & Scanner Area */}
        <div className="p-6 flex flex-col items-center">
          <div className="relative w-full max-w-md aspect-[4/3] bg-black rounded-xl overflow-hidden border-2 border-cyan-900/60 flex items-center justify-center">
            <video
              ref={videoRef}
              playsInline
              muted
              className="w-full h-full object-cover transform -scale-x-100"
            />
            <canvas ref={canvasRef} className="hidden" />

            {/* Target Reticle */}
            <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
              <div className="w-52 h-68 rounded-[48%] border-2 border-dashed border-cyan-400/70 shadow-[0_0_20px_rgba(6,182,212,0.3)] animate-pulse" />
              <div className="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-cyan-400" />
              <div className="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-cyan-400" />
              <div className="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-cyan-400" />
              <div className="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-cyan-400" />
            </div>

            {/* Completed Overlay */}
            {isCompleted && (
              <div className="absolute inset-0 bg-emerald-950/90 backdrop-blur-sm flex flex-col items-center justify-center gap-3 animate-in fade-in">
                <ShieldCheck className="w-14 h-14 text-emerald-400" />
                <h3 className="text-lg font-bold font-mono tracking-widest text-emerald-400">
                  ENROLLMENT COMPLETE
                </h3>
                <p className="text-xs text-emerald-200">
                  REFERENCE BIOMETRIC PROFILE PERSISTED SECURELY
                </p>
              </div>
            )}
          </div>

          {/* Sample Progress Thumbnails */}
          <div className="w-full max-w-md mt-4 flex items-center justify-between gap-3">
            {[0, 1, 2].map((idx) => (
              <div
                key={idx}
                className={`flex-1 h-12 rounded-lg border flex items-center justify-center text-xs font-mono transition ${
                  samples[idx]
                    ? "bg-emerald-950/60 border-emerald-500/60 text-emerald-300"
                    : idx === currentStep
                    ? "bg-cyan-950/60 border-cyan-500/60 text-cyan-300 animate-pulse"
                    : "bg-slate-900/60 border-slate-800 text-slate-500"
                }`}
              >
                {samples[idx] ? (
                  <span className="flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    SAMPLE {idx + 1}
                  </span>
                ) : (
                  <span>SAMPLE {idx + 1}</span>
                )}
              </div>
            ))}
          </div>

          {/* Error Message Display */}
          {errorMessage && (
            <div className="w-full max-w-md mt-4 p-3 rounded-xl bg-red-950/50 border border-red-500/40 text-red-300 text-xs font-mono flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="w-full max-w-md mt-6 flex items-center justify-between gap-4">
            <button
              onClick={() => {
                stopCamera();
                router.push("/face-verification");
              }}
              type="button"
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white text-xs font-semibold flex items-center gap-2 transition"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Verify
            </button>

            <button
              onClick={handleTakeSample}
              disabled={isProcessing || isCompleted || !cameraActive}
              type="button"
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 text-white text-xs font-bold font-mono tracking-wider uppercase shadow-[0_0_20px_rgba(6,182,212,0.4)] flex items-center gap-2 transition"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Generating Vector...
                </>
              ) : (
                <>
                  <Camera className="w-4 h-4" />
                  Capture Sample {samples.length + 1}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
