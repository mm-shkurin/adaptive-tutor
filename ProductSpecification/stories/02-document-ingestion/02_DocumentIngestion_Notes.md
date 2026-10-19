# PDF documents — Notes

## Warnings

### Functional Warnings

- The interview's 1–50 MB floor is pinned here as 1,048,576–52,428,800 bytes so the size cannot change units between the upload, the stored value, and the row. A real lecture PDF is often under 1 MB and will be refused. That floor was the interview's choice.
- The interview left a slow index "still visible". It did not name an end. This spec ends indexing at 5 minutes, at 2,000 pieces, or after 3 tries, whichever comes first. Those three numbers are not in the interview.
- A failed row is required. The shared mockup shows only «Готов» and «В процессе».
- The mockup's «Создать презентацию» is story 3. This story is the PDF zone and this person's PDF rows.
- Deleting the account does not remove documents yet. Story 1 records that attachment for when documents exist. This story only stores the owner.
- There is no way to remove one document. Uploading again adds a second copy and leaves the first.

### UI/UX Warnings

- An older status reply must not replace a newer one on the row.
- Leaving the screen before the upload is accepted leaves the list unchanged.

### Technical Warnings

- Do not mark a document ready when the virus check or the search store is down, slow, or unreadable. Missing settings fail at startup.
- A retry of indexing must not create a second document and must not scan the file again.
- Tables are text with the surrounding paragraphs, written so a person can read the table. They are not a separate record.

## Suggestions & Future Enhancements

### Functional Suggestions

- When account deletion removes a person's other rows, it removes these documents and their pieces too.

### UI/UX Suggestions

- None for this story. The failed row is a requirement, not a suggestion.

### Technical Suggestions

- Keep the virus check and the search store fake in tests. The suite does not need the live services.

## Technical Notes

### Load Considerations

Expected load is 1–2 uploads a day, files of 1–50 MB, and a 10 MB PDF indexed in under 30 seconds (P95 25 seconds, P99 40 seconds in `ExpectedLoad.md`). The story's bar for that file is 30 seconds. Peak chat is not this story's path. The list page of 50 and the 2,000-piece stop are the bounds a single person can still exceed on purpose.

### Security Considerations

See the hazard scan below. The file's text, secrets, stack traces, and paths stay out of errors and logs.

### Infrastructure Notes

The original file is deleted when indexing ends, ready or failed. It is not kept for a later retry. The app does not start without the virus-check and search-store settings.

### Integration Notes

See `interview.md`.

- PDF reading and table text: PyMuPDF. Tables become Markdown inside the piece, not a separate table index.
- Search store: self-hosted Qdrant. The interview names embedding size 384. `ExpectedLoad.md` names 1536 or 768. The interview stands until a measured model replaces it.
- Embeddings: freellmapi, OpenAI-compatible embeddings, free tier.
- Virus check: ClamAV.
- Indexing runs after the upload answer. The interview allows a background task or a worker. Either way the status rules above hold.
- Rate limit is per signed-in person. The interview's "per IP" applied when there was no sign-in.

## Additional Context

See `interview.md`. The line that says the MVP has no authentication is withdrawn. The document belongs to the signed-in person.

Story 1's acceptance suite does not cover documents. Nothing in the backend implements this upload yet.

## Hazard scan

Groups scanned: hz-01, hz-02, hz-03, hz-04, hz-05, hz-06, hz-07, hz-08.

| Group | Verdict | Disposition |
|-------|---------|-------------|
| hz-01 | GAP on units, the 500-token edge, and text | Folded: size is one byte count from upload to row; 1,048,576 and 52,428,800 are the edges; a 500-token piece is kept and a shorter one is joined; empty text is refused; the name and the text survive unchanged. No prices, so currency does not fire. |
| hz-02 | GAP on a retry after a partial run, the last write, and a bad answer from the virus check or the search store | Folded: a retry does not scan again and does not create a second document; a last-step failure leaves no pieces and no search entries; a timeout or unreadable answer refuses the file or fails the document. The 5-minute stop is the deadline. Seam with hz-03 closed by the single piece set. |
| hz-03 | GAP on overlapping checks, a stale read, and a dropped or repeated indexing run | Folded: two requests on the last rate slot accept one; the next list read shows the new row; search finds text only once ready and not after failure; a document whose indexing never started still finishes; three failures do not block the next document. |
| hz-04 | GAP on the status steps and on deleting the file | Folded: the only forward steps are waiting, indexing, then ready or failed; a finished document is not indexed again; the file delete touches this document only; failure leaves no orphan pieces. Schema evolution does not fire: first schema. Account deletion is story 1's later attachment, not this story. |
| hz-05 | GAP on search, server-set fields, encoding, and a failed check | Folded: search is this person's only; a guest opening by id looks like a missing document; the client cannot set id or page count; a script tag is text; quotes are not a command; an unreadable rate count refuses the upload. |
| hz-06 | GAP on the list, the file name, a huge PDF, and leftover work | Folded: 50 per page, newest first; 255-character names; stop at 2,000 pieces or 5 minutes. After failures the original files are gone and a further upload still works. Seam with hz-01 closed by the byte edges. |
| hz-07 | GAP on the minute boundary, a partial index, startup, and logs | Folded: the next minute accepts again; one failed table fails the document and is named; a ready row has no failure reason; missing settings refuse to start; logs omit the file text and secrets. The 30-second bar is a speed target, not an expiry. |
| hz-08 | GAP on a late reply and on skipping the screen | Folded: a late reply does not cover a newer status; the server still refuses what the screen would have blocked. |

Seams, and the one guard that closes each:

- Byte size is both the unit and the cap (hz-01, hz-06): one byte under 1,048,576 and one byte over 52,428,800.
- Piece size is both the floor and the explosion (hz-01, hz-06): 500 tokens minimum, 2,000 pieces maximum.
- Text is both a round-trip and an injection sink (hz-01, hz-05): stored unchanged, shown as text, not executed.
- One piece set covers a repeated run and an overlapping run (hz-02, hz-03).
- The saved row still finishes, and a last-step failure leaves nothing searchable (hz-02, hz-03, hz-04).
- Virus-check and search-store failure stay visible and never look ready (hz-02, hz-05, hz-07).
- The rate window, the overlapping last slot, and an unreadable counter are one refusal (hz-03, hz-05, hz-06, hz-07).
