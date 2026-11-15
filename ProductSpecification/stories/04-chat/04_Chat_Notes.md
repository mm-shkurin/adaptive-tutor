# Chat — Notes

**Decisions accepted 2026-11-14.** The ten recommendations below were accepted as a set. They are now the rules in `04_Chat.md`. API and test specs are written from that file.

## Decisions

1. **Already-ready PDFs have no file and no page.** Story 2 deletes the file when indexing finishes, and pieces are `(document_id, ordinal, body)`. The interview still says the first chat open vectorizes that PDF and the citation names a page. Decision: vectorize from the stored piece text; cite a page only when indexing stored one (new uploads). An old piece with no page is still askable, and the source card shows the piece text without a page number. Do not refuse every ready PDF.
2. **What the person sees when the model or the search fails.** The interview's "cannot be asked yet" is the vector run, not a later model error. Decision: a failed or unfinished vector run shows that sentence, stores no tutor line, and retries on the next open. A later model or search error on a PDF that already has vectors stores the person's line, stores no tutor line, and the person can send again. No 30-second silence rule. Load stays ExpectedLoad: P95 under 3 seconds, P99 under 5 seconds. The same attempt uses `Idempotency-Key`, as document upload already does, so a retry is not a second person line and a new key is a new attempt.
3. **List size.** The interview sets no page size. Decision: no page size until one is chosen. A row shows the document name and the last person line, as the mockup does. The screen may shorten the preview visually.
4. **How many pieces, and which page.** ExpectedLoad searches top-10. Decision: retrieve up to 10 pieces. The bubble cites the starting page of the first of those. A piece that crosses a page still cites that starting page.
5. **New chat and switching document.** Decision: a new chat binds to the ready PDF already selected, or to the newest ready PDF if none is selected. No ready PDF means an empty state and send is refused. Switching keeps the old chat in the list unchanged and shows the newest chat for the PDF just chosen, or a new empty chat bound to it. A late reply for the chat the screen has left is stored there and is not painted on the chat now shown.
6. **Socratic release.** Decision: while withholding, the tutor stores a question and no page. A try is any non-empty person line. Asking to be told is a control on that question, not a phrase match.
7. **Examiner shape.** Decision: choosing Examiner on a bound chat posts the first question immediately. Each question has four choices and one right choice, the choice the retrieved piece supports. The page is shown on the grade. A second answer to the same question does not grade again. After the third grade, the series stops and the next person line is answered with a page in the academic tone. Choosing Examiner again does not start a second series.
8. **Narrow layout.** The mockup hides history and Sources below 960px. Decision: both stay reachable. That `display: none` is not the product.
9. **Guest and a dead session.** Decision: a guest sees the landing. An API call with no session is refused the same way as a missing chat (`chat_not_found`, one message). Do not add a new startup gate for `FREE_LLM_API_KEY`; a missing key fails the send, and `QDRANT_URL` stays the existing startup check.
10. **Line length and omitted model.** Decision: a blank or whitespace-only line is refused and nothing is stored. No length cap until one is chosen. An omitted model is `auto`. An omitted mode is Professor. Null or unknown is refused. The last choice is kept on this device.

Hazard-pass notes that are not interview decisions (duplicate click, connection baseline, script-tag round-trip, ignored extra fields) stay out of the main file until one of these answers promotes them.

Interview: `interview.md` (2026-11-14). The person's words for the paperclip stay there: «скрепка переводит на вкладку документы пока что».

## Warnings

### Functional Warnings

- Pieces today are `(document_id, ordinal, body)` and the reader concatenates pages. A page citation is impossible until indexing and the lazy run store the starting page on the piece. Already-ready PDFs get that page only when the lazy run re-reads the file. Story 2 deletes the original file after indexing, so a ready PDF may have no file left to re-read. If the file is gone, the lazy run cannot recover page numbers from bytes it no longer has. The text pieces are still in Postgres. The page has to be recovered from a re-read only when the file is still there; otherwise the open says the material cannot be asked yet and does not invent a page. This blocks a real citation for PDFs indexed before this story unless the file was kept. Story 2's decision was ephemeral file storage. Do not pretend those old pieces have pages.
- "Tried an answer" means a person line that is not a request to be told the answer. The request is the person asking to be told. A bare empty send is refused and is not a try.
- Examiner questions are choice questions drawn from retrieved pieces of this PDF. The right choice is the one the piece supports. The model does not grade itself.
- The quiz product (list, create, result, retry) is story 7 and does not read these three questions.
- Story 2 still fails a new upload when embedding refuses. The lazy run of an already-ready document must not reuse that failure transition.

### UI/UX Warnings

- The mockup citation "Слайд 12, страница 5" is placeholder text. This story shows the PDF page only.
- Mode buttons in the mockup only toggle a CSS class. The product changes the turn.
- The sources panel shows the page and the piece text. It does not open the PDF.

### Technical Warnings

- `POST /api/v1/chat/messages` today returns 202 `{"status":"accepted"}` and, when the acceptance probe is armed, waits inside `PeakChatHold`. `PeakChatClient` posts `{"content":"peak load baseline"}` with no document. Replacing the stub must keep that probe able to hold 15 requests so story 2's upload-during-peak-chat test stays green. The probe is not the student's send.
- `backend/domain/llm/llm_service.py` calls an infrastructure client and parses nothing. `backend/infrastructure/llm/freellmapi_adapter.py` sits outside `backend/adapters/`. Neither is the implementation. The client lives in an adapter. The domain does not import it.
- Qdrant has no client. `QDRANT_URL` is only a startup check.
- Embedding refusal tests are a fake seam, not a port.

## Suggestions

- No streaming. The tutor line arrives whole.
- The 50-row list, the 50-line thread window, the 5-source cap, the 4,000-grapheme line, and the 30-second reply budget were not in the interview. They are the bounds the hazard pass required so a test can go red. The list size matches the document list. The 2,000-piece cap is story 2's.

## Hazard fold

Dismissed: a test that posts an unknown field to freellmapi. That request is not our contract. Unknown fields on our own send are ignored. A test that embedding queries stay a constant count regardless of piece count was dismissed because each piece needs one embedding and story 2 already refuses a document past 2,000 pieces. "Call the model only after the database commit" was dismissed because the tutor line is the model's text; the guard is the opposite failure — no tutor line stored when the call fails, and a retry of that send does not add a second person line.

## Technical Notes

### Student API

The student contract is `ProductSpecification/api-specs/chats.yaml`. `POST /api/v1/chat/messages` stays the acceptance hold from story 2. It is not a student send. Reading a chat is the open that runs a missing vector pass to completion or to "cannot be asked yet" inside that response. There is no second background queue.

### Load

`ProductSpecification/ExpectedLoad.md`: 20 people × 5 chat requests in one minute, and one upload while 15 chats are in flight. No new ceiling was set.

### Integration

- Embeddings: freellmapi `POST /v1/embeddings`, 384 dimensions, all-MiniLM-L6-v2. Interview of story 2.
- Tutor text: freellmapi chat completions. The sketch client uses `http://localhost:3001/v1` and `FREE_LLM_API_KEY`.
- Qdrant: self-hosted, `QDRANT_URL` (default `http://localhost:6333`).
- Acceptance does not call the live model or the live Qdrant. Unit tests use fakes, as story 2 already decided.

### Security

- Owner scope matches documents: a missing session and a stranger's id return the same not-found refusal, with no body that distinguishes them.
- Tutor text and piece text are shown as text. A script in the PDF or in the reply is not markup.
- Logs and error bodies do not include the document text, another person's chat, a secret, a stack, or a file path.
