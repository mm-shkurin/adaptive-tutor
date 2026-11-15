# Chat

Decisions below were accepted on 2026-11-14 from `04_Chat_Notes.md`. The primary person is a signed-in student. The feature works when that student can open their own chat on a ready PDF, send a line, and read a whole tutor reply drawn from that PDF.

## Brief Description

A signed-in person talks with the tutor about one ready PDF. The reply comes from that document's vectors and names the page when the piece has one. The mode changes the turn. The tutor line arrives whole.

## Prerequisites

- The person is signed in. A guest sees the landing, as in story 1.
- The chat's document is a ready PDF owned by this person. Waiting, indexing, and failed documents cannot be bound.
- Vectors for that PDF have finished. Until they have, the material cannot be asked yet.

## Flow

1. A guest sees the landing. A signed-in person opens their own chats. A call with no session is refused the same way as a missing chat. Another person's chat or PDF cannot be chosen, and that refusal matches a missing chat.
2. The list shows this person's dialogs, newest first. Each row shows the document name and the last line the person wrote, or no preview when they have not written yet. There is no chosen page size. Each chat is bound to one ready PDF they own.
3. A new chat is empty. It binds to the ready PDF already selected, or to the newest ready PDF when none is selected. No ready PDF means an empty state, no chat is stored, and send is refused.
4. Switching document leaves every existing chat unchanged. The screen shows the newest chat already bound to the PDF just chosen, or a new empty chat bound to it. A reply that belongs to a chat the screen has left is stored on that chat and is not painted on the chat now shown.
5. The paperclip opens Documents. It sends no file and adds no library row.
6. A new PDF gets its vectors at indexing. The starting page is stored on each piece while the file is still in hand. An embedding refusal on that upload still fails the document. An already-ready PDF with no vectors is vectorized from the stored piece text when a chat on it is opened. A page is cited only when the piece has one. An old piece with no page is still askable, and its source card shows the text without a page number. Until the vector run succeeds, the chat says the material cannot be asked yet, stores no tutor line, and the library row stays ready. The next open tries again. A run that stops after storing some pieces does not store those pieces again.
7. A send is one attempt. Repeating that attempt does not add another person line. A later attempt does, even when the words match. A blank or whitespace-only line is refused and nothing is stored. No line-length cap is chosen. An omitted model is `auto`. An omitted mode is Professor. A null or unknown model, and a null or unknown mode, are refused and nothing is stored. The last model and the last mode stay on this device.
8. A send is answered from up to ten pieces of that chat's PDF only. The tutor line arrives whole, shows the model that ran, and cites the starting page of the first of those pieces. A piece that crosses a page still cites that starting page. Sources show each of those pieces: the page when it exists, and the piece text. When nothing matches, the tutor says it is not in the material, sources stay empty, and the model does not answer from itself.
9. When the PDF already has vectors and the model or the search fails, or the reply does not finish within the chat latency budget, the person's line is kept, no tutor line is stored, and the person can send again. The failure the person sees carries none of the document text, another person's chat, a secret, a stack, or a file path. A missing model key fails the send the same way. It does not stop the app from starting.
10. Professor answers in an academic tone with the page. Five-year-old answers in plain words with the page. While Socratic is withholding, the tutor stores a question and no page. A try is any non-empty person line. Asking to be told is a control on that question, not a phrase in the line. After a try or that control, the tutor answers with the page.
11. Choosing Examiner on a bound chat posts the first question immediately. Each question has four choices and one right choice, the choice the piece supports. The model does not grade itself. The page is shown with the grade, not on the unanswered question. A second answer to the same question does not grade again. After the third grade the series stops. The next person line is answered with a page in the academic tone. Those three questions are not a quiz.
12. On a narrow window the history and the sources both stay reachable.

## Acceptance Criteria

- A waiting, indexing, or failed document cannot be bound to a chat.
- A ready PDF with no stored page is still askable. The source shows the piece text without a page number.
- Empty retrieval stores a not-in-the-material reply and no sources.
- A failed or unfinished vector run leaves the document ready, stores no tutor line, and the next open runs it again without duplicating pieces already stored.
- A failed reply keeps one person line for that attempt and no tutor line.
- The citation is a PDF page, never a slide. The sources panel does not open the PDF.
- Examiner questions do not appear in the quiz list.
- An upload while fifteen chat accepts are held in flight is still answered before indexing finishes. That hold is the acceptance seam, not the student's reply.
- If the search store setting is unset, the app does not start, as story 2 already requires. Acceptance does not call the live model or the live search store.

## Validation Rules

| Field | Rule |
|-------|------|
| Document | A ready PDF owned by this person. Any other document is refused. A missing document and another person's document match a missing chat. |
| Session | No session matches a missing chat. |
| Model | One of `auto`, `auto:smart`, `auto:fast`, `qwen/qwen3-32b`, `meta-llama/llama-3.3-70b`, `google/gemini-2.0-flash`, `mistralai/mistral-small`, `deepseek/deepseek-chat`, `fusion`. Omitted means `auto`. Null or any other value is refused. |
| Mode | Professor, Five-year-old, Socratic, Examiner. Omitted means Professor. Null or any other value is refused. |
| Line | Empty or whitespace-only is refused and nothing is stored. No maximum length is chosen. |
| Attempt | Repeating one attempt stores nothing more. A new attempt is stored. |
| Examiner choice | One of the four choices on the open question. A second answer does not grade again. |

## Screen States

- Guest: the landing. No chat list and no composer.
- No ready PDF: empty state. Send is refused.
- No chats, or an empty thread on a new chat.
- Thread with the person's line, the tutor line, the model, and the page. Sources filled, or empty.
- A source without a page number.
- Material cannot be asked yet.
- Not in the material.
- Reply failed: the person's line remains, with no tutor line.
- Socratic withholding, then the answer with a page.
- Examiner choice, then right or wrong with a page. After the third grade, an academic answer.
- Paperclip opens Documents.
- Narrow window: history and sources still reachable.

## Core Requirements

- Vectors are 384-dimensional and stored in the project's search store. The reply uses only retrieved pieces of this document, at most ten. Chats stay on the server after sign-out.
- Citations, the sources panel, and the four modes are this story. The quiz list is story 7. Slide labels are story 3.
- The tutor line arrives whole. History and sources stay reachable on a narrow window.
