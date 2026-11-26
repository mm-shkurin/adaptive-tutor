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

## Weak OCR → formula assist (2026-11-26)

**Decision:** Production keeps `NoopFormulaAssist`; tests script `FakeFormulaAssist` until a multimodal enricher is wired.
**Why:** Existing chat LLM is text completions; image OCR enrichment needs a separate HTTP contract.
**Where applied:** `application/presentation_wiring.py`, `adapters/presentation/noop_formula_assist.py`

## discussion (2026-11-26)

**Mistake:** Soft-stopped the 110-minute AFK after ~17 minutes when the «ready without human» queue looked empty.
**Why wrong:** The user set an explicit wall-clock budget and said park blockers in a file and keep going.
**Correct location/approach:** Spend remaining AFK budget on parkable work (write selenium, formal hazard/tiering, CI, scaffold) instead of ending at the first soft queue gap.

## IndexPresentation fail paths (2026-11-26)

**Surprise:** `Presentation.failed` existed but `IndexPresentation` never called it; OCR/search exceptions left the deck indexing or ready with partial pieces.
**Why:** Happy-path index was wired first; external-failure branches from the test-spec were still open.
**Impact:** Index now maps OCR/store refusal to `failed` with empty pieces; callers must treat `failed` as terminal for re-index until a retry path is added.

## Deleted-source tombstone (2026-11-26)

**Surprise:** `PostgresChatStore` used an inner join on documents, so hard-deleted presentations made chats disappear from list/get instead of showing «Источник удалён».
**Why:** Chat rows store only `document_id` and took the title from the join.
**Impact:** Outer join + `DELETED_SOURCE_NAME` (and quiz list enrichment) keep history cards visible after D1 hard-delete.

## Failed-index recovery (2026-11-26)

**Decision:** After OCR/search index failure, keep slide bytes, allow re-index and add-slides from `failed`, and catch unexpected exceptions as `indexing failed`.
**Why:** Leaving `failed` non-indexable made the editor CTA a 404 dead-end; clearing bytes on fail forced re-upload.
**Where applied:** `index_presentation.py`, `add_slides.py`

## Failed editor UX (2026-11-26)

**Mistake:** Selenium UI 1.4 tried `send_keys` on the gallery button / hidden file input in headless Chrome.
**Why wrong:** `slide-from-gallery` is a button that opens a native picker; hidden inputs did not reliably fire `change` under headless.
**Correct location/approach:** Seed create/add/index over HTTP, then assert the Documents ready row; keep `slide-gallery-input` testid for a later headed path.

## Failed editor UX (2026-11-26)

**Quirk:** AcceptanceServer exposes `POST /acceptance/presentations/ocr-fail` and `ocr-clear` against the wired `FakeOcr`.
**Where:** `acceptance/support/acceptance_server.py`
**Implication:** Browser tests that need a failed index must hit those probes before `POST …/index`; production has no equivalent.

## Selenium progress topic actions (2026-11-26)

**Mistake:** Located progress topics with `[data-testid^='prog-topic-']` and clicked the first match whose `.text` contained the topic name.
**Why wrong:** `prog-topic-nodes` is a parent whose text includes every child label, so the click hit the card, not the `button[data-testid^='prog-topic-']` row; `topic-quiz` never appeared.
**Correct location/approach:** Restrict to `button[data-testid^='prog-topic-']` (and exclude `prog-weak-mastery-*` when counting weak rows).
