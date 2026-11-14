# Task 2 — closed (Option A regression lock)

Closed after RCA (2026-11-12): compound frontend defect already remediated on branch by `6f0f417` (upload timeout 90s + reconcileList) and `d7987ee` (fresherPage pending-keep + direct SSE base). This task locked those guards with frontend unit tests and verified Pass via `TestUploadAppearsWaitingThenReady` (hold indexing).

## Do not re-open from older poke notes

Pre-RCA “still broken / not closed” poke notes are historical. Authoritative close-out: `progress.md` + `spec.md` § RCA.

## Key locks added

- `UPLOAD_TIMEOUT_MS` ≥ 90s (`documentApi.test.js`) and ≥ `VIRUS_SCAN_BUDGET_MS`
- `resolveDocumentStatusStreamBase` preference order (`documentStatusStream.test.js`)
- `isStreamOpenError` narrow classification (`documentStatusStream.test.js`)
- Duplicate status apply leaves status unchanged (`documentPage.test.js`)
- `FALLBACK_POLL_LIMIT` / `FALLBACK_POLL_MS` shared policy (`statusStreamPolicy.js`)

## Verification

- Selenium: `TestUploadAppearsWaitingThenReady` — 1 passed
- Backend SSE: `TestStatusEventsFollowUploadWithoutListPoll` — 1 passed

## Follow-ups (NEEDS_CYCLE from boundary review — not blocking Pass)

1. `pageWithStatusEvent` should return the same page reference when status is unchanged so `applyStatusEvent` can no-op without bumping the list epoch.
2. After SSE fallback poll exhausts (`FALLBACK_POLL_LIMIT`), recover (final reconcile and/or reopen stream) so a row cannot stick on «Ждёт» forever.
3. Characterize happy-path: while SSE succeeds, `listDocuments` must not run on the 1s fallback timer (needs hook-test harness).
