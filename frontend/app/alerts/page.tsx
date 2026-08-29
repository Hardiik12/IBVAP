"use client";

import React, { useState } from "react";
import { useAlerts } from "../../hooks/useAlerts";
import { AlertItem } from "../../components/alerts/AlertItem";
import { Bell, CheckCheck, Trash2, ShieldAlert, Sparkles } from "lucide-react";
import { Button } from "../../components/ui/Button";

export default function AlertsPage() {
  const { alerts, unreadCount, markAllAsRead, clearAlerts } = useAlerts();
  const [filterSeverity, setFilterSeverity] = useState<string>("");

  const filteredAlerts = alerts.filter((a) => {
    if (filterSeverity && a.severity !== filterSeverity) return false;
    return true;
  });

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl">
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Bell className="w-5 h-5 text-blue-400" />
            <span>Alerts & Incident Notification Center</span>
          </h1>
          <p className="text-xs font-mono text-slate-400 mt-1">
            Real-time WebSocket alerts dispatched by IBVAP State Machine Engine
          </p>
        </div>

        <div className="flex items-center gap-3">
          {unreadCount > 0 && (
            <Button
              variant="secondary"
              size="sm"
              onClick={markAllAsRead}
              leftIcon={<CheckCheck className="w-4 h-4" />}
            >
              Acknowledge All ({unreadCount})
            </Button>
          )}

          {alerts.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={clearAlerts}
              leftIcon={<Trash2 className="w-4 h-4 text-red-400" />}
            >
              Clear Log
            </Button>
          )}
        </div>
      </div>

      {/* Severity Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-surface-border/60 pb-3 text-xs font-mono">
        <span className="text-slate-500 mr-2">FILTER:</span>
        {["", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((sev) => (
          <button
            key={sev}
            onClick={() => setFilterSeverity(sev)}
            className={`px-3 py-1.5 rounded-lg border transition ${
              filterSeverity === sev
                ? "bg-blue-600/20 border-blue-500 text-blue-300 font-bold"
                : "bg-surface-200 border-surface-border text-slate-400 hover:text-slate-200"
            }`}
          >
            {sev === "" ? "ALL ALERTS" : sev}
          </button>
        ))}
      </div>

      {/* Alert Feed List */}
      <div className="space-y-3">
        {filteredAlerts.length === 0 ? (
          <div className="bg-surface-200 border border-surface-border rounded-xl p-12 text-center text-slate-500 font-mono text-sm">
            <Bell className="w-10 h-10 text-slate-600 mx-auto mb-3 stroke-1" />
            <p>No alerts matching the selected filter.</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <AlertItem key={alert.alert_id} alert={alert} />
          ))
        )}
      </div>
    </div>
  );
}
