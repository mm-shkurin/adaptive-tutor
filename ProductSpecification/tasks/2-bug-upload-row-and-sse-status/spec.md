# Task 2: Upload row and SSE status invisible until ready

Type: bug

## Problem

On the documents screen after Task 1 (SSE status stream), the intended UX does **not** hold in live poke against local Vite `:5174` + API `:8010` (`OAUTH_PROVIDER=fake`).

**Expected (Task 1 / decision `sse-document-status-decision.md`):**
1. `GET /api/v1/documents` paints the initial list once.
2. On PDF upload, `POST /api/v1/documents` returns `201` with `status: waiting` and the **new row appears in the list immediately** («Ждёт»).
3. While any row is `waiting` / `indexing`, the client opens `GET /api/v1/documents/status-events` and applies `document-status` events so the pill moves Ждёт → В процессе → Готов without a full list poll.
4. When nothing is in flight, the stream closes.

**Observed (confirmed by user 2026-11-12):**
- After choosing a valid PDF, **nothing appears in the list**.
- The row shows up **only when indexing has finished** (`ready`) — typically after a refresh or when a later list load finally paints it.
- Live status transitions via SSE are not visible; statuses effectively «do not work» for the person watching the screen.
- Feels like the upload did nothing until somehow later the file is there.

**Environment:**
- Frontend: Vite `http://127.0.0.1:5174/` (`VITE_API_PROXY_TARGET=http://127.0.0.1:8010`)
- Backend: local uvicorn on `:8010` (docker `adaptive-tutor-backend` was **not** used / was Exited)
- DB: Postgres `adaptive_tutor_local` on `:5433`
- Auth: `OAUTH_PROVIDER=fake` (browser sign-in uses code `demo` → `demo@example.test`)
- PDF ≥ 1 MB (server minimum); ClamAV on `:3310`

**Server-side evidence (so this is not «upload never accepted»):**
- `POST /api/v1/documents` returns **201** in API logs during the failed UX session.
- Rows exist in `adaptive_tutor_local.documents` as `ready` for `demo@example.test`, including the PDF the person uploaded (`Ustrojstvo-bronetankovoj-tehniki-chast-1.pdf`).
- Direct API check: list + SSE catch-up for that account return the documents with correct statuses. Backend stream itself works when called without the browser UI path.

**Frequency:** every upload in that poke session; not intermittent.

## Reproduction

1. Start stack as in memory-bank local poke: Postgres/Redis/ClamAV; uvicorn `:8010` with fake OAuth + `adaptive_tutor_local`; Vite `:5174`.
2. Open `http://127.0.0.1:5174/`, sign in (fake OAuth).
3. Open Документы. Note empty or existing ready rows.
4. Upload a PDF ≥ 1 MB and ≤ 50 MB.
5. **Watch the list without refreshing.**

**Fail:** no new row while waiting/indexing; no visible status motion. Row appears only once ready (or after F5 when already ready).

**Pass (definition for this task):** new row visible immediately as «Ждёт», then pill advances to «В процессе» and «Готов» without reload; Network shows `POST …/documents` 201, then `GET …/status-events` while in flight, and **no** happy-path 250ms/1s list poll for status.
