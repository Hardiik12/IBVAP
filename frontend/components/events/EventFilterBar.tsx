"use client";

import React from "react";
import { EventSeverity, EventType } from "../../types/event";
import { Camera } from "../../types/camera";
import { Filter, Search } from "lucide-react";

interface EventFilterBarProps {
  cameras: Camera[];
  selectedCamera: string;
  selectedSeverity: string;
  searchQuery: string;
  onCameraChange: (camId: string) => void;
  onSeverityChange: (sev: string) => void;
  onSearchChange: (q: string) => void;
}

export const EventFilterBar: React.FC<EventFilterBarProps> = ({
  cameras,
  selectedCamera,
  selectedSeverity,
  searchQuery,
  onCameraChange,
  onSeverityChange,
  onSearchChange,
}) => {
  return (
    <div className="bg-surface-200 border border-surface-border rounded-lg p-3 flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1.5 text-slate-400">
          <Filter className="w-3.5 h-3.5" />
          <span>FILTERS:</span>
        </div>

        {/* Camera Filter */}
        <select
          value={selectedCamera}
          onChange={(e) => onCameraChange(e.target.value)}
          className="bg-surface-100 border border-surface-border text-slate-200 rounded px-2.5 py-1.5 focus:outline-none focus:border-blue-500 cursor-pointer"
        >
          <option value="">All Cameras</option>
          {cameras.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>

        {/* Severity Filter */}
        <select
          value={selectedSeverity}
          onChange={(e) => onSeverityChange(e.target.value)}
          className="bg-surface-100 border border-surface-border text-slate-200 rounded px-2.5 py-1.5 focus:outline-none focus:border-blue-500 cursor-pointer"
        >
          <option value="">All Severities</option>
          <option value="CRITICAL">CRITICAL</option>
          <option value="HIGH">HIGH</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="LOW">LOW</option>
        </select>
      </div>

      {/* Search by Track or Event ID */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search Event ID or Track..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="bg-surface-100 border border-surface-border text-slate-200 placeholder-slate-500 rounded px-3 py-1.5 pl-8 focus:outline-none focus:border-blue-500 w-52"
        />
        <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
      </div>
    </div>
  );
};
