## Quirk: PdfRead.text must carry table Markdown

**Quirk:** `IndexDocuments` indexes only `PdfRead.text`; the `table` field is unused by the worker.
**Where:** `backend/usecase/document/index_documents.py`, `backend/adapters/pdfreader/pdf_reader.py`
**Implication:** The reader must put table Markdown inside `text` (full NFC composition matching the fixture), not rely on a later merge of `table`.
**From:** scenario 4.1 (4.1-an-accepted-pdf-becomes-ready-and-its-text-and-tables-can-be-searched)

## Decision: Acceptance indexing is gated

**Decision:** Acceptance indexing stays held until `IndexProbe.release_indexing()`.
**Why:** A background worker that indexes on upload races the "still waiting" read/list asserts.
**Where applied:** `acceptance/clients/application/index_probe.py`, `acceptance/support/acceptance_server.py`, `DocumentStatements.when_*_ready` / `when_the_document_finishes_indexing`
**From:** scenario 4.1 (4.1-an-accepted-pdf-becomes-ready-and-its-text-and-tables-can-be-searched)

## Quirk: Ready seed then hold indexing for a later upload

**Quirk:** After a ready PDF is seeded for the browser, `hold_indexing()` clears the release so the next upload stays «Ждёт» until re-released.
**Where:** `acceptance/statements/signed_in_browser_statements.py`, `IndexProbe.hold_indexing`
**Implication:** Upload UI tests must call `when_indexing_is_released()` after asserting waiting.
**From:** scenario 1.2 (1.2-a-ready-document-shows-its-name-size-pages-and-piece-count)

## Quirk: Probe pauses memory intake on indexing

**Quirk:** With an `IndexProbe`, `MemoryDocumentIntake.save` sleeps `indexing_hold_seconds` after status becomes indexing so the UI can observe «В процессе».
**Where:** `backend/adapters/memory/document_intake.py`, `acceptance/clients/application/index_probe.py`
**Implication:** Asserting the indexing pill in browser tests depends on this acceptance-only pause.
**From:** scenario 2.1 (2.1-an-accepted-pdf-appears-as-waiting-and-then-becomes-ready)

## Decision: Documents list polls while in flight

**Decision:** The documents screen polls GET `/api/v1/documents` every 250ms while any row is waiting or indexing.
**Why:** Upload answers before indexing finishes; the list is the status source.
**Where applied:** `frontend/src/features/documents/useDocumentsScreen.js`
**From:** scenario 2.1 (2.1-an-accepted-pdf-appears-as-waiting-and-then-becomes-ready)

## Decision: Upload refusals stay before SubmitDocument

**Decision:** Refuse unacceptable uploads in the HTTP adapter before `SubmitDocument`; no usecase change for this scenario.
**Why:** The outline codes are request-boundary validation; calling submit would consume rate/idempotency on a refused file.
**Where applied:** `backend/adapters/http/documents.py`, `backend/adapters/pdfreader/upload_check.py`
**From:** scenario 2.1 (2.1-an-unacceptable-file-adds-no-document)

## Quirk: Empty upload filename arrives as a plain form field

**Quirk:** A multipart `file` part with an empty filename is parsed as a plain `str` form field, not `UploadFile`.
**Where:** Starlette/`request.form()` consumed by `backend/adapters/http/documents.py` `_upload_part`
**Implication:** Presence of key `file` that is not an `UploadFile` must map to `name_missing`, not `file_missing`.
**From:** scenario 2.1 (2.1-an-unacceptable-file-adds-no-document)

## Decision: Document names are grapheme-limited and stored as text

**Decision:** The 255 name limit is NFC grapheme clusters; storage is `Text`, not `VARCHAR(255)`.
**Why:** A combining mark at the edge is two code points and one letter; a code-point cap would refuse or cut it.
**Where applied:** `backend/domain/document/file_name.py`, migration `0006`, `DocumentRow.name`, `documents.yaml`
**From:** scenario 2.4 (2.4-a-name-that-would-split-a-letter-at-the-limit-is-not-stored-broken)

## Quirk: Acceptance document intake has no VARCHAR length

**Quirk:** Acceptance wires `MemoryDocumentIntake`, so a grapheme-safe name longer than 255 code points can pass HTTP acceptance while Postgres `VARCHAR(255)` would still fail.
**Where:** `acceptance/support/acceptance_server.py`, `backend/adapters/memory/document_intake.py`
**Implication:** Name-length edge cases need a storage round-trip (or live Postgres) to catch column cuts.
**From:** scenario 2.4 (2.4-a-name-that-would-split-a-letter-at-the-limit-is-not-stored-broken)

## Decision: Mid-index failure is named via `_refusal` → `_fail`

**Decision:** A mid-index failure after a successful PDF read goes through `IndexDocuments._refusal` → `_fail(reason)`; the reason names the failed part.
**Why:** Tables are not a separate store step; the named failure is the refusal after text was read, before pieces are written.
**Where applied:** `backend/usecase/document/index_documents.py`, `ProbeIndexDocuments`, `FakeIndexDocuments`
**From:** scenario 4.2 (4.2-a-failed-index-names-the-part-and-leaves-nothing-searchable)

## Quirk: Token-cap before pieces()

**Quirk:** `over_piece_cap` after `ExtractedText.pieces()` never fails a many_pieces-scale PDF in practice — splitting ~1M tokens hangs before the document can become failed.
**Where:** `backend/usecase/document/index_documents.py`, `backend/domain/document/extracted_text.py`
**Implication:** Run `over_piece_cap(0, text)` (token branch) before calling `pieces()`.
**From:** scenario 4.5 (4.5-indexing-that-would-store-more-than-2000-pieces-fails-the-document)

## Decision: Fail over-cap PDFs before piece splitting

**Decision:** Fail over-cap PDFs with `too many pieces` via a token-cap check before splitting; keep the piece-count check after `pieces()` for the non-token path.
**Why:** The fixture exceeds `PIECE_CAP * TOKENS_PER_PIECE` without needing a completed split.
**Where applied:** `backend/usecase/document/index_documents.py`, `indexing_budget.over_piece_cap`
**From:** scenario 4.5 (4.5-indexing-that-would-store-more-than-2000-pieces-fails-the-document)

## Quirk: FakeIndexDocuments needs the injectable Clock

**Quirk:** `FakeIndexDocuments` must receive the same injectable `Clock` as `DocumentStatements`.
**Where:** `backend/usecase/tests/conftest.py`
**Implication:** Advancing `documents.clock` never trips `IndexingBudget.overdue` if the indexer still uses `_WallClock`.
**From:** scenario 4.6 (4.6-indexing-that-has-not-finished-in-5-minutes-is-failed)

## Quirk: Finished re-index needs a cleared table arm and a read count

**Quirk:** Clearing `_fail_table_after_text` and counting `FakePdfReader.read_count` are required for a real sanity fail on a second index of a finished document.
**Where:** `backend/usecase/tests/statements/document_statements.py`
**Implication:** Without those, a second run still ends ready/failed with the same pieces (`_store` skips; table arm still refuses).
**From:** scenario 4.7 (4.7-a-finished-document-is-not-indexed-again)
