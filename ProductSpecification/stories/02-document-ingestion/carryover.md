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
