import type { Metadata } from "next";
import "./globals.css";
import { AlertProvider } from "../context/AlertContext";
import { CameraProvider } from "../context/CameraContext";
import { Sidebar } from "../components/layout/Sidebar";
import { Header } from "../components/layout/Header";
import { AlertAudio } from "../components/alerts/AlertAudio";
import { AlertBanner } from "../components/alerts/AlertBanner";
import { EvidenceModal } from "../components/evidence/EvidenceModal";

export const metadata: Metadata = {
  title: "IBVAP — Intelligent Border Video Analytics Platform",
  description: "Real-time AI Video Analytics and SHA-256 Cryptographic Evidence Integrity Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-slate-100 flex h-screen overflow-hidden antialiased">
        <AlertProvider>
          <CameraProvider>
            {/* Native Audio Synthesizer */}
            <AlertAudio />

            {/* Sidebar Navigation */}
            <Sidebar />

            {/* Main Application Area */}
            <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden bg-background">
              {/* Header */}
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
          </CameraProvider>
        </AlertProvider>
      </body>
    </html>
  );
}
