"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { Camera } from "../types/camera";
import { Zone } from "../types/zone";
import { cameraService } from "../services/cameraService";

interface CameraContextType {
  cameras: Camera[];
  selectedCamera: Camera | null;
  zones: Zone[];
  showZones: boolean;
  showBoundingBoxes: boolean;
  showHud: boolean;
  isLoading: boolean;
  selectCamera: (cameraId: string) => void;
  toggleZones: () => void;
  toggleBoundingBoxes: () => void;
  toggleHud: () => void;
  refreshCameras: () => Promise<void>;
}

const CameraContext = createContext<CameraContextType | undefined>(undefined);

export function CameraProvider({ children }: { children: React.ReactNode }) {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null);
  const [zones, setZones] = useState<Zone[]>([]);
  const [showZones, setShowZones] = useState(true);
  const [showBoundingBoxes, setShowBoundingBoxes] = useState(true);
  const [showHud, setShowHud] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  const fetchCameraData = useCallback(async () => {
    setIsLoading(true);
    try {
      const cams = await cameraService.getCameras();
      setCameras(cams);
      if (cams.length > 0) {
        const active = cams.find((c) => c.status === "ACTIVE") || cams[0];
        setSelectedCamera((prev) => prev || active);

        const activeZones = await cameraService.getCameraZones(active.id);
        setZones(activeZones);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCameraData();
  }, [fetchCameraData]);

  const selectCamera = useCallback(
    async (cameraId: string) => {
      const target = cameras.find((c) => c.id === cameraId);
      if (target) {
        setSelectedCamera(target);
        const camZones = await cameraService.getCameraZones(target.id);
        setZones(camZones);
      }
    },
    [cameras]
  );

  const toggleZones = useCallback(() => setShowZones((prev) => !prev), []);
  const toggleBoundingBoxes = useCallback(() => setShowBoundingBoxes((prev) => !prev), []);
  const toggleHud = useCallback(() => setShowHud((prev) => !prev), []);

  return (
    <CameraContext.Provider
      value={{
        cameras,
        selectedCamera,
        zones,
        showZones,
        showBoundingBoxes,
        showHud,
        isLoading,
        selectCamera,
        toggleZones,
        toggleBoundingBoxes,
        toggleHud,
        refreshCameras: fetchCameraData,
      }}
    >
      {children}
    </CameraContext.Provider>
  );
}

export function useCameraContext(): CameraContextType {
  const context = useContext(CameraContext);
  if (!context) {
    throw new Error("useCameraContext must be used within a CameraProvider");
  }
  return context;
}
