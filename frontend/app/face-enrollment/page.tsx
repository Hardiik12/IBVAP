"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import {
  Scan,
  Shield,
  ShieldCheck,
  ShieldAlert,
  Camera,
  RefreshCw,
  ArrowLeft,
  Eye,
  AlertTriangle,
  UserCheck,
  Activity,
  CheckCircle2,
  Lock,
  Layers,
  ChevronRight,
} from "lucide-react";

type EnrollmentStep = 1 | 2 | 3;

interface StepPrompt {
  step: EnrollmentStep;
  title: string;
  instruction: string;
  hint: string;
}

const ENROLLMENT_STEPS: StepPrompt[] = [
  {
    step: 1,
    title: "SAMPLE 1/3: FRONTAL ALIGNMENT",
    instruction: "Look straight into the optical sensor.",
    hint: "Align face directly within the center scanning reticle.",
  },
  {
    step: 2,
    title: "SAMPLE 2/3: ANGULAR VARIATION (LEFT)",
    instruction: "Slightly tilt your head to the left (~15°).",
    hint: "Helps the SFace neural engine extract lateral biometric features.",
  },
  {
    step: 3,
    title: "SAMPLE 3/3: ANGULAR VARIATION (RIGHT)",
    instruction: "Slightly tilt your head to the right (~15°).",
    hint: "Final sample for unit-normalized composite biometric vector.",
  },
];

