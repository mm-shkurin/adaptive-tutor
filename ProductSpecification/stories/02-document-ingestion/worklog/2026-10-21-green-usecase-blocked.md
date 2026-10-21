# 2026-10-21 — backend scenario 4.1 blocked in green-usecase

Docker was not started. The user said containers come later.

## Progress

`progress.md` is unchanged on purpose. Scenario 4.1 stays at `[~] green-usecase`. Do not mark it done.

Frontend lane, already committed by the other session: scenario 1.1 is past `green-frontend`, next checkbox is `red-frontend-api` (`1664e0b`, `65f0436`). This note is not that lane.

## What passed

Uncommitted production code makes every check in `TestAcceptedPdfBecomesReady` pass except the last one. `pytest` from `backend/`: 1 failed. Failure is `backend/usecase/tests/statements/document_statements.py:149`, `then_the_neighbours_file_is_still_there`: `neighbour_file is None`, expected the neighbour PDF bytes.

The skip marker is back on the test, with the old reason `RED: SubmitDocument.submit raises NotImplementedError`. That reason is stale. `submit` is implemented in the working tree.

## Uncommitted files

Not committed, because the test is red.

- `backend/domain/document/document.py` — `accepted`, `indexing`, `ready`
- `backend/domain/document/extracted_text.py` — NFC text; a paragraph of 500 tokens stays whole; a shorter one is joined onward
- `backend/usecase/document/submit_document.py` — stores a waiting document and returns it before indexing
- `backend/usecase/document/index_documents.py` — claims the next waiting document, writes pieces, marks ready, deletes that document's file
- `backend/usecase/document/read_document.py`
- `backend/usecase/document/search_documents.py`
- `backend/usecase/document/read_stored_file.py`

## Problem

The spec and the test both say: when this person's indexing finishes, this person's file is gone and the neighbour's file is still there.

The test prepares the neighbour by calling the same `index_waiting`. That call deletes the neighbour's file. The later assertion then fails. Deleting only some finished documents by piece count or by "has a table" would make this fixture green and leave other finished documents with their file still stored.

The journey note is `summaries/4.1-an-accepted-pdf-becomes-ready-and-its-text-and-tables-can-be-searched.md`.
