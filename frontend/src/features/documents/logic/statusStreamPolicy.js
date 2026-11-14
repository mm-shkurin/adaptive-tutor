/** SSE open failure may fall back to list polls; keep the burst bounded. */
export const FALLBACK_POLL_MS = 1000
export const FALLBACK_POLL_LIMIT = 20

/** Server virus-scan budget the upload client must outlast. */
export const VIRUS_SCAN_BUDGET_MS = 30_000
