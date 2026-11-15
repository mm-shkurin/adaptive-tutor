# Chat — API Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with refusals that store nothing, then an empty chat, then a whole reply, then the four turns, then a failed vector run or reply, then switching document.

## 1. Prerequisite guards

### 1.1 A call with no session is refused like a missing chat

Tier: 2 (hz-05, hz-08)

```gherkin
Scenario Outline:
Given a person who is not signed in
When the person <asks>
Then the refusal matches a missing chat
And nothing is stored

Examples:
  | asks |
  | reads the chat list |
  | reads a chat |
  | starts a chat |
  | opens a chat for a document |
  | sends a line |
```

### 1.2 A document that is not ready cannot be bound

Tier: 2 (hz-04, hz-08)

```gherkin
Scenario Outline:
Given a signed-in person
And a document of theirs that is <state>
When the person <binds> that document
Then the bind is refused because the document is not ready
And no chat is stored
And the document status is unchanged

Examples:
  | state | binds |
  | waiting | starts a chat on |
  | indexing | starts a chat on |
  | failed | starts a chat on |
  | a status that is not a known document status | starts a chat on |
  | waiting | opens a chat for |
  | indexing | opens a chat for |
  | failed | opens a chat for |
  | a status that is not a known document status | opens a chat for |
```

### 1.3 A person with no ready PDF cannot start a chat

Tier: 2 (hz-04, hz-08)

```gherkin
Given a signed-in person with no ready PDF
When the person starts a chat
Then the start is refused
And the chat list is empty
```

### 1.4 A session store failure is refused like a missing chat

Tier: 2 (hz-05)

```gherkin
Scenario Outline:
Given a signed-in person's session store fails
When the person <asks>
Then the refusal matches a missing chat
And nothing is stored

Examples:
  | asks |
  | reads the chat list |
  | reads a chat |
  | starts a chat |
  | opens a chat for a document |
  | sends a line |
```

---

## 2. New chat

### 2.1 A new chat binds the selected ready PDF and starts empty

Tier: 1 (hz-04)

```gherkin
Given a signed-in person
And a selected ready PDF that is older than another ready PDF
When the person starts a chat on the selected PDF
Then the chat is bound to the selected PDF
And the thread is empty
And the list row shows that PDF's name and no preview
```

### 2.2 A new chat with nothing selected binds the newest ready PDF

Tier: 2 (hz-04, hz-05)

```gherkin
Given a signed-in person with two ready PDFs and nothing selected
And a neighbour who owns a newer ready PDF
When the person starts a chat
Then the chat is bound to the person's newer PDF
And the neighbour's PDF is not bound
And the thread is empty
```

---

## 3. Send validation

### 3.1 A blank line is refused and nothing is stored

Tier: 2 (hz-08)

```gherkin
Scenario Outline:
Given a signed-in person with an askable chat
When the person sends <line>
Then the send is refused
And the thread is unchanged

Examples:
  | line |
  | an empty line |
  | a line of only spaces |
```

### 3.2 An unknown or null model or mode is refused and nothing is stored

Tier: 2 (hz-04, hz-05, hz-08)

```gherkin
Scenario Outline:
Given a signed-in person with an askable chat
When the person sends a line with <value>
Then the send is refused
And the thread is unchanged

Examples:
  | value |
  | a null model |
  | a null mode |
  | a model that is not in the list |
  | a mode that is not in the list |
  | an empty model |
  | an empty mode |
```

### 3.3 A send before the material can be asked stores nothing

Tier: 2 (hz-04, hz-07, hz-08)

```gherkin
Given a signed-in person whose chat cannot be asked yet
When the person sends a line
Then the send is refused
And the thread has no person line and no tutor line
```

### 3.4 An invalid examiner answer is refused

Tier: 2 (hz-04, hz-05, hz-08)

```gherkin
Scenario Outline:
Given a signed-in person with an open examiner question
When the person <answers>
Then the send is refused
And the question stays open
And no grade is stored

Examples:
  | answers |
  | sends a line instead of a choice |
  | chooses a choice that is not on the question |
```

### 3.6 Asking to be told when nothing is withheld is refused

Tier: 2 (hz-04, hz-05, hz-08)

```gherkin
Given a signed-in person with an askable chat that is not withholding
When the person asks to be told
Then the send is refused
And the thread is unchanged
```

