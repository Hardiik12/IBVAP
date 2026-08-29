"use client";

import React, { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { AlertAudio } from "../alerts/AlertAudio";
import { AlertBanner } from "../alerts/AlertBanner";
import { EvidenceModal } from "../evidence/EvidenceModal";
import { Loader2, Shield } from "lucide-react";

const AUTH_ROUTES = ["/login", "/mfa", "/mfa/setup"];

export const AppShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const pathname = usePathname();
  const router = useRouter();
  const { authState, isLoading } = useAuth();

  const isAuthRoute = AUTH_ROUTES.some((route) => pathname === route || pathname.startsWith(route + "/"));

  useEffect(() => {
    if (isLoading) return;

    if (!isAuthRoute) {
      if (authState === "UNAUTHENTICATED") {
        router.replace("/login");
      } else if (authState === "MFA_PENDING") {
        router.replace("/mfa");
      }
    }
  }, [authState, isLoading, isAuthRoute, router]);

  // If on an unauthenticated page (/login, /mfa, /mfa/setup), render cleanly without surveillance shell
  if (isAuthRoute) {
    return <main className="w-full min-h-screen">{children}</main>;
  }

  // Loading state when initial session token verification is in flight
  if (isLoading) {
    return (
      <div className="w-full h-screen bg-[#070b14] flex flex-col items-center justify-center text-slate-300 font-mono gap-4">
        <div className="w-12 h-12 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.3)]">
          <Shield className="w-6 h-6 text-cyan-400 animate-pulse" />
        </div>
        <div className="flex items-center gap-2 text-xs text-cyan-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>VERIFYING DEFENSE PROTOCOLS & OPERATOR CLEARANCE...</span>
        </div>
      </div>
    );
  }

  // If not authenticated and on protected route, show transition screen while redirect triggers
  if (authState !== "AUTHENTICATED") {
    return (
      <div className="w-full h-screen bg-[#070b14] flex flex-col items-center justify-center text-slate-300 font-mono gap-4">
        <div className="w-12 h-12 rounded-xl bg-blue-500/20 border border-blue-500/40 flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.3)]">
          <Shield className="w-6 h-6 text-blue-400" />
        </div>
        <p className="text-xs text-slate-400">REDIRECTING TO OPERATOR LOGIN...</p>
      </div>
    );
  }

  // Full Command Center Surveillance Shell
  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      {/* Native Audio Synthesizer */}
      <AlertAudio />

      {/* Tactical Sidebar Navigation */}
      <Sidebar />

      {/* Main Application Surveillance Workspace */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden bg-background">
        {/* Header with dynamic operator and session profile */}
        <Header />

        {/* Dynamic Alert Banner upon Intrusion */}
        <AlertBanner />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto custom-scrollbar p-3.5">
          {children}
        </main>
      </div>

      {/* Global Evidence Inspection & SHA-256 Verification Modal */}
      <EvidenceModal />
    </div>
  );
};
