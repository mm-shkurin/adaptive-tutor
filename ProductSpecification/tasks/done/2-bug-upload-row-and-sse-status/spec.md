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

## RCA (2026-11-12)

### Symptom (authoritative source)

- **Observable:** After choosing a valid PDF on Документы, the list did not gain a «Ждёт» / «В процессе» row; the new file became visible only as «Готов» (often after refresh). Live SSE status motion was not seen in that session.
- **Source:** Task `spec.md` Problem/Reproduction (user-confirmed 2026-11-12); server logs/DB showed `POST /api/v1/documents` **201** and `ready` rows for `demo@example.test` (including `Ustrojstvo-bronetankovoj-tehniki-chast-1.pdf`).
- **Frequency:** every upload in the failing poke session (not intermittent).

### Assumptions audit

| Prior claim | Status | Evidence |
|-------------|--------|----------|
| Backend rejects or never stores the upload | refuted | MEASURED earlier in spec (201 + DB `ready` rows); MEASURED again this RCA via live POST 201 bodies with `status: "waiting"` |
| Backend SSE itself is broken | refuted | Spec’s direct API check; MEASURED this RCA: browser `GET http://127.0.0.1:8010/api/v1/documents/status-events` → **200** `event-stream` after upload |
| UI never applies the 201 body / `pageWithUploaded` never runs (on current HEAD) | refuted | MEASURED DOM timeline: first paint of new row is «Ждёт» immediately after 201 |
| Row is applied then wiped by a late list (on current HEAD) | refuted for HEAD | MEASURED: waiting → indexing → ready stayed on screen; `fresherPage` pending-keep is present (`d7987ee`) |
| Indexing is so fast that waiting is never painted | refuted | MEASURED: waiting samples present (e.g. 1.1 MB upload waiting at t≈3684 ms; 3.6 MB at t≈5262 ms) before indexing/ready |
| Wrong stack / wrong API host | refuted | MEASURED: Vite `:5174`, uvicorn `:8010`, `VITE_API_PROXY_TARGET=http://127.0.0.1:8010`; SSE URL used that host |
| notes.md “still broken after patches” | refuted on HEAD | MEASURED live poke after `6f0f417` + `d7987ee`: Pass criteria hold for 1.1 MB and 3.6 MB PDFs |

### Hypotheses

| # | Candidate cause | Evidence gathered | Label | Verdict |
|---|-----------------|-------------------|-------|---------|
| 1 | Client upload used default **15s** timeout while virus scan can run up to ~30s → abort before 201 → no `pageWithUploaded`; document finishes server-side and appears later as ready | `6f0f417` raised `UPLOAD_TIMEOUT_MS` to 90s and added `reconcileList` on error; `SubmitDocument` runs `virus.clear` before store; MEASURED POST durations ~3.6s / ~5.1s on HEAD (under both 15s and 90s) | MEASURED + REASONED | **confirmed** as a primary cause of the reported “no row until ready” sessions (especially larger/slower scans) |
| 2 | SSE opened through Vite `/api` proxy which **buffered** `text/event-stream`, so pills did not move until refresh | `d7987ee` switched stream base to `VITE_API_PROXY_TARGET` / SSE base; comment in `documentStatusStream.js`; MEASURED HEAD uses `http://127.0.0.1:8010/.../status-events` and advances Ждёт→В процессе→Готов without reload | MEASURED + REASONED | **confirmed** as the cause of “statuses do not work” when the stream was proxied/buffered |
| 3 | `fresherPage` replaced local page with a list response missing the just-uploaded in-flight id → **wiped** the waiting row until a later ready list | Pre-`d7987ee` `fresherPage` mapped only `incoming.documents`; post-fix keeps pending waiting/indexing; unit test `fresherPage keeps a just-uploaded in-flight row…` | REASONED (code/git) | **confirmed** as a wipe mechanism that matches “row gone until ready/refresh” once a concurrent list ran (SSE fallback poll or overlapping GET) |
| 4 | `isStreamOpenError` treated almost any `Error` as stream-open failure → **fallback 1s list poll** that interacted with (3) | Pre-`d7987ee` `instanceof Error`; post-fix narrows to HTTP≥400 / `TypeError` and ignores `AbortError`; earlier backend logs showed paired `GET /documents` ~1s apart while a tab was open | MEASURED (logs) + REASONED | **confirmed** as an aggravating path (starts list traffic that can wipe via (3)); not sufficient alone |
| 5 | Backend holds POST until ready / never returns `waiting` | MEASURED 201 JSON `status: "waiting"` with `page_count`/`piece_count` null; indexing is `schedule_indexing()` after response | MEASURED | **refuted** |
| 6 | CORS / empty `STREAM_BASE` always blocks SSE on this stack | MEASURED SSE 200 on `:8010` with session bearer from the documents page | MEASURED | **refuted** for current env |

### Conclusion

- **Root cause:** Compound **frontend** defect, not a backend intake/SSE outage. The failing poke matched three client mechanisms that were already patched on this branch before this RCA: (1) upload aborted under the default 15s client timeout while ClamAV could still be running, so the UI never applied a `waiting` row from the 201 body; (2) status events were read through Vite’s `/api` proxy and could be buffered, so pills did not move live; (3) list merges via `fresherPage` could drop a just-uploaded waiting/indexing row, especially once SSE fallback started 1s list polls. Together these produce “nothing in the list until ready / refresh,” even though `POST` returned 201 and the DB row reached `ready`.
- **Measured:** On current HEAD (`:5174` + uvicorn `:8010` + `adaptive_tutor_local` + fake OAuth), instrumented browser uploads of `rca-upload.pdf` (~1.1 MB) and `rca-large.pdf` (~3.6 MB) showed POST **201** `waiting`, SSE open on `http://127.0.0.1:8010/api/v1/documents/status-events` **200**, and DOM sequence **Ждёт → В процессе → Готов** without reload. During the in-flight POST (virus + accept) the list gained no new row for ~3.5–5 s (`uploading` only disables the file input — no other affordance).
- **Reasoned:** The user-confirmed failure session is explained by the pre-fix client behavior in `6f0f417` / `d7987ee` (timeout + buffered SSE + list wipe + broad fallback-poll trigger). Those commits’ diffs and messages align with the symptom; this RCA did not re-checkout the pre-fix tree to re-break the UI.
- **Residual unknowns:** Whether the original user session hit timeout, proxy buffering, list wipe, or all three in one upload was not captured with DevTools at the time. Postgres MCP was unavailable; DB checks used SQLAlchemy against `adaptive_tutor_local` instead.
- **Fix lever:** Treat production fixes in `6f0f417` + `d7987ee` as the causal remediation already on the branch; **design** should decide verification / regression coverage (and whether a visible in-upload state during the pre-201 virus wait is in scope). Do not re-implement those patches blindly — re-poke and lock the Pass criteria with tests that hold indexing so «Ждёт» cannot be skipped.