---

## 4. Reply

### 4.1 A question is answered from this PDF with the model, the first page, and at most ten sources

Tier: 1 (hz-05, hz-06)

```gherkin
Given a signed-in person with an askable chat
And the PDF has more matching pieces than the reply uses, each with a starting page
And a neighbour's pieces are in the search store
When the person sends a question naming a listed model in Professor mode
Then the tutor line arrives whole
And the tone is academic
And the model on the line is the model that was asked
And the page is the starting page of the first retrieved piece
And the sources are only pieces of this PDF
And none of the neighbour's pieces are sources
And there are at most ten sources
And each source shows that piece's text and starting page
And the citation is a page, not a slide
```

### 4.2 Nothing in the material stores that sentence and no sources

Tier: 2

```gherkin
Given a signed-in person with an askable chat
And the question matches nothing in this PDF
When the person sends the question
Then the tutor says it is not in the material
And the sources are empty
And the model did not answer
```

### 4.3 A piece with no page is still answered and the source has no page

Tier: 2 (hz-04)

```gherkin
Given a signed-in person with an askable chat
And the retrieved piece has no page
When the person sends a question
Then the tutor answers
And the bubble has no page
And the source shows the piece text without a page
```

### 4.4 The list shows this person's document name and last line, newest first

Tier: 2 (hz-05, hz-07)

```gherkin
Given a signed-in person with two chats, the newer one spoken in last
And a neighbour with a chat of their own
When the person reads the chat list
Then each row shows that chat's document name and the last person line
And a chat with no person line has no preview
And the newer chat is first
And the neighbour's chat is absent
And every chat this person owns is listed
```

### 4.5 A multibyte line and a multibyte piece round-trip unchanged

Tier: 2 (hz-01)

```gherkin
Given a signed-in person with an askable chat
And a retrieved piece whose text contains a multibyte character
When the person sends a line that contains a multibyte character
Then the thread shows that line unchanged
And the source shows that piece unchanged
```

### 4.6 The same attempt stores one person line and one tutor line

Tier: 2 (hz-02)

```gherkin
Given a signed-in person with an askable chat
When the person delivers the same attempt twice
Then the thread contains one person line and one tutor line
And the model is called once
```

### 4.7 An omitted model is auto and an omitted mode is Professor

Tier: 2 (hz-04, hz-05)

```gherkin
Given a signed-in person with an askable chat
When the person sends a line and omits the model and the mode
Then the tutor line's model is auto
And the turn is Professor
```

### 4.8 Two different attempts in flight both remain in the thread

Tier: 2 (hz-03, hz-04)

```gherkin
Given a signed-in person with an askable chat
When two different attempts interleave between the read of the thread and the write
Then both person lines remain in the thread
And neither replaces the other
```

### 4.9 The same attempt interleaved stores one person line

Tier: 2 (hz-03)

```gherkin
Given a signed-in person with an askable chat
When two deliveries of the same attempt interleave between the read of that attempt and the write
Then the thread contains one person line and one tutor line
And the model is called once
```

### 4.10 Two chats created at the same instant keep their order

Tier: 2 (hz-06)

```gherkin
Given a signed-in person with two chats created at the same instant
When the person reads the chat list twice
Then the two chats stay in the same order
```

### 4.11 A long chat list is read a constant number of times

Tier: 2 (hz-06)

```gherkin
Given a signed-in person with a long list of chats
When the person reads the chat list
Then the chat store is read a constant number of times
And every chat this person owns is listed
```

---

## 5. Modes

### 5.1 Five-year-old answers in plain words with a page

Tier: 2 (hz-05)

```gherkin
Given a signed-in person with an askable chat
And the retrieved piece has a starting page
When the person sends a question as a five-year-old
Then the tutor answers in plain words
And the line has that page
```

### 5.2 Socratic stores a question and no page

Tier: 2 (hz-04)

```gherkin
Given a signed-in person with an askable chat
When the person sends a question in Socratic mode
Then the tutor stores a question
And the line has no page
And the sources are empty
```

### 5.3 A try after a withheld question answers with a page

Tier: 2 (hz-04)

```gherkin
Scenario Outline:
Given a signed-in person whose tutor is withholding
When the person sends <line>
Then that line is kept as the try
And the tutor answers with a page

Examples:
  | line |
  | a non-empty try |
  | a non-empty line that asks to be told |
```

