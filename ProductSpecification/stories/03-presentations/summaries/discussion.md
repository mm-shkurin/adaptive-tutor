## discussion (2026-11-25)

**Decision:** Interview gaps D1–D5 closed with AFK defaults (delete material only; graph nodes without edges; weak &lt;40%; sessions = distinct active days; virus on photo/office) and recorded in `AFK_ISSUES.md` / `decisions/afk-defaults-decision.md` so delivery could continue without waiting.
**Alternatives:** Stop AFK until human answers; invent edges/cascade-delete.
**Why this way:** User asked AFK to park questions in a file and keep shipping what the interview already decided.

## discussion (2026-11-25)

**Decision:** Production presentation indexing keeps `FakeOcr` until a real Tesseract adapter exists; Postgres store and HTTP path still land.
**Alternatives:** Block the store until OCR is live; call chat-LLM for every slide.
**Why this way:** Tests already require faked OCR; live poke is human (P3). Shipping persistence unblocks create/add without pretending recognition quality.

## discussion (2026-11-25)

**Quirk:** Document JSON now requires `kind` (`pdf` | `presentation`); status may be `draft` for presentations.
**Where:** `documents._json`, `frontend/.../bodyGuards.js` (`DOCUMENT_KINDS`, `draft` in statuses)
**Implication:** Fixtures and mocks without `kind` fail the FE guard; PDF rows must send `kind: "pdf"`.

## discussion (2026-11-25)

**Quirk:** `PostgresChatStore.person_send_times` returns empty; progress weekly sessions in production mostly count quiz finishes until chat line timestamps exist.
**Where:** `adapters/storage/chat_store.py` / `adapters/progress/quiz_chat_activity.py`
**Implication:** Do not assume `sessions_this_week` includes chat days on a live DB poke.

## discussion (2026-11-25)

**Quirk:** After ordinary PDF indexing erases the file body, presentation `pdf_page` slides get text from `PieceIndex.placed` for that page (PdfReader only if bytes remain).
**Where:** `usecase/presentation/index_presentation.py`
**Implication:** PDF-page slides need the source PDF already indexed with pieces, or retained bytes, or they index empty.

## discussion (2026-11-26)

**Decision:** After a successful presentation index the editor closes so Documents can show the ready row (UI 1.4); reopen via document-name click → GET presentation.
**Alternatives:** Keep editor open and only reconcile behind it; require Back before seeing the list.
**Why this way:** List is unmounted while the editor is open; closing matches the scenario wording without a split view.

## discussion (2026-11-26)

**Quirk:** `chat_lines.created_at` (migration `0018`) backfills from `chats.created_at` for old rows; new person lines stamp wall-clock (or injected store clock).
**Where:** `adapters/storage/chat_store.py`, `chat_attempt_commit.py`
**Implication:** Progress `sessions_this_week` needs `alembic upgrade head` through `0018` before chat days count in prod.
