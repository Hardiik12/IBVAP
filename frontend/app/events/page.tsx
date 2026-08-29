"use client";

import React, { useState, useEffect } from "react";
import { EventTable } from "../../components/events/EventTable";
import { eventService } from "../../services/eventService";
import { cameraService } from "../../services/cameraService";
import { IntrusionEvent } from "../../types/event";
import { Camera } from "../../types/camera";
import { ListOrdered, ShieldCheck, Download } from "lucide-react";
import { Button } from "../../components/ui/Button";

export default function EventsPage() {
  const [events, setEvents] = useState<IntrusionEvent[]>([]);
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [evts, cams] = await Promise.all([
          eventService.getEvents(),
          cameraService.getCameras(),
        ]);
        setEvents(evts);
        setCameras(cams);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const exportJsonLog = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(events, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `ibvap_events_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl">
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <ListOrdered className="w-5 h-5 text-blue-400" />
            <span>Forensic Event Audit Log</span>
          </h1>
          <p className="text-xs font-mono text-slate-400 mt-1">
            Immutable log of all detected boundary crossings and state machine transitions
          </p>
        </div>

        <Button
          variant="secondary"
          size="sm"
          onClick={exportJsonLog}
          leftIcon={<Download className="w-4 h-4" />}
        >
          Export JSON Audit
        </Button>
      </div>

      {/* Main Event Table */}
      <EventTable events={events} cameras={cameras} />
    </div>
  );
}
