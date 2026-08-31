const PREFIX = "trace:investigation:";

export function readInvestigationCache(investigationId) {
  if (typeof window === "undefined" || !investigationId) return null;
  try {
    const raw = window.localStorage.getItem(`${PREFIX}${investigationId}`);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function writeInvestigationCache(investigationId, data) {
  if (typeof window === "undefined" || !investigationId) return;
  try {
    window.localStorage.setItem(
      `${PREFIX}${investigationId}`,
      JSON.stringify({ investigation_id: investigationId, cached_at: new Date().toISOString(), data }),
    );
  } catch {
    // Storage can be unavailable or full; the network path remains available.
  }
}

export function removeInvestigationCache(investigationId) {
  if (typeof window === "undefined" || !investigationId) return;
  try {
    window.localStorage.removeItem(`${PREFIX}${investigationId}`);
  } catch {
    // Storage can be unavailable; the next dashboard load will use the API.
  }
}
