"use client";

import React, { useEffect, useRef } from "react";
import { useAlerts } from "../../hooks/useAlerts";

/**
 * Bulletproof audio notification synthesizer using Web Audio API.
 * Guarantees zero 404 errors and zero external asset dependency.
 */
export const AlertAudio: React.FC = () => {
  const { latestAlert, isAudioMuted } = useAlerts();
  const lastAlertIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (!latestAlert || isAudioMuted) return;
    if (lastAlertIdRef.current === latestAlert.alert_id) return;

    lastAlertIdRef.current = latestAlert.alert_id;

    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;

      const ctx = new AudioCtx();

      // Dual-tone security chime (880Hz -> 587Hz)
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "sine";
      osc.frequency.setValueAtTime(880, ctx.currentTime); // A5
      osc.frequency.exponentialRampToValueAtTime(587.33, ctx.currentTime + 0.15); // D5

      gain.gain.setValueAtTime(0.25, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.4);
    } catch {
      // Ignore autoplay policy restrictions gracefully
    }
  }, [latestAlert, isAudioMuted]);

  return null;
};