### 5.4 The tell control answers with a page and stores no person line

Tier: 2 (hz-04)

```gherkin
Given a signed-in person whose tutor is withholding
When the person uses the tell control
Then the tutor answers with a page
And no person line is added
```

### 5.5 Examiner posts the first question with four choices and no page

Tier: 2 (hz-04)

```gherkin
Given a signed-in person with an askable chat
When the person chooses Examiner
Then the tutor posts one question immediately
And the question has four choices
And the right choice is not marked
And the question has no page
```

### 5.6 Continuing the examiner series with the supported choice

Tier: 2 (hz-04)

```gherkin
Given a signed-in person who has graded fewer than two examiner questions
And an examiner question is open
When the person chooses the choice the piece supports
Then the grade is right
And the grade shows that piece's starting page
And the thread gains exactly one new question
```

### 5.7 Grading the third examiner question

Tier: 2 (hz-04)

```gherkin
Given a signed-in person with the third examiner question open
When the person chooses a choice the piece does not support
Then the grade is wrong
And the grade shows that piece's starting page
And no further question is posted
```

### 5.8 A second answer to the same question does not grade again

Tier: 2 (hz-02, hz-04)

```gherkin
Given a signed-in person whose examiner question is already graded
When the person chooses again
Then the grade is unchanged
And the thread has one grade for that question
```

### 5.10 After the third grade the next line is academic and is not a quiz

Tier: 2 (hz-04)

```gherkin
Given a signed-in person whose examiner series has three grades
When the person sends a line
Then no fourth question appears
And the tutor answers in an academic tone with a page
And the quiz list does not contain the three questions
```

### 5.11 A try and the tell control interleaved release once

Tier: 2 (hz-03)

```gherkin
Given a signed-in person whose tutor is withholding
When a try and the tell control interleave between the read of the withhold and the write
Then the tutor answers with a page once
And the thread has one release
```

### 5.12 Two stale copies of a withhold do not lose the release

Tier: 2 (hz-03)

```gherkin
Given a signed-in person whose tutor is withholding
And two stale copies of that withhold
When one copy is released by a try and the other by the tell control
Then one release is kept
And the second save does not drop that release
```

### 5.13 Two answers to one open question interleaved grade once

Tier: 2 (hz-03)

```gherkin
Given a signed-in person with an open examiner question
When two choices interleave between the read of the question and the write
Then the thread has one grade
```

### 5.14 Two stale copies of a grade do not double it

Tier: 2 (hz-03)

```gherkin
Given a signed-in person with an open examiner question
And two stale copies of that question
When each copy saves a different choice
Then the thread has one grade
And the second save does not add another grade
```

### 5.15 Choosing Examiner while a question is open does not post another

Tier: 2 (hz-04)

```gherkin
Given a signed-in person with an open examiner question
When the person chooses Examiner again
Then the open question stays the only unanswered question
```

### 5.17 A stopped examiner series ignores a new series, a choice, and tell

Tier: 2 (hz-04)

```gherkin
Scenario Outline:
Given a signed-in person whose examiner series has stopped
When the person <acts>
Then the series stays stopped
And the thread gains no question and no grade

Examples:
  | acts |
  | chooses Examiner |
  | chooses a choice |
  | asks to be told |
```

---

## 6. Vector run and a failed reply

### 6.1 Opening a ready PDF with no vectors makes it askable from the stored text

Tier: 2 (hz-04)

```gherkin
Given a signed-in person
And a ready PDF that has stored pieces and no vectors
When the person opens a chat on that PDF
Then the pieces are vectorized from the stored text
And the chat becomes askable
And the library row stays ready
```

### 6.2 A failed vector run leaves the document ready and the chat not askable

Tier: 2 (hz-04)

```gherkin
Given a signed-in person
And a ready PDF whose vector run fails
When the person opens a chat on that PDF
Then the chat says the material cannot be asked yet
And no tutor line is stored
And the library row stays ready
```

### 6.3 The next open after a failed vector run tries again

Tier: 2 (hz-02)

```gherkin
Given a signed-in person
And a ready PDF whose vector run failed on the previous open
When the person opens the chat again and the run succeeds
Then the chat becomes askable
And the library row stays ready
```

### 6.4 A vector run that stops midway does not store those pieces twice