export default function FaceEnrollmentPage() {
  const { enrollFace, pendingUsername, logout } = useAuth();
  const router = useRouter();

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [currentStep, setCurrentStep] = useState<EnrollmentStep>(1);
  const [capturedSamples, setCapturedSamples] = useState<string[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [isEnrolledSuccess, setIsEnrolledSuccess] = useState<boolean>(false);
  const [cameraReady, setCameraReady] = useState<boolean>(false);
  const [isCapturing, setIsCapturing] = useState<boolean>(false);

  // Stop camera media tracks cleanly
  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch (e) {
          console.error("Error stopping track:", e);
        }
      });
      streamRef.current = null;
    }
  }, []);

  // Request camera permission and start video stream
  const startCamera = useCallback(async () => {
    setErrorMessage(null);
    setIsEnrolledSuccess(false);
    setCameraReady(false);

    try {
      if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
        throw new Error("Webcam API not supported in this browser environment.");
      }

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
        setCameraReady(true);
      }
    } catch (err: any) {
      console.error("Camera access error:", err);
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        setErrorMessage("CAMERA ACCESS REQUIRED — Please allow webcam permissions in your browser.");
      } else {
        setErrorMessage("BIOMETRIC SENSOR UNAVAILABLE — " + (err.message || "Failed to initialize optical capture device."));
      }
    }
  }, []);

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, [startCamera, stopCamera]);

  // Capture video frame from canvas as base64 JPEG
  const captureFrame = (): string | null => {
    if (!videoRef.current || !canvasRef.current) return null;
    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext("2d");
    if (!ctx) return null;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.92);
  };

  // Handle capture sample button
  const handleCaptureSample = async () => {
    if (isCapturing || isProcessing || isEnrolledSuccess) return;
    setIsCapturing(true);
    setErrorMessage(null);

    const frameBase64 = captureFrame();
    if (!frameBase64) {
      setIsCapturing(false);
      setErrorMessage("OPTICAL CAPTURE FAILED — Unable to acquire frame from video sensor.");
      return;
    }

    const nextSamples = [...capturedSamples, frameBase64];
    setCapturedSamples(nextSamples);
    setIsCapturing(false);

    if (currentStep < 3) {
      setCurrentStep((prev) => (prev + 1) as EnrollmentStep);
    } else {
      // All 3 samples acquired, submit to backend for 128-d composite vector generation
      submitEnrollment(nextSamples);
    }
  };

  // Submit collected samples to backend
  const submitEnrollment = async (samplesToSubmit: string[]) => {
    setIsProcessing(true);
    setErrorMessage(null);

    try {
      await enrollFace(samplesToSubmit);
      setIsEnrolledSuccess(true);
      stopCamera();
    } catch (err: any) {
      console.error("Biometric enrollment error:", err);
      setIsProcessing(false);
      const detail = err.response?.data?.error?.message || err.message || "";
      if (detail.includes("NO_FACE_DETECTED") || detail.includes("ENROLLMENT_FAILED")) {
        setErrorMessage("ENROLLMENT FAILED — No clear face detected in one or more samples. Please retry.");
      } else if (detail.includes("MULTIPLE_FACES_DETECTED")) {
        setErrorMessage("MULTIPLE FACES DETECTED — Ensure only one operator is present during biometric capture.");
      } else {
        setErrorMessage("ENROLLMENT REJECTED — " + detail);
      }
      // Reset for re-capture
      setCapturedSamples([]);
      setCurrentStep(1);
    }
  };

  const handleReset = () => {
    setCapturedSamples([]);
    setCurrentStep(1);
    setErrorMessage(null);
    startCamera();
  };

  const currentPrompt = ENROLLMENT_STEPS[currentStep - 1];

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col items-center justify-center p-4 relative overflow-hidden font-sans select-none">
      {/* Tactical Background Grid & Ambient Glow */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a15_1px,transparent_1px),linear-gradient(to_bottom,#0f172a15_1px,transparent_1px)] bg-[size:4rem_4rem] pointer-events-none" />
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-950/25 blur-[130px] rounded-full pointer-events-none" />
      <div className="absolute bottom-10 right-10 w-[350px] h-[350px] bg-blue-950/20 blur-[100px] rounded-full pointer-events-none" />

      {/* Main Container */}
      <div className="relative z-10 w-full max-w-2xl bg-[#0b1120]/95 backdrop-blur-xl border border-cyan-900/40 rounded-2xl shadow-[0_0_50px_rgba(6,182,212,0.15)] overflow-hidden flex flex-col">
        
        {/* Header HUD Bar */}
        <div className="px-6 py-4 border-b border-cyan-900/30 bg-slate-900/60 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-cyan-950/80 border border-cyan-500/40 rounded-lg shadow-[0_0_15px_rgba(6,182,212,0.3)]">
              <Scan className="w-5 h-5 text-cyan-400 animate-pulse" />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-widest text-cyan-400 uppercase font-mono">
                FIRST-TIME BIOMETRIC ENROLLMENT
              </h1>
              <p className="text-xs text-slate-400">
                INITIALIZING FACIAL DESCRIPTOR EMBEDDING FOR OPERATOR: <strong className="text-cyan-300 uppercase">{pendingUsername || "ADMIN"}</strong>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="flex h-2.5 w-2.5 relative">
              <span
                className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                  isEnrolledSuccess ? "bg-emerald-400" : errorMessage ? "bg-red-400" : "bg-cyan-400"
                }`}
              />
              <span
                className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                  isEnrolledSuccess ? "bg-emerald-500" : errorMessage ? "bg-red-500" : "bg-cyan-500"
                }`}
              />
            </span>
            <span className="text-[11px] font-mono tracking-wider text-slate-300 uppercase">
              {isEnrolledSuccess ? "ENROLLED" : `SAMPLE ${currentStep}/3`}
            </span>
          </div>
        </div>

        {/* 3-Step Progress Header */}
        <div className="px-6 py-3 bg-slate-900/40 border-b border-cyan-900/20 grid grid-cols-3 gap-3 text-xs font-mono">
          {[1, 2, 3].map((stepNum) => (
            <div
              key={stepNum}
              className={`flex items-center gap-2 p-2 rounded-lg border transition-all ${
                currentStep === stepNum
                  ? "bg-cyan-950/60 border-cyan-500/60 text-cyan-300 shadow-[0_0_10px_rgba(6,182,212,0.2)]"
                  : capturedSamples.length >= stepNum
                  ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300"
                  : "bg-slate-950/40 border-slate-800 text-slate-500"
              }`}
            >
              <div
                className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                  capturedSamples.length >= stepNum
                    ? "bg-emerald-500 text-slate-950"
                    : currentStep === stepNum
                    ? "bg-cyan-500 text-slate-950"
                    : "bg-slate-800 text-slate-400"
                }`}
              >
                {capturedSamples.length >= stepNum ? "✓" : stepNum}
              </div>
              <span className="truncate text-[11px]">
                {stepNum === 1 ? "Frontal" : stepNum === 2 ? "Left Tilt" : "Right Tilt"}
              </span>
            </div>
          ))}
        </div>

        {/* Video Scanner Feed Area */}
        <div className="p-6 flex flex-col items-center">
          <div className="relative w-full max-w-md aspect-[4/3] bg-black rounded-xl overflow-hidden border-2 border-cyan-900/60 shadow-[inset_0_0_30px_rgba(0,0,0,0.8)] flex items-center justify-center">
            {/* Live Video Element */}
            <video
              ref={videoRef}
              playsInline
              muted
              className={`w-full h-full object-cover transform -scale-x-100 ${
                isEnrolledSuccess ? "opacity-75" : ""
              }`}
            />

            {/* Hidden Frame Grab Canvas */}
            <canvas ref={canvasRef} className="hidden" />

            {/* Futuristic Security Scanning Reticle Overlay */}
            <div className="absolute inset-0 pointer-events-none">
              {/* Corner Targeting Brackets */}
              <div className="absolute top-4 left-4 w-8 h-8 border-t-2 border-l-2 border-cyan-400/80" />
              <div className="absolute top-4 right-4 w-8 h-8 border-t-2 border-r-2 border-cyan-400/80" />
              <div className="absolute bottom-4 left-4 w-8 h-8 border-b-2 border-l-2 border-cyan-400/80" />
              <div className="absolute bottom-4 right-4 w-8 h-8 border-b-2 border-r-2 border-cyan-400/80" />

              {/* Facial Oval Positioning Reticle */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div
                  className={`w-52 h-68 rounded-[48%] border-2 transition-all duration-300 ${
                    isEnrolledSuccess
                      ? "border-emerald-400 shadow-[0_0_30px_rgba(16,185,129,0.6)] bg-emerald-500/10"
                      : errorMessage
                      ? "border-red-500 shadow-[0_0_25px_rgba(239,68,68,0.4)] bg-red-500/10"
                      : "border-cyan-400/70 shadow-[0_0_20px_rgba(6,182,212,0.35)] border-dashed animate-pulse"
                  }`}
                />
              </div>

              {/* Sweeping Laser Line when processing */}
              {isProcessing && !isEnrolledSuccess && (
                <div className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_15px_#06b6d4] animate-bounce" />
              )}

              {/* Real-time Stage HUD Overlay */}
              <div className="absolute top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-black/75 backdrop-blur-md rounded border border-cyan-500/30 text-[10px] font-mono tracking-widest text-cyan-300 uppercase">
                {isProcessing
                  ? "GENERATING COMPOSITE 128-D DESCRIPTOR..."
                  : currentPrompt.title}
              </div>
            </div>

            {/* Access Granted / Enrolled Overlay */}
            {isEnrolledSuccess && (
              <div className="absolute inset-0 bg-emerald-950/85 backdrop-blur-sm flex flex-col items-center justify-center gap-3 animate-in fade-in duration-300">
                <div className="p-3 bg-emerald-500/20 border border-emerald-400 rounded-full shadow-[0_0_30px_rgba(16,185,129,0.6)]">
                  <ShieldCheck className="w-12 h-12 text-emerald-400 animate-bounce" />
                </div>
                <h3 className="text-lg font-bold font-mono tracking-widest text-emerald-400">
                  BIOMETRIC PROFILE ENROLLED
                </h3>
                <p className="text-xs text-emerald-200">
                  VECTOR PERSISTED ➔ OPENING DASHBOARD...
                </p>
              </div>
            )}
          </div>

          {/* Current Step Instruction Banner */}
          <div className="w-full mt-4 p-3 rounded-xl bg-cyan-950/30 border border-cyan-800/40 text-center font-mono">
            <p className="text-xs text-cyan-300 font-semibold">{currentPrompt.instruction}</p>
            <p className="text-[11px] text-slate-400 mt-0.5">{currentPrompt.hint}</p>
          </div>

          {/* Status Message and Error Notification */}
          {errorMessage && (
            <div className="w-full mt-3 p-3 rounded-xl bg-red-950/50 border border-red-500/40 text-red-300 text-xs font-mono flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Security Disclaimer Note */}
          <p className="mt-3 text-[11px] text-slate-400 text-center flex items-center justify-center gap-1.5">
            <Shield className="w-3 h-3 text-cyan-500" />
            Biometric embeddings are unit-normalized 128-d vectors. Raw camera images are not stored to disk.
          </p>

          {/* Action Buttons */}
          <div className="w-full mt-6 flex items-center justify-between gap-4">
            <button
              onClick={() => {
                stopCamera();
                logout();
              }}
              type="button"
              className="px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-300 hover:text-white text-xs font-semibold flex items-center gap-2 transition cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4" />
              Cancel / Exit
            </button>

            <div className="flex items-center gap-3">
              {capturedSamples.length > 0 && !isEnrolledSuccess && (
                <button
                  onClick={handleReset}
                  type="button"
                  className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-2 transition cursor-pointer"
                >
                  <RefreshCw className="w-4 h-4" />
                  Reset Samples
                </button>
              )}

              <button
                onClick={handleCaptureSample}
                disabled={isCapturing || isProcessing || isEnrolledSuccess || !cameraReady}
                type="button"
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 text-white text-xs font-bold font-mono tracking-wider uppercase shadow-[0_0_20px_rgba(6,182,212,0.4)] flex items-center gap-2 transition cursor-pointer"
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Enrolling Vector...
                  </>
                ) : (
                  <>
                    <Camera className="w-4 h-4" />
                    Capture Sample {currentStep}/3
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
