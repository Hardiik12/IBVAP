"use client";

import React, { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

const AUTH_PAGES = [
  "/login",
  "/face-enrollment",
  "/face-verification",
  "/admin/face-enrollment",
  "/mfa",
  "/mfa/setup",
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const { authState, isLoading, isMfaSetupRequired, isFaceEnrolled } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const isAuthPage = AUTH_PAGES.includes(pathname);

  useEffect(() => {
    if (isLoading) return;

    if (authState === "UNAUTHENTICATED") {
      if (!isAuthPage) {
        router.replace("/login");
      }
    } else if (authState === "MFA_PENDING") {
      if (pathname !== "/mfa" && pathname !== "/mfa/setup" && !isAuthPage) {
        if (isMfaSetupRequired) {
          router.replace("/mfa/setup");
        } else {
          router.replace("/mfa");
        }
      }
    } else if (authState === "FACE_VERIFICATION_PENDING") {
      if (pathname !== "/face-verification" && pathname !== "/face-enrollment" && pathname !== "/admin/face-enrollment" && !isAuthPage) {
        if (!isFaceEnrolled) {
          router.replace("/face-enrollment");
        } else {
          router.replace("/face-verification");
        }
      }
    } else if (authState === "AUTHENTICATED") {
      if (isAuthPage) {
        router.replace("/dashboard");
      }
    }
  }, [authState, isLoading, pathname, isAuthPage, isMfaSetupRequired, isFaceEnrolled, router]);

  // Pure standalone layout for authentication and onboarding routes (zero loading blocker)
  if (isAuthPage) {
    return <main className="min-h-screen bg-[#070b14]">{children}</main>;
  }

  // Loading state for protected surveillance dashboard
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#070b14] flex flex-col items-center justify-center text-cyan-400 font-mono select-none">
        <div className="relative w-16 h-16 flex items-center justify-center">
          <div className="absolute inset-0 border-2 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
          <div className="w-8 h-8 border-2 border-blue-500/30 border-b-blue-400 rounded-full animate-spin [animation-direction:reverse]" />
        </div>
        <p className="mt-4 text-xs tracking-widest uppercase">
          INITIALIZING SURVEILLANCE SUBSYSTEMS...
        </p>
      </div>
    );
  }

  // Authenticated surveillance shell
  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-slate-950/80">
          {children}
        </main>
      </div>
    </div>
  );
}

export default AppShell;