Tier: 2 (hz-02, hz-04, hz-07)

```gherkin
Given a signed-in person
And a ready PDF whose vector run stored some pieces and then failed
When the person opens the chat again
Then the pieces already stored are not stored again
And the pieces after the failed one are still attempted
And the run records which piece failed
And the person-facing notice stays the fixed sentence
And the chat stays not askable until the run finishes
```

### 6.5 Opening a PDF that already has vectors does not write them again

Tier: 2 (hz-02, hz-04)

```gherkin
Given a signed-in person
And a ready PDF that already has vectors
When the person opens a chat on that PDF twice
Then the vectors are not written again
```

### 6.6 A failed reply keeps one person line for that attempt

Tier: 2 (hz-02)

```gherkin
Given a signed-in person with an askable chat
And the reply fails after the vectors are ready
When the person repeats that same attempt
Then the thread has one person line
And the thread has no tutor line
```

### 6.7 A new attempt after a failed reply is kept

Tier: 2 (hz-02)

```gherkin
Given a signed-in person whose last reply failed
When the person sends a new attempt
Then that person line is kept
```

### 6.8 A reply that misses the latency budget keeps one person line and no tutor line

Tier: 2 (hz-02, hz-04)

```gherkin
Given a signed-in person with an askable chat
When the reply does not finish within the chat latency budget
Then the thread has one person line
And the thread has no tutor line
And the reply work does not continue after the budget
```

### 6.9 The latency budget is pinned just before, at, and just after expiry

Tier: 2 (hz-02, hz-07)

```gherkin
Scenario Outline:
Given a signed-in person with an askable chat
And the clock is fixed <when>
When the person sends a line
Then <outcome>

Examples:
  | when | outcome |
  | just before the chat latency budget expires | the tutor line is kept |
  | at the instant the chat latency budget expires | the thread has one person line and no tutor line, and the reply work stops |
  | just after the chat latency budget expires | the thread has one person line and no tutor line, and the reply work stops |
```

### 6.10 Two opens interleaved do not store a piece twice

Tier: 2 (hz-03)

```gherkin
Given a signed-in person
And a ready PDF that is being vectorized
When two opens interleave between the read of which pieces have vectors and the write
Then each piece has one vector
```

### 6.11 A vector write with no document leaves every neighbour untouched

Tier: 2 (hz-04)

```gherkin
Given a signed-in person
And a neighbour who owns a ready PDF with vectors
When a vector write is attempted with no document
Then no piece and no vector is written
And the neighbour's vectors are unchanged
```

---

## 7. Switching document

### 7.1 Switching document keeps the previous chat and opens the chosen PDF

Tier: 2 (hz-04)

```gherkin
Scenario Outline:
Given a signed-in person with a chat that already has a person line
When the person switches to <chosen>
Then the previous chat still has that person line
And the opened chat is <opened>

Examples:
  | chosen | opened |
  | a ready PDF that already has a chat | the newest chat for that PDF |
  | a ready PDF with no chat | a new empty chat for that PDF |
```

### 7.2 A reply to the chat just left stays on that chat

Tier: 2 (hz-04)

