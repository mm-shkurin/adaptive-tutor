# Task 2 — handoff notes (bug still open in UI)

User confirmed 2026-11-12 after Task 1: upload row + SSE status UX still broken. Use this in the next chat; do not assume the patches below fixed the poke.

## Intended flow (product)

See Task 1 done folder + `stories/02-document-ingestion/decisions/sse-document-status-decision.md`.

```
GET /documents  → paint list
POST /documents → 201 waiting → paint row immediately (pageWithUploaded)
open SSE status-events while waiting|indexing → apply events to rows
stream ends when nothing in flight
```

## Already landed (Task 1 + follow-up commits on `features/document-ingestion`)

These are **in the branch**; they are candidates / partial mitigations, **not** a verified green poke.

| Commit / area | Intent |
|---------------|--------|
| Task 1 SSE | `GET /api/v1/documents/status-events`, hub + `NotifyingDocumentIntake`, frontend stream consumer, retire 250ms poll |
| `6f0f417` | Upload client timeout 90s; after upload error, `reconcileList()` |
| `5f0ce2d` | Clear refusals for `<1MB`, virus, rate limit |
| `d7987ee` | `fresherPage` keeps local waiting/indexing rows missing from a late list; SSE `fetch` uses `VITE_API_PROXY_TARGET` (direct `:8010`) to avoid Vite buffering; vite proxy timeouts for SSE |

Key files:

- `frontend/src/features/documents/useDocumentsScreen.js` — upload → `pageWithUploaded`; SSE while `needsStatusStream`
- `frontend/src/features/documents/logic/documentPage.js` — `pageWithUploaded`, `fresherPage`, `pageWithStatusEvent`
- `frontend/src/shared/api/backend/documentStatusStream.js` — SSE client (`STREAM_BASE`)
- `frontend/src/shared/api/backend/documentApi.js` — `UPLOAD_TIMEOUT_MS`
- `frontend/vite.config.js` — proxy SSE headers / timeouts
- `backend/adapters/http/documents.py` — `/status-events`
- `backend/adapters/http/document_status_hub.py`
- `backend/adapters/document_status/notifying_intake.py`

## What next chat must still prove

Live browser poke still fails the Pass criteria in `spec.md`. Treat root cause as **not closed**.

### Hypotheses to re-verify (do not skip)

1. **UI never applies 201 body** — guard/`UnexpectedBodyError`, abort, or `shouldApplyUpload` false; Network 201 but no row.
2. **Row applied then wiped** — concurrent `listDocuments` + `showPage`/`fresherPage`/`lists` epoch; StrictMode double effects; fallback poll after SSE error.
3. **SSE never delivers to the React tree** — CORS on direct `:8010`, `STREAM_BASE` empty in some boot, parse/`isDocumentBody` drop, effect `inFlight` never true because row never painted.
4. **Indexing finishes so fast** that waiting/indexing are never painted — still must show waiting from POST body before ready; if only ready appears after F5, paint path is wrong.
5. **Wrong stack** — person hitting another port/gateway; docker backend Exited; confirm Vite → `:8010`.

### Suggested first moves

1. Reproduce with DevTools Network + React: confirm `POST` 201 body, whether `pageWithUploaded` runs, whether `status-events` opens and frames arrive.
2. If 201 and body OK but no row → trace `useDocumentsScreen` upload success path and any later `showPage` that replaces state.
3. If row flashes then vanishes → log `fresherPage` inputs; fix epoch/poll/SSE interaction.
4. If row never in flight → SSE never starts; fix paint first, then status events.
5. Add a failing frontend/acceptance test that asserts: after upload response, list contains waiting **before** ready (hold indexing in acceptance like story 2 UI tests).

### Local poke commands (reference)

- API: uvicorn on `127.0.0.1:8010`, DB `adaptive_tutor_local`, `OAUTH_PROVIDER=fake`, ClamAV `127.0.0.1:3310`
- Front: `frontend/.env` → `VITE_API_PROXY_TARGET=http://127.0.0.1:8010`, `FRONTEND_PORT=5174`
- Do **not** require rebuilding `adaptive-tutor-backend` docker image for this bug unless you choose to switch to compose backend.

### Related done work

- `ProductSpecification/tasks/done/1-refactoring-sse-document-status/` — SSE feature delivery (contract + wiring); this Task 2 is the residual UX bug.
