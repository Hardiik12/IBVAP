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
} from "lucide-react";

type BiometricStage =
  | "INITIALIZING CAMERA..."
  | "SCANNING FACE..."
  | "FACE DETECTED"
  | "VERIFYING BIOMETRIC SIGNATURE..."
  | "ACCESS GRANTED"
  | "ACCESS DENIED";

export default function FaceVerificationPage() {
  const { verifyFace, pendingUsername, isFaceEnrolled, logout } = useAuth();
  const router = useRouter();

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [stage, setStage] = useState<BiometricStage>("INITIALIZING CAMERA...");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [isAccessGranted, setIsAccessGranted] = useState<boolean>(false);
  const [cameraReady, setCameraReady] = useState<boolean>(false);
  const [faceDetected, setFaceDetected] = useState<boolean>(false);

  // Stop camera media tracks cleanly when navigating away
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
    setStage("INITIALIZING CAMERA...");
    setErrorMessage(null);
    setIsAccessGranted(false);
    setCameraReady(false);
    setFaceDetected(false);

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
        setStage("SCANNING FACE...");
      }
    } catch (err: any) {
      console.error("Camera access error:", err);
      setStage("ACCESS DENIED");
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

  // Perform live biometric verification
  const handleVerify = async () => {
    if (isProcessing || isAccessGranted) return;
    setIsProcessing(true);
    setErrorMessage(null);
    setStage("VERIFYING BIOMETRIC SIGNATURE...");

    const frameBase64 = captureFrame();
    if (!frameBase64) {
      setIsProcessing(false);
      setStage("ACCESS DENIED");
      setErrorMessage("NO OPTICAL SIGNAL — Unable to capture frame from webcam stream.");
      return;
    }

    try {
      await verifyFace(frameBase64, true);
      setStage("ACCESS GRANTED");
      setIsAccessGranted(true);
      stopCamera();
    } catch (err: any) {
      console.error("Biometric verification error:", err);
      setIsProcessing(false);
      setStage("ACCESS DENIED");

      const detail = err.response?.data?.error?.message || err.message || "";
      if (detail.includes("NO_FACE_DETECTED")) {
        setErrorMessage("NO FACE DETECTED — Position your face clearly inside the scanner reticle.");
      } else if (detail.includes("MULTIPLE_FACES_DETECTED")) {
        setErrorMessage("MULTIPLE FACES DETECTED — Only one operator may be present.");
      } else if (detail.includes("NO_ENROLLED_PROFILE")) {
        setErrorMessage("NO ENROLLED PROFILE FOUND — Please complete initial biometric enrollment.");
      } else {
        setErrorMessage("BIOMETRIC MISMATCH — ACCESS DENIED");
      }
    }
  };

  // Automated face presence detection transition
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (cameraReady && !isProcessing && !isAccessGranted && stage === "SCANNING FACE...") {
      timer = setTimeout(() => {
        setFaceDetected(true);
        setStage("FACE DETECTED");
        // Auto-initiate verification scan
        setTimeout(() => {
          handleVerify();
        }, 1200);
      }, 1000);
    }
    return () => clearTimeout(timer);
  }, [cameraReady, stage, isProcessing, isAccessGranted]);

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
                BIOMETRIC IDENTITY VERIFICATION
              </h1>
              <p className="text-xs text-slate-400">
                STAGE 3 // 1:1 FACIAL BIOMETRIC MATCHING
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="flex h-2.5 w-2.5 relative">
              <span
                className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                  isAccessGranted ? "bg-emerald-400" : errorMessage ? "bg-red-400" : "bg-cyan-400"
                }`}
              />
              <span
                className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                  isAccessGranted ? "bg-emerald-500" : errorMessage ? "bg-red-500" : "bg-cyan-500"
                }`}
              />
            </span>
            <span className="text-[11px] font-mono tracking-wider text-slate-300 uppercase">
              {isAccessGranted ? "AUTHORIZED" : errorMessage ? "DENIED" : "ACTIVE"}
            </span>
          </div>
        </div>

        {/* Subtitle Banner */}
        <div className="px-6 py-3 bg-cyan-950/20 border-b border-cyan-900/20 flex items-center justify-between text-xs text-slate-300">
          <span>
            Target Operator: <strong className="text-cyan-300 uppercase font-mono">{pendingUsername || "ADMIN"}</strong>
          </span>
          <span className="text-slate-400 text-[11px]">
            {isFaceEnrolled ? "ENROLLED REFERENCE DETECTED" : "FIRST-TIME ENROLLMENT ACTIVE"}
          </span>
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
                isAccessGranted ? "opacity-75" : ""
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
                    isAccessGranted
                      ? "border-emerald-400 shadow-[0_0_30px_rgba(16,185,129,0.6)] bg-emerald-500/10"
                      : errorMessage
                      ? "border-red-500 shadow-[0_0_25px_rgba(239,68,68,0.4)] bg-red-500/10"
                      : "border-cyan-400/70 shadow-[0_0_20px_rgba(6,182,212,0.35)] border-dashed animate-pulse"
                  }`}
                />
              </div>

              {/* Sweeping Laser Line when processing */}
              {isProcessing && !isAccessGranted && (
                <div className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_15px_#06b6d4] animate-bounce" />
              )}

              {/* Real-time Stage HUD Overlay */}
              <div className="absolute top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-black/75 backdrop-blur-md rounded border border-cyan-500/30 text-[10px] font-mono tracking-widest text-cyan-300 uppercase">
                {stage}
              </div>
            </div>

            {/* Access Granted Overlay */}
            {isAccessGranted && (
              <div className="absolute inset-0 bg-emerald-950/85 backdrop-blur-sm flex flex-col items-center justify-center gap-3 animate-in fade-in duration-300">
                <div className="p-3 bg-emerald-500/20 border border-emerald-400 rounded-full shadow-[0_0_30px_rgba(16,185,129,0.6)]">
                  <ShieldCheck className="w-12 h-12 text-emerald-400 animate-bounce" />
                </div>
                <h3 className="text-lg font-bold font-mono tracking-widest text-emerald-400">
                  IDENTITY VERIFIED — ACCESS GRANTED
                </h3>
                <p className="text-xs text-emerald-200">
                  AUTHENTICATION COMPLETE ➔ OPENING DASHBOARD...
                </p>
              </div>
            )}
          </div>

          {/* Status Message and Error Notification */}
          <div className="w-full mt-5">
            <div
              className={`p-3.5 rounded-xl border text-xs font-mono flex items-center justify-between ${
                isAccessGranted
                  ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300"
                  : errorMessage
                  ? "bg-red-950/50 border-red-500/40 text-red-300 shadow-[0_0_15px_rgba(239,68,68,0.2)]"
                  : "bg-slate-900/60 border-cyan-900/40 text-cyan-300"
              }`}
            >
              <div className="flex items-center gap-2.5">
                {isAccessGranted ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : errorMessage ? (
                  <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
                ) : (
                  <Activity className="w-4 h-4 text-cyan-400 shrink-0 animate-spin" />
                )}
                <span className="font-semibold tracking-wide">
                  {errorMessage || stage}
                </span>
              </div>

              <span className="text-[10px] text-slate-400 uppercase bg-slate-800/60 px-2 py-0.5 rounded border border-slate-700">
                SFace 128-D
              </span>
            </div>

            {/* Security Disclaimer Note */}
            <p className="mt-2 text-[11px] text-slate-400 text-center flex items-center justify-center gap-1.5">
              <Shield className="w-3 h-3 text-cyan-500" />
              Prototype-level biometric verification demo. Facial vectors are evaluated for 1:1 match against enrolled profile.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="w-full mt-6 flex items-center justify-between gap-4">
            <button
              onClick={() => {
                stopCamera();
                logout();
              }}
              type="button"
              className="px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-300 hover:text-white text-xs font-semibold flex items-center gap-2 transition"
            >
              <ArrowLeft className="w-4 h-4" />
              Cancel / Return to Login
            </button>

            <div className="flex items-center gap-3">
              {errorMessage && (
                <button
                  onClick={() => {
                    startCamera();
                  }}
                  type="button"
                  className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-cyan-500/40 text-cyan-300 text-xs font-semibold flex items-center gap-2 transition"
                >
                  <RefreshCw className="w-4 h-4" />
                  Retry Biometric Scan
                </button>
              )}

              <button
                onClick={handleVerify}
                disabled={isProcessing || isAccessGranted || !cameraReady}
                type="button"
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 text-white text-xs font-bold font-mono tracking-wider uppercase shadow-[0_0_20px_rgba(6,182,212,0.4)] flex items-center gap-2 transition cursor-pointer"
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  <>
                    <UserCheck className="w-4 h-4" />
                    Verify Biometrics
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Biometric Enrollment Link */}
          <div className="w-full mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Need to update or re-enroll biometric reference?</span>
            <button
              onClick={() => {
                stopCamera();
                router.push("/admin/face-enrollment");
              }}
              className="text-cyan-400 hover:text-cyan-300 font-semibold underline underline-offset-2 cursor-pointer"
            >
              Open Biometric Enrollment Tool &rarr;
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