```gherkin
Given a signed-in person who sent a line to one chat
When the person switches to another chat before that reply is stored
Then the reply is stored on the chat that was sent
And the chat now open does not gain that reply
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `a person who is not signed in` | No `Authorization` bearer token |
| `the refusal matches a missing chat` | HTTP 404 `{"code":"chat_not_found","message":"Chat was not found"}`, identical for no session, unknown id, and another owner |
| `nothing is stored` / `no chat is stored` / `the thread is unchanged` | No new chat row and no new line row |
| `a document of theirs that is <state>` | Own document with status `waiting`, `indexing`, or `failed` |
| `the bind is refused because the document is not ready` | HTTP 400 `{"code":"document_not_ready","message":"Document is not ready"}` |
| `the start is refused` | HTTP 400 `{"code":"no_ready_document","message":"No ready document"}` |
| `starts a chat` | `POST /api/v1/chats` |
| `starts a chat on the selected PDF` | `POST /api/v1/chats` with that `document_id` |
| `opens a chat for a document` / `switches to` | `POST /api/v1/chats/open` |
| `reads a chat` / `opens a chat on that PDF` | `GET /api/v1/chats/{id}` |
| `reads the chat list` | `GET /api/v1/chats` |
| `sends a line` / `sends a question` | `POST /api/v1/chats/{id}/messages` with a new `Idempotency-Key` |
| `the same attempt` | The same `Idempotency-Key` |
| `a new attempt` | A different `Idempotency-Key` |
| `an empty line` / `a line of only spaces` | HTTP 400 `{"code":"empty_message","message":"Message is empty"}` |
| `a null model` / `a model that is not in the list` | HTTP 400 `{"code":"invalid_model","message":"Model is not allowed"}` |
| `a null mode` / `a mode that is not in the list` | HTTP 400 `{"code":"invalid_mode","message":"Mode is not allowed"}` |
| `cannot be asked yet` / `the material cannot be asked yet` | `askable` false and `notice` «Материал пока нельзя спросить.» |
| `the send is refused` while not askable | HTTP 409 `{"code":"not_askable","message":"Material cannot be asked yet"}` |
| `sends a line instead of a choice` | HTTP 400 `{"code":"choice_required","message":"Choice is required"}` |
| `a choice that is not on the question` | HTTP 400 `{"code":"choice_unknown","message":"Choice is not on the question"}` |
| `asks to be told` when not withholding | HTTP 400 `{"code":"tell_unavailable","message":"Nothing is withheld"}` |
| `the tutor line arrives whole` | One tutor line in the response body, not a stream |
| `the tone is academic` / `the turn is Professor` | Tutor `mode` is `professor` and `kind` is `reply` |
| `answers in plain words` | Tutor `mode` is `five_year_old` and `kind` is `reply` |
| `the model on the line is the model that was asked` | Tutor `model` equals the requested id |
| `the model did not answer` / `it is not in the material` | Tutor text «Этого нет в материале.», `model` null, `sources` [] |
| `at most ten sources` | `sources.length` ≤ 10. Bubble `page` is `sources[0].page` |
| `the citation is a page, not a slide` | `page` is an integer. The payload has no slide field |
| `no preview` | `preview` null |
| `the last person line` | `preview` is that line's `text` |
| `the newer chat is first` | List order is newest `created_at`, then higher id |
| `a multibyte character` | A combining character, stored and returned byte-exact |
| `two different attempts are in flight` | Two concurrent posts with different `Idempotency-Key` values |
| `stores a question` / `withholding` | Tutor `kind` `withheld`, `page` null, `sources` [] |
| `uses the tell control` | Body `{"tell": true}` and no `text` |
| `chooses Examiner` | Body `{"mode":"examiner"}` with no `text` while no series is open |
| `four choices` | `kind` `question`, `choices` length 4, no `correct` on the question |
| `the choice the piece supports` | The choice id the fake marked from the retrieved piece |
| `the grade is right` / `the grade is wrong` | `kind` `grade`, `correct` true or false, `page` set |
| `chooses again` | A second `choice_id` for a question that already has a grade |
| `the quiz list does not contain the three questions` | No quiz row is written. Story 7's list has nothing from this series |
| `vectorized from the stored text` | Embedding input is the piece `body`. Dimension 384. No file is re-read |
| `the library row stays ready` | Document `status` remains `ready` |
| `the vector run fails` / `the reply fails` | Fake embedding, search, or model returns an error, times out, or a malformed body |
| `the pieces already stored are not stored again` | Those piece ids remain one vector each |
| `the chat latency budget` | `ProductSpecification/ExpectedLoad.md` chat P99 of 5 seconds. Inner work is cancelled when it is spent |
| `session store fails` | The session lookup times out or errors. The response is still `chat_not_found` |
| `interleave between the read` and `the write` | A latch between the existence read and the insert, so both callers pass the read before either writes |
| `the model is called once` | The chat-completions fake records one call for that `Idempotency-Key` |
| `the chat store is read a constant number of times` | The repository call count does not grow with the number of chats |
| `the run records which piece failed` | The stored failure names that piece's ordinal. The notice stays «Материал пока нельзя спросить.» and does not include the piece text |
| `a vector write is attempted with no document` | The vector port is invoked with an empty document scope |
| `the clock is fixed` | The test clock is set just before, at, and just after the 5 second budget |
| `the chat store is down` | PostgreSQL connection refused. HTTP 503 `{"code":"unavailable","message":"Chat store is unavailable"}` |
