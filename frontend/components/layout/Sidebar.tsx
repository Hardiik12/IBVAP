"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Bell,
  ListOrdered,
  FileCheck2,
  Video,
  Shield,
  ChevronLeft,
  ChevronRight,
  Radio,
} from "lucide-react";
import { useAlerts } from "../../hooks/useAlerts";

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const { unreadCount } = useAlerts();
  const [isCollapsed, setIsCollapsed] = useState(true);

  const navigation = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    {
      name: "Alerts",
      href: "/alerts",
      icon: Bell,
      badge: unreadCount > 0 ? unreadCount : undefined,
    },
    { name: "Audit Log", href: "/events", icon: ListOrdered },
    { name: "Evidence Vault", href: "/evidence", icon: FileCheck2 },
    { name: "Cameras", href: "/cameras", icon: Video },
  ];

  return (
    <aside
      className={`${
        isCollapsed ? "w-16" : "w-56"
      } bg-surface-300/95 border-r border-white/10 flex flex-col h-screen select-none transition-all duration-300 ease-in-out relative z-40`}
    >
      {/* Top Logo & Title */}
      <div className="p-3.5 border-b border-white/10 flex items-center justify-between bg-surface-200/50">
        <div className="flex items-center gap-2.5 overflow-hidden">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 shrink-0">
            <Shield className="w-4 h-4" />
          </div>
          {!isCollapsed && (
            <div className="transition-opacity duration-200 whitespace-nowrap">
              <div className="text-sm font-bold tracking-wider text-slate-100 font-mono flex items-center gap-1.5">
                IBVAP
                <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-blue-950 text-blue-400 border border-blue-800">
                  AI
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Toggle Collapse Button */}
        <button
          onClick={() => setIsCollapsed((prev) => !prev)}
          className="p-1 rounded-md hover:bg-surface-100 text-slate-400 hover:text-white transition"
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Live Stream Dot (Compact or Expanded) */}
      <div className="px-3 py-2 border-b border-white/5 bg-surface-200/20 text-center">
        {isCollapsed ? (
          <div className="w-2.5 h-2.5 mx-auto rounded-full bg-emerald-400 animate-ping" title="Feed Active" />
        ) : (
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
            <span className="flex items-center gap-1.5">
              <Radio className="w-3 h-3 text-emerald-400 animate-pulse" />
              STATUS
            </span>
            <span className="text-emerald-400 font-bold">ONLINE</span>
          </div>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-2 py-3 space-y-1.5 overflow-y-auto custom-scrollbar">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              title={isCollapsed ? item.name : undefined}
              className={`flex items-center ${
                isCollapsed ? "justify-center p-2.5" : "justify-between px-3 py-2.5"
              } rounded-lg text-xs font-medium font-mono transition-all relative group ${
                isActive
                  ? "bg-blue-600/20 text-blue-400 border border-blue-500/40 shadow-[0_0_12px_rgba(59,130,246,0.15)]"
                  : "text-slate-400 hover:text-slate-200 hover:bg-surface-100 border border-transparent"
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? "text-blue-400" : "text-slate-400"}`} />
                {!isCollapsed && <span className="whitespace-nowrap">{item.name}</span>}
              </div>

              {/* Badge Counter */}
              {item.badge !== undefined && (
                <span
                  className={`${
                    isCollapsed
                      ? "absolute top-1 right-1 w-2 h-2 p-0 rounded-full bg-red-500 animate-ping"
                      : "px-1.5 py-0.2 text-[10px] font-mono font-bold bg-red-600 text-white rounded-full"
                  }`}
                >
                  {!isCollapsed && item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer Info */}
      {!isCollapsed && (
        <div className="p-3 border-t border-white/10 bg-surface-200/30 text-[10px] text-slate-500 font-mono">
          <div className="flex items-center justify-between">
            <span>CORE</span>
            <span className="text-slate-300">YOLOv8 + PIP</span>
          </div>
        </div>
      )}
    </aside>
  );
};
