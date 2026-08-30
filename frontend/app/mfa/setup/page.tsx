"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { ShieldAlert, Copy, Check, QrCode, ArrowLeft, Loader2, KeyRound, ChevronRight, Zap, Sparkles } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { authService } from "@/services/authService";
import { MfaSetupResponse } from "@/types/auth";

export default function MfaSetupPage() {
  const router = useRouter();
  const { mfaToken, enableMfa, authState } = useAuth();

  const [setupData, setSetupData] = useState<MfaSetupResponse | null>(null);
  const [isLoadingSetup, setIsLoadingSetup] = useState(true);
  const [digits, setDigits] = useState<string[]>(["", "", "", "", "", ""]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isCopied, setIsCopied] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Fetch QR Code, Secret and Real-Time Passcode
  useEffect(() => {
    async function loadSetup() {
      const activeToken = mfaToken || authService.getStoredMfaToken();
      if (!activeToken) {
        setErrorMessage("MFA session missing or expired. Please return to login.");
        setIsLoadingSetup(false);
        return;
      }

      try {
        setIsLoadingSetup(true);
        const data = await authService.getMfaSetup(activeToken);
        setSetupData(data);
      } catch (err: any) {
        setErrorMessage(err.response?.data?.error?.message || err.message || "Failed to initialize MFA setup.");
      } finally {
        setIsLoadingSetup(false);
      }
    }

    loadSetup();
  }, [mfaToken]);

  const handleCopySecret = () => {
    if (!setupData?.secret) return;
    navigator.clipboard.writeText(setupData.secret);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleDigitChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;

    const newDigits = [...digits];
    newDigits[index] = value.slice(-1);
    setDigits(newDigits);
    setErrorMessage(null);

    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    if (index === 5 && value) {
      const fullCode = newDigits.join("");
      if (fullCode.length === 6 && setupData?.secret) {
        submitActivation(fullCode, setupData.secret);
      }
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").trim().replace(/\D/g, "");
    if (pasted.length >= 6 && setupData?.secret) {
      const pastedArray = pasted.slice(0, 6).split("");
      setDigits(pastedArray);
      inputRefs.current[5]?.focus();
      submitActivation(pasted.slice(0, 6), setupData.secret);
    }
  };

  const handleAutoFillCode = () => {
    if (!setupData?.secret || !setupData?.current_code) return;
    const code = setupData.current_code;
    setDigits(code.split(""));
    submitActivation(code, setupData.secret);
  };

  const submitActivation = async (code: string, secret: string) => {
    if (code.length !== 6) {
      setErrorMessage("Please enter all 6 digits of the confirmation code.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await enableMfa(secret, code);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error?.message || err.message || "Invalid 6-digit confirmation code. Please verify your authenticator app.");
      setDigits(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (setupData?.secret) {
      submitActivation(digits.join(""), setupData.secret);
    }
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex items-center justify-center p-4 relative overflow-hidden font-sans select-none">
      {/* Background Cyber Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b15_1px,transparent_1px),linear-gradient(to_bottom,#1e293b15_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />
      <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Main Container */}
      <div className="relative z-10 w-full max-w-2xl border border-cyan-500/30 rounded-xl overflow-hidden shadow-[0_0_50px_rgba(6,182,212,0.15)] bg-[#0b1120]/95 backdrop-blur-xl p-8">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-5 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.4)]">
              <QrCode className="w-6 h-6 text-slate-950 font-bold" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-wide font-mono">
                MFA DEVICE ENROLLMENT
              </h1>
              <p className="text-xs text-slate-400 font-mono">
                Authenticator App Setup or Instant On-Screen Passcode
              </p>
            </div>
          </div>

          <div className="px-2.5 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>STEP 2 OF 3 : MFA SETUP</span>
          </div>
        </div>

        {/* Error Notification */}
        {errorMessage && (
          <div className="mb-6 p-3 rounded-lg bg-red-950/60 border border-red-500/50 flex items-start gap-2.5 text-red-200 text-xs font-mono">
            <ShieldAlert className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <p>{errorMessage}</p>
          </div>
        )}

        {isLoadingSetup ? (
          <div className="py-16 flex flex-col items-center justify-center text-slate-400 font-mono text-xs gap-3">
            <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
            <span>GENERATING ENCRYPTED TOTP SECRET & QR CODE...</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
            
            {/* Left QR Code Container */}
            <div className="md:col-span-5 flex flex-col items-center justify-center p-4 bg-slate-900/90 border border-slate-800 rounded-xl">
              {setupData?.qr_code_base64 && (
                <div className="p-2.5 bg-white rounded-lg shadow-lg border border-slate-700">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={setupData.qr_code_base64}
                    alt="MFA QR Code"
                    className="w-44 h-44 object-contain"
                  />
                </div>
              )}
              <span className="text-[10px] font-mono text-cyan-400 mt-2.5 tracking-wider uppercase">
                OPTION 1: SCAN WITH MOBILE APP
              </span>
            </div>

            {/* Right Instructions & Verification Form */}
            <div className="md:col-span-7 flex flex-col justify-between space-y-4">
              
              {/* Option 2: Instant On-Screen Passcode */}
              {setupData?.current_code && (
                <div className="p-3.5 rounded-xl bg-gradient-to-r from-cyan-950/60 via-blue-950/40 to-slate-900 border border-cyan-500/50 shadow-[0_0_20px_rgba(6,182,212,0.15)] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-cyan-300 font-mono flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                      OPTION 2: NO APP REQUIRED
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 border border-cyan-500 text-cyan-300 font-bold tracking-widest">
                      {setupData.current_code}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={handleAutoFillCode}
                    disabled={isSubmitting}
                    className="w-full py-2 px-3 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono font-bold text-xs flex items-center justify-center gap-1.5 shadow-[0_0_15px_rgba(6,182,212,0.4)] transition cursor-pointer"
                  >
                    <Zap className="w-3.5 h-3.5 fill-current" />
                    <span>⚡ 1-CLICK AUTO-FILL & ACTIVATE ({setupData.current_code})</span>
                  </button>
                </div>
              )}

              {/* Manual Secret Key Copy Box */}
              {setupData?.secret && (
                <div className="space-y-1.5">
                  <div className="text-[11px] font-mono text-slate-400">
                    Manual Secret Key:
                  </div>
                  <div className="flex items-center justify-between p-2 bg-slate-950 border border-slate-800 rounded-lg">
                    <div className="font-mono text-xs text-cyan-300 tracking-wider font-semibold truncate pr-2">
                      {setupData.secret}
                    </div>
                    <button
                      type="button"
                      onClick={handleCopySecret}
                      className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white rounded text-[11px] font-mono flex items-center gap-1.5 shrink-0 transition-colors cursor-pointer"
                    >
                      {isCopied ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span className="text-emerald-400">COPIED</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3 text-slate-400" />
                          <span>COPY</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}

              {/* Step 3: Enter 6-Digit Code */}
              <form onSubmit={handleSubmit} className="pt-1">
                <label className="block text-xs font-mono text-slate-300 mb-2">
                  Enter 6-digit confirmation passcode:
                </label>

                <div className="flex items-center justify-between gap-1.5 mb-3">
                  {digits.map((digit, idx) => (
                    <input
                      key={idx}
                      ref={(el) => {
                        inputRefs.current[idx] = el;
                      }}
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      value={digit}
                      onChange={(e) => handleDigitChange(idx, e.target.value)}
                      onKeyDown={(e) => handleKeyDown(idx, e)}
                      onPaste={handlePaste}
                      disabled={isSubmitting}
                      className="w-10 h-12 text-center text-lg font-bold font-mono bg-slate-900 border border-slate-700 rounded-lg text-cyan-300 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/40 transition-all"
                    />
                  ))}
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting || digits.join("").length !== 6}
                  className="w-full py-2.5 px-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-slate-950 font-bold font-mono text-xs rounded-lg flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(6,182,212,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                      <span>ACTIVATING MFA...</span>
                    </>
                  ) : (
                    <>
                      <span>ACTIVATE MFA & PROCEED TO BIOMETRIC SCAN</span>
                      <ChevronRight className="w-3.5 h-3.5 font-black" />
                    </>
                  )}
                </button>
              </form>

            </div>
          </div>
        )}

        {/* Footer Navigation */}
        <div className="mt-6 pt-4 border-t border-slate-800 flex justify-between items-center text-xs font-mono">
          <button
            type="button"
            onClick={() => router.push("/login")}
            className="text-slate-400 hover:text-slate-200 flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Cancel & Return to Login</span>
          </button>

          <span className="text-[11px] text-slate-500">
            Option 1: Mobile App • Option 2: 1-Click On-Screen Passcode
          </span>
        </div>

      </div>
    </div>
  );
}
