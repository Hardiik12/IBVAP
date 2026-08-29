"use client";

import React from "react";
import { AlertItem } from "./AlertItem";
import { useAlerts } from "../../hooks/useAlerts";
import { Bell, CheckCheck, Trash2 } from "lucide-react";

export const AlertFeed: React.FC = () => {
  const { alerts, unreadCount, markAllAsRead, clearAlerts } = useAlerts();

  return (
    <div className="surveillance-card corner-brackets flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/10 bg-white/[0.02] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-blue-400" />
          <span className="font-semibold text-sm text-slate-100">REAL-TIME ALERTS</span>
          {unreadCount > 0 && (
            <span className="px-2 py-0.5 text-xs font-mono font-bold bg-red-600/90 text-white rounded-full">
              {unreadCount} NEW
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {alerts.length > 0 && (
            <>
              <button
                onClick={markAllAsRead}
                className="text-xs text-slate-400 hover:text-slate-200 transition p-1 hover:bg-surface-50 rounded"
                title="Mark all as read"
              >
                <CheckCheck className="w-4 h-4" />
              </button>
              <button
                onClick={clearAlerts}
                className="text-xs text-slate-400 hover:text-red-400 transition p-1 hover:bg-surface-50 rounded"
                title="Clear all alerts"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Feed List */}
      <div className="flex-1 p-3 space-y-2.5 overflow-y-auto custom-scrollbar max-h-[580px]">
        {alerts.length === 0 ? (
          <div className="h-48 flex flex-col items-center justify-center text-center p-4 text-slate-500 font-mono text-xs">
            <Bell className="w-8 h-8 text-slate-600 mb-2 stroke-1" />
            <p>NO ACTIVE ALERTS</p>
            <p className="text-[11px] text-slate-600 mt-1">
              Perimeter monitoring active. Any intrusion will trigger instant alert.
            </p>
          </div>
        ) : (
          alerts.map((alert) => <AlertItem key={alert.alert_id} alert={alert} />)
        )}
      </div>
    </div>
  );
};
