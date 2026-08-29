import { PolygonPoint } from "../types/zone";

export interface BoxRenderOptions {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  label?: string;
  className?: string;
  trackId?: number;
  confidence?: number;
  isInsideZone?: boolean;
  color?: string;
  isNormalized?: boolean;
}

export interface ZoneRenderOptions {
  polygon: PolygonPoint[];
  name: string;
  color?: string;
  isAlertActive?: boolean;
}

export function clearCanvas(ctx: CanvasRenderingContext2D, width: number, height: number): void {
  ctx.clearRect(0, 0, width, height);
}

/**
 * Draws the 4 massive Green Corner Reticles in the viewport
 */
export function drawViewportGreenReticles(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number
): void {
  ctx.save();

  const reticleColor = "#00ff66";
  const padding = 16;
  const len = 32;
  const thickness = 3.5;

  ctx.strokeStyle = reticleColor;
  ctx.lineWidth = thickness;
  ctx.shadowColor = reticleColor;
  ctx.shadowBlur = 10;

  // Top-Left [ ┌ ]
  ctx.beginPath();
  ctx.moveTo(padding, padding + len);
  ctx.lineTo(padding, padding);
  ctx.lineTo(padding + len, padding);
  ctx.stroke();

  // Top-Right [ ┐ ]
  ctx.beginPath();
  ctx.moveTo(width - padding - len, padding);
  ctx.lineTo(width - padding, padding);
  ctx.lineTo(width - padding, padding + len);
  ctx.stroke();

  // Bottom-Left [ └ ]
  ctx.beginPath();
  ctx.moveTo(padding, height - padding - len);
  ctx.lineTo(padding, height - padding);
  ctx.lineTo(padding + len, height - padding);
  ctx.stroke();

  // Bottom-Right [ ┘ ]
  ctx.beginPath();
  ctx.moveTo(width - padding - len, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.lineTo(width - padding, height - padding - len);
  ctx.stroke();

  ctx.restore();
}

/**
 * Renders the glowing red/green virtual fence laser line across the surveillance feed
 */
export function drawVirtualFenceLine(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  isBreached = true
): void {
  ctx.save();

  const startX = 0;
  const startY = height * 0.72;
  const endX = width;
  const endY = height * 0.38;

  const fenceColor = isBreached ? "#ff3333" : "#00ff66";

  // Dual laser line with intense glow
  ctx.strokeStyle = fenceColor;
  ctx.shadowColor = fenceColor;
  ctx.shadowBlur = 16;

  // Primary Line
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  ctx.moveTo(startX, startY);
  ctx.lineTo(endX, endY);
  ctx.stroke();

  // Parallel Secondary Line
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(startX, startY + 4);
  ctx.lineTo(endX, endY + 4);
  ctx.stroke();

  // Floating "VIRTUAL FENCE" Text Badge
  ctx.shadowBlur = 0;
  const midX = width * 0.58;
  const midY = height * 0.54;

  ctx.save();
  ctx.translate(midX, midY);
  const angle = Math.atan2(endY - startY, endX - startX);
  ctx.rotate(angle);

  ctx.font = "bold 11px JetBrains Mono, monospace";
  ctx.fillStyle = fenceColor;
  ctx.shadowColor = fenceColor;
  ctx.shadowBlur = 8;
  ctx.fillText("────── VIRTUAL FENCE ──────", -90, -8);

  ctx.restore();
  ctx.restore();
}

/**
 * Draws dynamic tactical YOLO detection bounding box with real class label, confidence, track ID, and crosshairs
 */
export function drawTacticalIntruderBox(
  ctx: CanvasRenderingContext2D,
  options: BoxRenderOptions,
  canvasWidth: number,
  canvasHeight: number
): void {
  let {
    x1,
    y1,
    x2,
    y2,
    isNormalized = true,
    trackId = 1,
    className = "person",
    confidence = 0.9,
    label,
    isInsideZone = false,
  } = options;

  if (isNormalized) {
    x1 = x1 * canvasWidth;
    y1 = y1 * canvasHeight;
    x2 = x2 * canvasWidth;
    y2 = y2 * canvasHeight;
  }

  const boxW = Math.max(10, x2 - x1);
  const boxH = Math.max(10, y2 - y1);
  const centerX = (x1 + x2) / 2;
  const centerY = (y1 + y2) / 2;
  const boxColor = isInsideZone ? "#ff2a2a" : "#00ff66";

  ctx.save();

  // 1. Glowing Target Bounding Box
  ctx.strokeStyle = boxColor;
  ctx.lineWidth = 2;
  ctx.shadowColor = boxColor;
  ctx.shadowBlur = 12;

  ctx.beginPath();
  ctx.rect(x1, y1, boxW, boxH);
  ctx.stroke();

  // Subtle interior fill
  ctx.fillStyle = isInsideZone ? "rgba(255, 42, 42, 0.12)" : "rgba(0, 255, 102, 0.08)";
  ctx.fill();

  ctx.shadowBlur = 0;

  // 2. Top Banner Label: "[CLASS] [CONF%] | [STATUS]"
  const confPercent = Math.round(confidence * 100);
  const statusText = isInsideZone ? "ZONE INTRUSION" : "TRACKED";
  const labelText = label || `${className.toUpperCase()} ${confPercent}% | ${statusText}`;

  ctx.font = "bold 10px JetBrains Mono, monospace";
  const metrics = ctx.measureText(labelText);
  const bannerW = metrics.width + 12;
  const bannerY = Math.max(20, y1);

  ctx.fillStyle = "rgba(10, 15, 25, 0.92)";
  ctx.strokeStyle = boxColor;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.roundRect(x1, bannerY - 20, bannerW, 18, 2);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = boxColor;
  ctx.fillText(labelText, x1 + 6, bannerY - 7);

  // 3. Right Callout Tag: "Track #ID" with leader line
  const calloutX = Math.min(canvasWidth - 110, x2 + 16);
  const calloutY = y1 + 14;
  const formattedId = trackId > 0 ? (trackId < 10 ? `0${trackId}` : `${trackId}`) : "01";
  const calloutText = `Track #${formattedId}`;

  // Leader line
  ctx.strokeStyle = "#94a3b8";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(x2, y1 + 14);
  ctx.lineTo(calloutX, calloutY);
  ctx.lineTo(calloutX + 6, calloutY);
  ctx.stroke();

  // Callout Box
  ctx.font = "10px JetBrains Mono, monospace";
  const calloutMetrics = ctx.measureText(calloutText);
  const tagW = calloutMetrics.width + 10;

  ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
  ctx.strokeStyle = "rgba(255, 255, 255, 0.25)";
  ctx.beginPath();
  ctx.roundRect(calloutX + 6, calloutY - 10, tagW, 20, 2);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = "#cbd5e1";
  ctx.fillText(calloutText, calloutX + 11, calloutY + 4);

  // 4. Center-Mass Target Crosshair
  ctx.strokeStyle = "rgba(255, 255, 255, 0.85)";
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(centerX - 8, centerY);
  ctx.lineTo(centerX + 8, centerY);
  ctx.moveTo(centerX, centerY - 8);
  ctx.lineTo(centerX, centerY + 8);
  ctx.stroke();

  // 5. Bottom-Center Reference Point (Ground Contact)
  ctx.beginPath();
  ctx.arc(centerX, y2, 3.5, 0, Math.PI * 2);
  ctx.fillStyle = isInsideZone ? "#ff2a2a" : "#00ff66";
  ctx.fill();
  ctx.strokeStyle = "#ffffff";
  ctx.lineWidth = 1;
  ctx.stroke();

  ctx.restore();
}

/**
 * Standard polygon zone drawing (compatible with legacy views)
 */
export function drawPolygonZone(
  ctx: CanvasRenderingContext2D,
  options: ZoneRenderOptions,
  canvasWidth: number,
  canvasHeight: number
): void {
  const { polygon, name, isAlertActive = false } = options;
  if (!polygon || polygon.length < 3) return;

  const strokeColor = isAlertActive ? "#ef4444" : "#f59e0b";
  ctx.save();
  ctx.beginPath();
  ctx.moveTo(polygon[0][0] * canvasWidth, polygon[0][1] * canvasHeight);
  for (let i = 1; i < polygon.length; i++) {
    ctx.lineTo(polygon[i][0] * canvasWidth, polygon[i][1] * canvasHeight);
  }
  ctx.closePath();
  ctx.fillStyle = isAlertActive ? "rgba(239, 68, 68, 0.15)" : "rgba(245, 158, 11, 0.15)";
  ctx.fill();
  ctx.strokeStyle = strokeColor;
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.restore();
}

/**
 * Standard bounding box drawing
 */
export function drawBoundingBox(
  ctx: CanvasRenderingContext2D,
  options: BoxRenderOptions,
  canvasWidth: number,
  canvasHeight: number
): void {
  drawTacticalIntruderBox(ctx, options, canvasWidth, canvasHeight);
}

/**
 * Reference point math helper
 */
export function drawReferencePoint(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  isInsideZone: boolean
): void {
  ctx.save();
  ctx.beginPath();
  ctx.arc(x, y, 4, 0, Math.PI * 2);
  ctx.fillStyle = isInsideZone ? "#ef4444" : "#10b981";
  ctx.fill();
  ctx.restore();
}

/**
 * Standard HUD overlay
 */
export function drawHudOverlay(
  ctx: CanvasRenderingContext2D,
  cameraId: string,
  width: number,
  height: number,
  fps = 29.8
): void {
  drawViewportGreenReticles(ctx, width, height);
}
