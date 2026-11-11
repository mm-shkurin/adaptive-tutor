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

## Decision: Finished docs refuse rework in `_index`

**Decision:** `IndexDocuments._index` returns immediately when `Document.is_finished()`; a forced second run still calls `_index` so that guard is what refuses rework.
**Why:** Finished documents are terminal — re-running with restored bytes must not rewrite pieces or flip a failed row to ready.
**Where applied:** `backend/domain/document/document.py`, `backend/usecase/document/index_documents.py`, `acceptance/support/acceptance_server.py` (`_second_indexing_run`)
**From:** scenario 4.7 (4.7-a-finished-document-is-not-indexed-again)

## Decision: Status moves only go forward through transition

**Decision:** `Document.transition` allows only waiting→indexing and indexing→ready|failed; skip, reverse, and moves from ready/failed raise `InvalidStatusTransition`.
**Why:** Finished docs used to no-op as HTTP 200 instead of refusing the move.
**Where applied:** `backend/domain/document/document.py`, acceptance `/move`
**From:** scenario 4.8 (4.8-a-step-that-skips-or-reverses-indexing-is-refused)

## Decision: Seed failed browser docs without an illegal move

**Decision:** Browser fixtures seed a failed document via `IndexProbe.force_failed_document`, not waiting→failed through `/move`.
**Why:** waiting→failed is refused by `Document.transition`.
**Where applied:** `acceptance/clients/application/index_probe.py`, `acceptance/statements/signed_in_browser_statements.py`
**From:** scenario 4.8 (4.8-a-step-that-skips-or-reverses-indexing-is-refused)

## Decision: Searchability is Document.is_ready

**Decision:** `Document.is_ready()` is true only for `status == "ready"`; `SearchDocuments` gates pieces and extracted text on it.
**Why:** An unknown/corrupted status must not expose seeded piece rows.
**Where applied:** `backend/domain/document/document.py`, `backend/usecase/document/search_documents.py`
**From:** scenario 4.9 (4.9-an-unknown-status-is-not-treated-as-ready)

## Decision: next_waiting claims the document

**Decision:** `DocumentIntake.next_waiting` atomically moves `waiting → indexing` and returns that claim; a concurrent loser gets `None`.
**Why:** Two workers that both see waiting would otherwise both index and write pieces.
**Where applied:** Memory, Fake, and Postgres `DocumentIntake.next_waiting`
**From:** scenario 4.10 (4.10-two-indexing-claims-of-one-document-store-one-set-of-pieces)

## Quirk: piece replace-count does not prove exclusive claim

**Quirk:** `IndexDocuments._store` skips replace when pieces already exist, so `replace_count == 1` can pass without an atomic waiting claim.
**Where:** `backend/usecase/document/index_documents.py` (`_store`)
**Implication:** Dual-claim guards must assert claim cardinality (one non-None `next_waiting`), not write count alone.
**From:** scenario 4.10 (4.10-two-indexing-claims-of-one-document-store-one-set-of-pieces)

## Decision: In-flight indexing refuses a second `_index`

**Decision:** `IndexingBudget.begin` returns false while the document id is in `_inflight`; overlapping `_index` returns before `_run`.
**Why:** A second run started mid-read would otherwise re-enter PDF read and race `_store` (replace-count alone can still stay 1).
**Where applied:** `backend/usecase/document/indexing_budget.py`, `IndexDocuments._index`
**From:** scenario 4.11 (4.11-a-second-indexing-run-started-while-the-first-is-going-stores-one-set)

## Quirk: Overlapping-run guards need attempt/read count

**Quirk:** `piece_write_count` / `replace_count == 1` stays green even when a second `_index` enters `_run` during a blocked PDF read — `_store` skips once pieces exist.
**Where:** acceptance `then_the_two_runs_do_not_both_write_pieces`, usecase indexing claim statements
**Implication:** Assert `indexing_attempts == 1` (acceptance) or `read_count == 1` (usecase) so the in-flight refuse is forced.
**From:** scenario 4.11 (4.11-a-second-indexing-run-started-while-the-first-is-going-stores-one-set)

## Decision: First terminal status wins on save

**Decision:** `Document.prefer_terminal` keeps a finished row when a later save brings a different status; intakes apply that under save (Postgres with `FOR UPDATE`).
**Why:** Two loads taken while indexing can both transition locally; last-write-wins would erase an earlier ready with a stale failed.
**Where applied:** `backend/domain/document/document.py`; Fake / Memory / Postgres `DocumentIntake.save`
**From:** scenario 4.12 (4.12-a-stale-status-write-does-not-erase-a-newer-one)

## Quirk: Stale terminal writes need frozen loads

