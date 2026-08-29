import React from "react";
import Link from "next/link";
import { ShieldAlert, ArrowLeft } from "lucide-react";
import { Button } from "../components/ui/Button";

export default function NotFound() {
  return (
    <div className="h-[70vh] flex flex-col items-center justify-center text-center p-6 space-y-4">
      <div className="w-16 h-16 rounded-full bg-surface-100 border border-surface-border flex items-center justify-center text-slate-400">
        <ShieldAlert className="w-8 h-8" />
      </div>
      <h2 className="text-xl font-bold text-slate-100">404 — Tactical Route Not Found</h2>
      <p className="text-sm font-mono text-slate-400 max-w-md">
        The requested operational view does not exist in the IBVAP system catalog.
      </p>
      <Link href="/">
        <Button variant="secondary" leftIcon={<ArrowLeft className="w-4 h-4" />}>
          Return to Dashboard
        </Button>
      </Link>
    </div>
  );
}
