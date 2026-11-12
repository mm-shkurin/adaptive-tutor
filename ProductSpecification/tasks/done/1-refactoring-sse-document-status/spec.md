# Task 1: SSE document status

Type: refactoring

## Problem

After story 2, document status on the library screen updates by polling `GET /api/v1/documents` every 250ms while any row is `waiting` or `indexing`. Live poke showed that is awkward: the page feels stuck, it is unclear whether indexing started, and a full refresh often seems needed. Carryover decision «Documents list polls while in flight» is superseded by `stories/02-document-ingestion/decisions/sse-document-status-decision.md`.

## Solution

Push document status over **SSE** (session-scoped, same auth as the list). Keep `GET /api/v1/documents` for the initial page only. While any owned document is in flight, the client opens the stream and applies events to rows. Retire the 250ms list poll as the happy path; optional short-lived fallback only if the stream cannot open. Events carry at least: document id, status, and the fields the row already shows (`error` when failed; `page_count` / `piece_count` when ready). Later screens that show the same statuses reuse this channel.

Layers: api-spec, adapters (HTTP SSE + emit on status change), application wiring for the indexing loop, frontend documents screen.

## Key Files

- `ProductSpecification/api-specs/documents.yaml`
- `ProductSpecification/stories/02-document-ingestion/decisions/sse-document-status-decision.md`
- `backend/adapters/http/documents.py`
- `backend/application/main.py` (indexing loop / emit hook)
- `backend/usecase/document/index_documents.py` (status transitions — emit boundary)
- `frontend/src/features/documents/useDocumentsScreen.js`
- `frontend/src/features/documents/logic/documentPage.js` (poll helpers → stream apply)