**Quirk:** Sequential acceptance `/move` ready→failed is 409 after 4.8; concurrent stale writes need two held indexing snapshots and `/stale-save`.
**Where:** `acceptance/clients/application/index_probe.py` (`hold_two_loads`), `acceptance/support/acceptance_server.py`
**Implication:** Do not simulate last-write races with two fresh re-reads through `/move`.
**From:** scenario 4.12 (4.12-a-stale-status-write-does-not-erase-a-newer-one)

## Decision: PDF parse runs off the event loop

**Decision:** `PyPdfReader.read` parses via `asyncio.to_thread` so the five-minute deadline can cancel the await.
**Why:** Sync pymupdf on the loop would block the deadline poll for a costly file.
**Where applied:** `backend/adapters/pdfreader/pdf_reader.py`
**From:** scenario 4.13 (4.13-a-pathological-pdf-does-not-keep-indexing-busy-past-five-minutes)

## Quirk: Synthetic `_pdf_of_size` fails pymupdf

**Quirk:** `_pdf_of_size` builds bytes that pymupdf cannot open (`invalid_pdf`); padded real fixtures pass the upload gate.
**Where:** `acceptance/statements/document_statements.py` (`_pdf_of_size`, `_pad_pdf_to_minimum`)
**Implication:** Costly/pathological acceptance bodies should pad `lecture.pdf` (or another readable fixture), not `_pdf_of_size`.
**From:** scenario 4.13 (4.13-a-pathological-pdf-does-not-keep-indexing-busy-past-five-minutes)

## Decision: Upload virus scan is VirusCheck on SubmitDocument

**Decision:** `VirusCheck.clear(content)` runs at the start of `SubmitDocument.submit`; Probe and ClamAV implement the port.
**Why:** Settings already required ClamAV; unclean files must add no row.
**Where applied:** `backend/usecase/document/submit_document.py`, `adapters/virus/clamav.py`, `ProbeVirusCheck`
**From:** scenario 1.1 (1.1-1.2-virus-check-on-upload)

## Quirk: Idempotent replay still virus-scans

**Quirk:** `SubmitDocument` calls `virus.clear` before the idempotency lookup, so a replayed Idempotency-Key still scans.
**Where:** `backend/usecase/document/submit_document.py`
**Implication:** Upload-path scan counts include replays; indexing retries are a separate “no second virus check” path.
**From:** scenario 1.1 (1.1-1.2-virus-check-on-upload)

## Quirk: FakePieceIndex needs search-store outcome

**Quirk:** FakePieceIndex must `set_outcome` for `times out` / `refuses` / `answers unreadable` or usecase tests never hit `StoreUnavailable`.
**Where:** `backend/usecase/tests/fake/document/fake_piece_index.py`
**Implication:** Search-store usecase steps arm the fake before `index_waiting`.
**From:** scenario 2.1 (2.1-a-search-store-that-does-not-accept-the-index-fails-the-document)

## Decision: Partial ready failure keeps pieces, skips rewrite

**Decision:** After pieces are written, a failed ready step leaves the document indexing with pieces intact; `_store` skips `replace` when pieces already exist so a retry finishes ready with one write.
**Why:** Search-store write succeeded; rewriting on retry would duplicate the piece set.
**Where applied:** `IndexDocuments._store`; Fake/Probe `_hold_ready` for the partial-ready seam
**From:** scenario 2.2 (2.2-a-retry-after-a-partial-index-does-not-write-the-pieces-twice)

## Decision: Embedding refusal fails; server error pauses the try

**Decision:** Embedding `refuses` / `unreadable` fail the document as `embedding refused`; `server_error` returns `PAUSE` so `IndexingBudget.begin` still counted the try and the document does not become ready.
**Why:** A hard refusal must stop; a transient server error must spend a try without finishing.
**Where applied:** `ProbeIndexDocuments._refusal`, `FakeIndexDocuments._refusal`; `IndexDocuments` PAUSE branch
**From:** scenario 2.3 (2.3-an-embedding-refusal-stops-and-a-server-error-stays-inside-the-three-tries)

## Quirk: Embedding outcomes live on the index double until a port exists

**Quirk:** There is no Embedding port yet; acceptance and usecase arm outcomes on Probe/Fake `_refusal`.
**Where:** `acceptance/clients/application/probe_index_documents.py`, `backend/usecase/tests/fake/document/fake_index_documents.py`
**Implication:** A real freellmapi adapter must map the same three outcomes into `_refusal` / PAUSE semantics.
**From:** scenario 2.3 (2.3-an-embedding-refusal-stops-and-a-server-error-stays-inside-the-three-tries)
