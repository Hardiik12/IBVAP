/**
 * Formatting utilities for IBVAP dates, hashes, and numbers.
 */

/**
 * Parses an ISO UTC date string safely across all browsers and formats.
 * Enforces UTC timezone if no offset is explicitly provided.
 */
export function parseUTCDate(dateInput: string | Date | null | undefined): Date {
  if (!dateInput) return new Date();
  if (dateInput instanceof Date) return dateInput;

  let str = String(dateInput).trim();
  // Handle space separator from SQLite datetime
  str = str.replace(" ", "T");

  // If string has no timezone indicator (+, -, or Z), treat as UTC and append 'Z'
  const hasTimezone = str.endsWith("Z") || str.endsWith("z") || /[+-]\d{2}:?\d{2}$/.test(str);
  if (!hasTimezone) {
    str = str + "Z";
  }

  const d = new Date(str);
  return isNaN(d.getTime()) ? new Date() : d;
}

export function formatDate(isoString: string | Date): string {
  try {
    const date = parseUTCDate(isoString);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch {
    return String(isoString);
  }
}

/**
 * Formats relative time elapsed from an authoritative UTC timestamp.
 * - less than 10 seconds → "Just now"
 * - less than 60 seconds → "X sec ago"
 * - less than 60 minutes → "X min ago"
 * - otherwise            → "X hr ago"
 */
export function formatTimeAgo(isoString: string | Date): string {
  try {
    const eventTime = parseUTCDate(isoString).getTime();
    const diffMs = Math.max(0, Date.now() - eventTime);
    const diffSec = Math.floor(diffMs / 1000);

    if (diffSec < 10) return "Just now";
    if (diffSec < 60) return `${diffSec} sec ago`;

    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin} min ago`;

    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return `${diffHour} hr ago`;

    const diffDays = Math.floor(diffHour / 24);
    return `${diffDays}d ago`;
  } catch {
    return "Just now";
  }
}

export function truncateHash(hash: string, startChars = 8, endChars = 8): string {
  if (!hash || hash.length <= startChars + endChars) return hash;
  return `${hash.substring(0, startChars)}...${hash.substring(hash.length - endChars)}`;
}

export function formatConfidence(conf: number): string {
  return `${(conf * 100).toFixed(1)}%`;
}
