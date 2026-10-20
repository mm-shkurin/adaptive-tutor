# Decision: A worker indexes an accepted PDF

**Date**: 2026-10-20 **Scenarios**: 4.1

The upload must be answered before indexing finishes, and parsing a lecture must not run in the process that answers sign-in and the list.

| Rejected | Why |
|----------|-----|
| Same-process task after the answer | The index would share the process that serves every other request, and a restart of that process is the only place an unstarted job lives. |

**Chosen**: A separate worker claims saved waiting documents and indexes them. The upload process stores the row and the file and returns waiting.

## Model

- Document: id, owner, name, size in bytes, page count, piece count, status, error. The client sends the file only.
- Status moves only waiting → indexing → ready, or waiting → indexing → failed.
- Ports: an intake that stores the waiting row and the bytes as one unit; a file store; a PDF reader; a piece index keyed by document id; an embedder. The worker is the only caller that advances status.
- Pieces: a piece of 500 tokens is kept; a shorter piece is joined onward; tables are markdown inside the piece; text is stored unchanged in NFC.
- Search for this person reads that document's pieces. A neighbour's pieces are a different document.

## Edge Cases

| Case | Behavior |
|------|----------|
| The file write or the row write fails | Neither remains. No waiting row without its bytes, and no file without a row. |
| An empty document id is asked to delete or replace | Nothing is deleted and no pieces change. |
| Two claims index one document | One piece set. The second claim does not append. |
| This document's pieces are replaced | The neighbour's pieces and file stay. |
| Indexing never started | The waiting row is still claimed later and reaches ready or failed. |
| Indexing ends, ready or failed | This document's original file is gone. |
