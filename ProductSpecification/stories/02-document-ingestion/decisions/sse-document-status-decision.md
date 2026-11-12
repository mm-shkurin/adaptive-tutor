# Decision: Document status updates over SSE (not list polling)

**Date**: 2026-11-11 **Supersedes**: carryover «Documents list polls while in flight»

Live poke after story 2: polling `GET /api/v1/documents` every 250ms while a row is waiting/indexing is awkward — the screen feels stuck unless the page is refreshed, and it is unclear whether indexing started.

| Rejected | Why |
|----------|-----|
| Keep 250ms list poll | Constant list traffic; UX still feels like a dead page when the worker is slow or missing; hard to see waiting → indexing without staring at a pill that may not change for a long stretch. |
| WebSocket for status only | Heavier than needed for one-way status; SSE matches «server pushes status» with a simpler client. |

**Chosen**: Push document status over **SSE**. The list load stays a normal GET; while any owned document is in flight (waiting / indexing), the client opens an SSE stream and applies status events to rows. Polling the full list for status is retired once SSE is live.

## Shape (to lock in the task / api-spec)

- Stream is session-scoped (same auth as the list).
- Events name at least: document id, status, and the fields the row already shows (error when failed; page_count / piece_count when ready).
- Client falls back only if the stream cannot open — not a permanent poll as the happy path.
- Presentation / chat screens that later show the same statuses should reuse this channel, not invent a second poll.

## Not in this decision

- Real embeddings + Qdrant (separate backlog item).
- Story 3 interview scope.
