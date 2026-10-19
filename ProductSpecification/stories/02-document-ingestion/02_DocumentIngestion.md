# PDF documents

## Brief Description

A signed-in person uploads a PDF. The app checks it, indexes its text and tables, and shows when that document is ready.

## Flow

1. A guest is turned away from upload, from the list, and from a document opened by id. The refusal looks the same as a missing document.
2. The person picks a PDF. Checks on the screen are not the gate: the same file sent without them is still refused.
3. The app refuses at once, and adds no row, when the file is missing, not a PDF, empty of text, under 1,048,576 bytes, over 52,428,800 bytes, encrypted, or fails the virus check. A virus check that times out or answers unreadable is the same refusal.
4. An accepted file is answered at once. The next list read shows it as waiting, then indexing. A saved document whose indexing did not start still reaches ready or failed.
5. Indexing keeps the text and the tables with the surrounding text, readable as a table. Pieces follow paragraphs and headings. A piece of exactly 500 tokens is kept; a shorter one is joined onward. The file name and the text are stored and shown unchanged.
6. The only forward steps are waiting to indexing, then indexing to ready or to failed. Any other step is refused. The person cannot set the id, the owner, the status, the page count, the piece count, or the error.
7. Ready text is searchable by this person only. A failure, including one table or one piece, leaves nothing searchable, names that part, and removes this document's pieces. The original file is gone either way. A neighbour document is untouched.
8. A second click of one submission stores one document, even when the two requests overlap. Uploading that PDF again creates another document. Indexing a document again does not add a second set of pieces, and does not run the virus check again.

## Acceptance Criteria

- 1,048,576 bytes and 52,428,800 bytes are accepted. One byte under and one byte over are refused. The stored size and the size on the row are that same count.
- A file name of 255 characters is kept. A longer name is refused. A name or a failure reason that contains a script tag is shown as text. Quotes in the PDF are not a search command. Search does not change with the server's language.
- A 10 MB PDF is ready within 30 seconds. Indexing that has not finished in 5 minutes, or that would store more than 2,000 pieces, is failed. It is tried at most 3 times. A document that keeps failing does not block the next one.
- A failure on the last step leaves no pieces and no search entries, and the document is not ready. A ready row has no failure reason.
- The sixth upload inside one minute is refused, including when two uploads arrive together on the last free slot. Those five stay. An upload at the start of the next minute is accepted. If the rate count cannot be read, the upload is refused.
- The list returns at most 50 documents, newest first. A late reply does not paint over a newer status.
- If the virus check or the search store is not configured, the app does not start. If the search store times out or answers unreadable, the document is failed, not ready.
- Errors name the reason. The response and the log never include the file's text, another person's data, a secret, a stack trace, or a file path.

## Validation Rules

| Field | Rule |
|-------|------|
| File | A PDF. Anything else, or an omitted file, is refused. |
| Size | 1,048,576–52,428,800 bytes. Empty of text is refused. |
| Name | 1–255 characters. |
| Protection | Encrypted is refused. A virus is refused. |
| Rate | Five accepted uploads a minute for this person. |
| Ownership | The signed-in person only. |

## Screen States

- Documents, empty.
- List row: waiting, indexing, ready, failed with a reason.
- Upload refused, list unchanged.
- Upload accepted, the new row is on the next read.

## Core Requirements

- Slides from photos, other office formats, scanned pages, pictures, and formulas are other stories.
- The signed-in person owns the document. There is no instructor door.
- Chat is a later story. A ready document's status stays readable and its pieces stay searchable.
- A finished document is not indexed again. The earlier copy stays as it was.
