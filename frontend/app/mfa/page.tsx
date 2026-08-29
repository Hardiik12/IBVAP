"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck, KeyRound, AlertTriangle, ArrowLeft, Loader2, QrCode, Timer } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function MfaVerificationPage() {
  const router = useRouter();
  const { mfaData, verifyMfa, authState } = useAuth();

  const [digits, setDigits] = useState<string[]>(["", "", "", "", "", ""]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [secondsRemaining, setSecondsRemaining] = useState<number>(30);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // If already authenticated, go to dashboard
  useEffect(() => {
    if (authState === "AUTHENTICATED") {
      router.replace("/dashboard");
    } else if (authState === "UNAUTHENTICATED") {
      router.replace("/login");
    }
  }, [authState, router]);

  // Focus the first input box on load
  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  // Rotating TOTP 30s window countdown timer indicator
  useEffect(() => {
    const updateCountdown = () => {
      const currentSeconds = new Date().getSeconds();
      setSecondsRemaining(30 - (currentSeconds % 30));
    };
    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleDigitChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return; // Only allow numbers

    const newDigits = [...digits];
    // Take the last character if typed
    newDigits[index] = value.slice(-1);
    setDigits(newDigits);
    setErrorMessage(null);

    // Auto-advance to next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    // If all 6 digits filled, auto-submit
    if (index === 5 && value) {
      const fullCode = newDigits.join("");
      if (fullCode.length === 6) {
        submitCode(fullCode);
      }
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !digits[index] && index > 0) {
      // Focus previous input on backspace if current is empty
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").trim().replace(/\D/g, "");
    if (pasted.length >= 6) {
      const pastedArray = pasted.slice(0, 6).split("");
      setDigits(pastedArray);
      inputRefs.current[5]?.focus();
      submitCode(pasted.slice(0, 6));
    }
  };

  const submitCode = async (codeToSubmit: string) => {
    if (codeToSubmit.length !== 6) {
      setErrorMessage("Please enter all 6 digits of your authenticator code.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await verifyMfa(codeToSubmit);
      router.replace("/dashboard");
    } catch (err: any) {
      setErrorMessage(err.message || "MFA VERIFICATION FAILED: Code is invalid or expired.");
      // Clear inputs for re-entry
      setDigits(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitCode(digits.join(""));
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex items-center justify-center p-4 relative overflow-hidden font-sans select-none">
      {/* Background Cyber Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b15_1px,transparent_1px),linear-gradient(to_bottom,#1e293b15_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Main Card */}
      <div className="relative z-10 w-full max-w-md border border-cyan-500/30 rounded-xl overflow-hidden shadow-[0_0_50px_rgba(6,182,212,0.15)] bg-[#0b1120]/95 backdrop-blur-xl p-8">
        
        {/* Header Icon */}
        <div className="text-center mb-6">
          <div className="w-14 h-14 mx-auto mb-4 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.4)] border border-cyan-300/40">
            <ShieldCheck className="w-8 h-8 text-slate-950 font-black" />
          </div>

          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-[11px] font-mono mb-2">
            <KeyRound className="w-3 h-3" />
            <span>STEP 2 OF 2 : MFA CHALLENGE</span>
          </div>

          <h1 className="text-xl font-bold text-white tracking-wide font-mono">
            SECURITY VERIFICATION
          </h1>
          <p className="text-xs text-slate-400 mt-1.5 font-mono">
            Enter the 6-digit TOTP code from your Authenticator app for{" "}
            <span className="text-cyan-400 font-semibold">{mfaData?.username || "Operator"}</span>.
          </p>
        </div>

        {/* Error Notification */}
        {errorMessage && (
          <div className="mb-6 p-3 rounded-lg bg-red-950/60 border border-red-500/50 flex items-start gap-2.5 text-red-200 text-xs font-mono animate-in fade-in duration-200">
            <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <p>{errorMessage}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 6-Digit Segmented Input Boxes */}
          <div className="flex items-center justify-between gap-2">
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
                className="w-12 h-14 text-center text-xl font-bold font-mono bg-slate-900/90 border border-slate-700/80 rounded-lg text-cyan-300 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/40 shadow-[inset_0_0_8px_rgba(0,0,0,0.5)] transition-all"
              />
            ))}
          </div>

          {/* Rotating TOTP Window Timer */}
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 px-1">
            <span className="flex items-center gap-1.5 text-slate-400">
              <Timer className="w-3.5 h-3.5 text-cyan-400" />
              Code rotates in:
            </span>
            <span className="text-cyan-400 font-bold tracking-wider">{secondsRemaining}s</span>
          </div>

          {/* Submit Action */}
          <button
            type="submit"
            disabled={isSubmitting || digits.join("").length !== 6}
            className="w-full py-3 px-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-slate-950 font-bold font-mono text-sm rounded-lg flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(6,182,212,0.3)] hover:shadow-[0_0_25px_rgba(6,182,212,0.5)] transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                <span>AUTHORIZING ACCESS...</span>
              </>
            ) : (
              <span>CONFIRM & ENTER DASHBOARD</span>
            )}
          </button>
        </form>

        {/* Secondary Navigation */}
        <div className="mt-6 pt-5 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs font-mono">
          <button
            type="button"
            onClick={() => router.push("/mfa/setup")}
            className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <QrCode className="w-3.5 h-3.5" />
            <span>Setup / Rebind Authenticator</span>
          </button>

          <button
            type="button"
            onClick={() => router.push("/login")}
            className="text-slate-400 hover:text-slate-200 flex items-center gap-1 transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Switch Operator</span>
          </button>
        </div>

      </div>
    </div>
  );
}
