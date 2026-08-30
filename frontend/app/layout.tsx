import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "../context/AuthContext";
import { AlertProvider } from "../context/AlertContext";
import { CameraProvider } from "../context/CameraContext";
import { AppShell } from "../components/layout/AppShell";

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
        <AuthProvider>
          <CameraProvider>
            <AlertProvider>
              <AppShell>{children}</AppShell>
            </AlertProvider>
          </CameraProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
