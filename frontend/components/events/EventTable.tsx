"use client";

import React, { useState, useMemo } from "react";
import { IntrusionEvent } from "../../types/event";
import { Camera } from "../../types/camera";
import { Badge } from "../ui/Badge";
import { EventFilterBar } from "./EventFilterBar";
import { formatDate } from "../../utils/formatters";
import { useAlerts } from "../../hooks/useAlerts";
import { FileSearch, ShieldAlert } from "lucide-react";

interface EventTableProps {
  events: IntrusionEvent[];
  cameras: Camera[];
}

export const EventTable: React.FC<EventTableProps> = ({ events, cameras }) => {
  const { openEvidenceModal } = useAlerts();

  const [selectedCamera, setSelectedCamera] = useState("");
  const [selectedSeverity, setSelectedSeverity] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredEvents = useMemo(() => {
    return events.filter((e) => {
      if (selectedCamera && e.camera_id !== selectedCamera) return false;
      if (selectedSeverity && e.severity !== selectedSeverity) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const matchId = e.event_id.toLowerCase().includes(q);
        const matchTrack = `track #${e.track_id}`.toLowerCase().includes(q);
        const matchClass = (e.class_name || "").toLowerCase().includes(q);
        if (!matchId && !matchTrack && !matchClass) return false;
      }
      return true;
    });
  }, [events, selectedCamera, selectedSeverity, searchQuery]);

  return (
    <div className="space-y-4">
      <EventFilterBar
        cameras={cameras}
        selectedCamera={selectedCamera}
        selectedSeverity={selectedSeverity}
        searchQuery={searchQuery}
        onCameraChange={setSelectedCamera}
        onSeverityChange={setSelectedSeverity}
        onSearchChange={setSearchQuery}
      />

      <div className="bg-surface-200 border border-surface-border rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-surface-border bg-surface-100/70 text-slate-400">
                <th className="py-3 px-4 font-semibold">EVENT ID</th>
                <th className="py-3 px-4 font-semibold">TIMESTAMP</th>
                <th className="py-3 px-4 font-semibold">CAMERA</th>
                <th className="py-3 px-4 font-semibold">RESTRICTED ZONE</th>
                <th className="py-3 px-4 font-semibold">OBJECT / TRACK</th>
                <th className="py-3 px-4 font-semibold">SEVERITY</th>
                <th className="py-3 px-4 font-semibold text-right">EVIDENCE ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border/60 text-slate-300">
              {events.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-16 text-slate-400 font-mono">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <div className="w-10 h-10 rounded-xl bg-surface-100 border border-surface-border flex items-center justify-center text-slate-500">
                        <FileSearch className="w-5 h-5 text-slate-500" />
                      </div>
                      <p className="text-sm font-semibold text-slate-300">No audit logs available</p>
                      <p className="text-xs text-slate-500 font-sans">
                        New system security events and boundary crossing logs will appear here in real-time.
                      </p>
                    </div>
                  </td>
                </tr>
              ) : filteredEvents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-slate-500 font-mono">
                    No security events found matching criteria.
                  </td>
                </tr>
              ) : (
                filteredEvents.map((evt) => (
                  <tr
                    key={evt.event_id}
                    className="hover:bg-surface-100/60 transition-colors"
                  >
                    <td className="py-3 px-4 font-bold text-slate-200">{evt.event_id}</td>
                    <td className="py-3 px-4 text-slate-400" suppressHydrationWarning>{formatDate(evt.timestamp)}</td>
                    <td className="py-3 px-4 text-slate-300">{evt.camera_id}</td>

                    <td className="py-3 px-4 font-sans font-medium text-slate-200">
                      {evt.zone_name || evt.zone_id}
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-blue-400 font-bold">Track #{evt.track_id}</span>
                      <span className="text-slate-500 ml-1">({evt.class_name})</span>
                    </td>
                    <td className="py-3 px-4">
                      <Badge severity={evt.severity}>{evt.severity}</Badge>
                    </td>
                    <td className="py-3 px-4 text-right">
                      {evt.evidence_id ? (
                        <button
                          onClick={() => openEvidenceModal(evt.evidence_id!)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-blue-950/60 hover:bg-blue-900 border border-blue-800/80 text-blue-300 transition"
                        >
                          <FileSearch className="w-3.5 h-3.5" />
                          <span>Verify</span>
                        </button>
                      ) : (
                        <span className="text-slate-600">N/A</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
