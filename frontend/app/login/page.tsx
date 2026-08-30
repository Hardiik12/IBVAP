"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Shield, Lock, User, Eye, EyeOff, AlertTriangle, Radio, Cpu, CheckCircle2, ChevronRight, Loader2, Scan } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { login, authState } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // If already authenticated or in later stage, route accordingly
  useEffect(() => {
    if (authState === "AUTHENTICATED") {
      router.replace("/dashboard");
    }
  }, [authState, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setErrorMessage("Please enter both Operator ID and Password.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await login(username.trim(), password);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error?.message || err.message || "ACCESS DENIED: Invalid operator credentials.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex items-center justify-center p-4 relative overflow-hidden font-sans select-none">
      {/* Background Cyber Grid & Glow Orbs */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b15_1px,transparent_1px),linear-gradient(to_bottom,#1e293b15_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Main Container */}
      <div className="relative z-10 w-full max-w-4xl grid grid-cols-1 md:grid-cols-12 gap-0 border border-cyan-500/30 rounded-xl overflow-hidden shadow-[0_0_50px_rgba(6,182,212,0.15)] bg-[#0b1120]/90 backdrop-blur-xl">
        
        {/* Left Telemetry HUD Panel (5 cols) */}
        <div className="md:col-span-5 bg-gradient-to-br from-[#0c1427] via-[#09101f] to-[#060b16] p-8 border-b md:border-b-0 md:border-r border-slate-800/80 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 w-48 h-48 bg-cyan-500/5 rounded-full blur-2xl pointer-events-none" />

          <div>
            {/* Header Badge */}
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.5)] border border-cyan-300/30">
                <Shield className="w-6 h-6 text-slate-950 font-black" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-wider text-white font-mono flex items-center gap-1.5">
                  IBVAP <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">v2.4</span>
                </h1>
                <p className="text-[10px] uppercase tracking-widest text-cyan-400/80 font-mono">
                  Border Defense Intelligence
                </p>
              </div>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed mb-6 font-mono">
              Intelligent Border & Vehicle Analytics Platform. Multi-Tier Biometric Defense Access Node.
            </p>

            {/* Tactical Telemetry Badges */}
            <div className="space-y-2.5">
              <div className="flex items-center justify-between text-xs px-3 py-2 rounded bg-slate-900/80 border border-slate-800 text-slate-300 font-mono">
                <span className="flex items-center gap-2">
                  <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
                  PERIMETER SENSORS
                </span>
                <span className="text-emerald-400 font-semibold">ACTIVE</span>
              </div>

              <div className="flex items-center justify-between text-xs px-3 py-2 rounded bg-slate-900/80 border border-slate-800 text-slate-300 font-mono">
                <span className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
                  MFA TOTP TOKEN
                </span>
                <span className="text-blue-400 font-semibold">RFC-6238</span>
              </div>

              <div className="flex items-center justify-between text-xs px-3 py-2 rounded bg-slate-900/80 border border-slate-800 text-slate-300 font-mono">
                <span className="flex items-center gap-2">
                  <Scan className="w-3.5 h-3.5 text-cyan-400" />
                  FACIAL BIOMETRICS
                </span>
                <span className="text-cyan-400 font-semibold">1:1 SFace</span>
              </div>
            </div>
          </div>

          {/* Dev Quick Hint */}
          <div className="mt-8 pt-4 border-t border-slate-800/80">
            <div className="bg-cyan-950/40 border border-cyan-500/20 rounded p-2.5 text-[11px] font-mono text-slate-400">
              <span className="text-cyan-400 font-bold">DEV OPERATOR ACCESS:</span>
              <div className="mt-1 flex justify-between text-slate-300">
                <span>User: <strong className="text-white">admin</strong></span>
                <span>Pass: <strong className="text-white">Admin@123</strong></span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Form Panel (7 cols) */}
        <div className="md:col-span-7 p-8 md:p-10 flex flex-col justify-center relative">
          <div className="mb-6">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-blue-500/10 border border-blue-500/30 text-blue-400 text-[11px] font-mono mb-3">
              <Lock className="w-3 h-3" />
              <span>STEP 1 OF 3 : OPERATOR CREDENTIALS</span>
            </div>
            <h2 className="text-2xl font-bold text-white tracking-wide font-mono">
              SECURE OPERATOR ACCESS
            </h2>
            <p className="text-xs text-slate-400 mt-1 font-mono">
              Enter authorized credentials to initiate authentication pipeline.
            </p>
          </div>

          {/* Error Callout */}
          {errorMessage && (
            <div className="mb-5 p-3.5 rounded-lg bg-red-950/60 border border-red-500/50 flex items-start gap-3 text-red-200 text-xs font-mono animate-in fade-in slide-in-from-top-2 duration-200">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-red-300">ACCESS REJECTED</p>
                <p className="text-red-200/90 mt-0.5">{errorMessage}</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username / Operator ID Input */}
            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1.5 uppercase tracking-wider">
                Operator ID or Security Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin"
                  autoComplete="username"
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-900/90 border border-slate-700/80 rounded-lg text-white placeholder-slate-500 text-sm font-mono focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors"
                />
              </div>
            </div>

            {/* Password Input with Show/Hide Toggle */}
            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1.5 uppercase tracking-wider">
                Security Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  autoComplete="current-password"
                  required
                  className="w-full pl-10 pr-11 py-2.5 bg-slate-900/90 border border-slate-700/80 rounded-lg text-white placeholder-slate-500 text-sm font-mono focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-500 hover:text-slate-300 transition-colors"
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Maintain Session Checkbox */}
            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 text-xs font-mono text-slate-400 cursor-pointer hover:text-slate-300">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-3.5 h-3.5 rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-cyan-500 focus:ring-offset-0 focus:ring-offset-slate-900"
                />
                <span>Maintain terminal state</span>
              </label>

              <span className="text-[11px] font-mono text-cyan-400/80 hover:underline cursor-pointer">
                Defense Auth Tier 3
              </span>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full mt-3 py-3 px-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-slate-950 font-bold font-mono text-sm rounded-lg flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(6,182,212,0.3)] hover:shadow-[0_0_25px_rgba(6,182,212,0.5)] transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                  <span>VERIFYING CREDENTIALS...</span>
                </>
              ) : (
                <>
                  <span>PROCEED TO MFA VERIFICATION</span>
                  <ChevronRight className="w-4 h-4 font-black" />
                </>
              )}
            </button>
          </form>

          {/* Security Notice Footer */}
          <div className="mt-6 text-center">
            <p className="text-[10px] font-mono text-slate-400 tracking-wider">
              PROTECTED BY IBVAP COMMAND DEFENSE SYSTEM • UNAUTHORIZED ACCESS IS MONITORED
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}
