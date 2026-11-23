# Quizzes — API Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with refusals that store nothing, then an empty list, then create validation, then one stored quiz, then list projection, then grading, finish, resume, replay, and account delete.
> Channel timeouts and transport errors are specified in `06_Integration_Tests.md`. Acceptance uses the completions fake, never live freellmapi.

## 1. Prerequisite guards

### 1.1 A call with no session is refused like a missing quiz

Tier: 2 (hz-05, hz-08)

```gherkin
Scenario Outline:
Given a person who is not signed in
And a ready PDF
When the person <asks>
Then the refusal matches a missing quiz
And nothing is stored

Examples:
  | asks |
  | reads the quiz list |
  | reads a quiz |
  | creates a quiz |
  | answers a quiz |
  | advances a quiz |
  | plays a quiz again |
```

### 1.2 A session store failure is refused like a missing quiz

Tier: 2 (hz-05)

```gherkin
Scenario Outline:
Given a signed-in person's session store fails
When the person <asks>
Then the refusal matches a missing quiz
And nothing is stored

Examples:
  | asks |
  | reads the quiz list |
  | reads a quiz |
  | creates a quiz |
  | answers a quiz |
  | advances a quiz |
  | plays a quiz again |
```

### 1.3 A document that is not ready cannot start a quiz

Tier: 2 (hz-04, hz-05, hz-08)

```gherkin
Scenario Outline:
Given a signed-in person
And a document of theirs that is <state>
When the person creates a quiz on that document
Then the create is refused because the document is not ready
And nothing is stored
And the document status is unchanged

Examples:
  | state |
  | waiting |
  | indexing |
  | failed |
  | a status that is not a known document status |
```

### 1.4 A person with no ready PDF cannot start a quiz

Tier: 2 (hz-04, hz-08)

```gherkin
Given a signed-in person with no ready PDF
When the person creates a quiz
Then the create is refused because there is no ready document
And the quiz list is empty
```

---

## 2. Quiz list

### 2.1 An empty quiz list is the person's own list

Tier: 2

```gherkin
Given a signed-in person with no quiz
And a neighbour who has a quiz
When the person reads the quiz list
Then the list is empty
And the neighbour's quiz is not listed
```

### 2.2 An examiner series does not appear on the quiz list

Tier: 2

```gherkin
Given a signed-in person whose examiner series has three grades
And the person has no quiz
When the person reads the quiz list
Then the list is empty
```

---

## 3. Create validation

### 3.1 A blank topic is refused and nothing is stored

Tier: 2 (hz-05)

```gherkin
Scenario Outline:
Given a signed-in person with a ready PDF
When the person creates a quiz with <topic>
Then the create is refused because the topic is empty
And nothing is stored
And the model is not called

Examples:
  | topic |
  | an empty topic |
  | a topic of only spaces |
  | an omitted topic |
  | a null topic |
```

### 3.2 A question count outside 3, 5, and 8 is refused and nothing is stored

Tier: 2 (hz-05, hz-08)

```gherkin
Scenario Outline:
Given a signed-in person with a ready PDF
When the person creates a quiz with <count>
Then the create is refused because the question count is not allowed
And nothing is stored
And the model is not called

Examples:
  | count |
  | a null count |
  | 0 |
  | 1 |
  | 2 |
  | 4 |
  | 6 |
  | 9 |
  | -1 |
  | a count that is not a number |
```

---

## 4. Create

### 4.1 A quiz is stored from the selected ready PDF and opens on the first question

Tier: 1 (hz-04)

```gherkin
Scenario Outline:
Given a signed-in person
And a selected ready PDF that is older than another ready PDF
And the completions fake returns a valid quiz
When the person creates a quiz on the selected PDF with <asked>
Then one quiz is stored for that person
And the quiz is bound to the selected PDF
And the question count is <stored>
And the attempt is open on the first question
And each question has four choices and one stored correct choice
And the response hides the page and the correct choice
And the page on each question is a page of a retrieved piece
And the citation is a page, not a slide
And the model asked is auto
And the model is called once
And the list shows this quiz first with no completed score
And the neighbour's quizzes are not listed

Examples:
  | asked | stored |
  | the count omitted | 5 |
  | 3 | 3 |
  | 5 | 5 |
  | 8 | 8 |
```

### 4.2 The questions and the choices follow the topic's language

Tier: 2

```gherkin
Scenario Outline:
Given a signed-in person with a ready PDF
And the completions fake returns a valid quiz in the language it was asked
When the person creates a quiz with <topic>
Then the model is asked in the topic's language
And the questions and the choices are in the topic's language

Examples:
  | topic |
  | a Russian topic |
  | an English topic |
```

### 4.3 Topic, questions, and choices round-trip as Unicode

Tier: 2 (hz-01)

```gherkin
Given a signed-in person with a ready PDF
And a topic that normalizes to the maximum length and includes a combining mark and an emoji
And the completions fake returns questions and choices with a combining mark and an emoji
When the person creates a quiz with that topic, including surrounding spaces
Then the stored topic is the trimmed normalized topic
And the stored questions and choices equal the fake's text normalized
And reading the quiz returns those same characters
```

### 4.4 The same create attempt stores one quiz and a new attempt may store another

Tier: 2 (hz-02)

```gherkin
Given a signed-in person with a ready PDF
And the completions fake returns a valid quiz
When the person creates a quiz
Then one quiz is stored
And the model is called once
When the person repeats that same attempt
Then the same quiz is returned
And the model is still called once
And the list contains that quiz once
When the person creates a quiz as a new attempt
Then a second quiz is stored
And the model is called for the new attempt
```

### 4.5 Two creates in flight with the same attempt store one quiz

Tier: 2 (hz-02, hz-03)

```gherkin
Given a signed-in person with a ready PDF
And the completions fake returns a valid quiz
When two creates with the same attempt interleave before the quiz is stored
Then one quiz is stored
And the model is called once
And both responses are that quiz
And the list contains that quiz once
```

---

## 5. Create failures

### 5.1 An empty search for the topic stores nothing

Tier: 2 (hz-02, hz-05)

```gherkin
Given a signed-in person with a ready PDF
And the topic matches no retrieved piece
When the person creates a quiz
Then the create is refused because nothing was found
And nothing is stored
And the model is not called
```

### 5.2 A reply of the wrong shape stores nothing and does not pin the attempt

Tier: 2 (hz-02, hz-06)

```gherkin
Scenario Outline:
Given a signed-in person with a ready PDF
And the completions fake returns <shape>
When the person creates a quiz
Then the create is refused because the quiz could not be assembled
And nothing is stored
And that attempt did not call the model a second time
When the fake returns a valid quiz and the person repeats that same attempt
Then one quiz is stored
And the model is called once for the successful try

Examples:
  | shape |
  | fewer questions than were asked |
  | more questions than were asked |
  | a question without four choices |
  | a question with no correct choice |
  | a question with two correct choices |
  | a page that was not in the retrieved pieces |
```

### 5.3 A failed last write leaves no quiz, no questions, and no attempt

Tier: 2 (hz-02)

```gherkin
Given a signed-in person with a ready PDF
And the completions fake returns a valid quiz
And the last write of the create fails
When the person creates a quiz
Then nothing is stored
And that attempt is not pinned to a quiz
When the last write succeeds and the person repeats that same attempt
Then one quiz is stored
```

---

## 6. List after create

### 6.1 The list is newest first and an open attempt does not change the completed score

Tier: 2 (hz-06)

```gherkin
Given a signed-in person
And an older finished quiz with a score of 1 of 3
And a finished quiz that was started again, with a completed score of 2 of 5
And another quiz created at that same time with a higher id and no completed score
And a neighbour who has a newer quiz
When the person reads the quiz list
Then the higher id comes before the quiz that shares its creation time
And both come before the older finished quiz
And the open attempt still shows 2 of 5
And the older card shows 1 of 3
And the card with no completed score shows no score
And each card shows the document name, the topic, and the question count
And no card shows a correct choice
And the neighbour's quiz is not listed
```

### 6.2 The list returns at most the declared cap

Tier: 2 (hz-06)

```gherkin
Given a signed-in person with more quizzes than the list cap
And a neighbour who has a quiz
When the person reads the quiz list
Then the list contains only this person's quizzes
And the list contains at most the cap
And the newest quizzes are the ones returned
And the quiz store is read a constant number of times
```

---

## 7. Answer

### 7.1 A choice is graded from the stored correct choice and a second choice does not grade again

Tier: 1 (hz-02, hz-03)

```gherkin
Scenario Outline:
Given a signed-in person on the first question of an open quiz
When the person chooses <first choice>
Then the grade is <grade>
And the page is revealed
And the revealed choices are <revealed>
And the page is a page of a retrieved piece
And the model is not called
When the person chooses another choice on that question
Then the grade is still <grade>
And the stored choice is still the first choice
And the model is not called

Examples:
  | first choice | grade | revealed |
  | the correct choice | right | the correct choice |
  | a wrong choice | wrong | the chosen choice and the correct choice |
```

### 7.2 A choice that is not on the question is refused

Tier: 2 (hz-05)

```gherkin
Given a signed-in person on an open question
When the person chooses a choice that is not on the question
Then the answer is refused
And the question stays unanswered
And the page and the correct choice stay hidden
```

### 7.3 Two answers at the same moment leave one grade

Tier: 2 (hz-03)

```gherkin
Given a signed-in person on an unanswered question
When two different choices interleave before the grade is stored
Then one choice is stored
And both responses show that same grade
And the grade is the stored correct choice, not a blend of the two requests
```

---

## 8. Advance and result

### 8.1 Next opens the following question

Tier: 1 (hz-04)

```gherkin
Given a signed-in person who has answered the first question of an open quiz
When the person goes to the next question
Then the attempt is open on the following question
And that question hides the page and the correct choice
And the previous grade is unchanged
And the list score is unchanged
```

### 8.2 Advance before a choice is refused

Tier: 2 (hz-04)

```gherkin
Given a signed-in person on an unanswered question
When the person goes to the next question
Then the advance is refused because the question is not answered
And the attempt stays on that question
```

### 8.3 Finish records the score and the review and clears the open attempt

Tier: 1 (hz-01, hz-04)

```gherkin
Scenario Outline:
Given a signed-in person with an open quiz of <count> questions
When the person answers every question <how> and finishes
Then the score is <correct> of <count>
And the result reviews every question with the chosen choice, the correct choice, and the page
And there is no open attempt
And the list card shows that score
And the model is not called

Examples:
  | count | how | correct |
  | 5 | wrong | 0 |
  | 3 | right | 3 |
  | 8 | right | 8 |
```

### 8.4 Choose and advance after finish are refused

Tier: 2 (hz-04)

```gherkin
Scenario Outline:
Given a signed-in person with a finished quiz and no open attempt
When the person <acts>
Then the action is refused because there is no open attempt
And the score is unchanged
And the model is not called

Examples:
  | acts |
  | answers the quiz |
  | advances the quiz |
```

---

## 9. Resume

### 9.1 Opening the quiz again continues at the saved question

Tier: 1 (hz-02)

```gherkin
Given a signed-in person who has answered the first question and gone to the next
And the list still shows the previous completed score
When the person leaves and reads the quiz again
Then the attempt is open on that same question
And the first grade is unchanged
And the open question hides the page and the correct choice
And the list still shows the previous completed score
And the model is not called
```

---

## 10. Play again

### 10.1 Play again uses the same questions and keeps the previous score until the new finish

Tier: 1 (hz-02, hz-04)

```gherkin
Given a signed-in person with a finished quiz
When the person plays the quiz again
Then the attempt is open on the first question
And the questions and the choices are the stored ones
And the page and the correct choice are hidden
And the list still shows the previous score
And the model is not called
When the person finishes the new attempt with a different score
Then the list shows only the new score
And the model is not called
```

---

## 11. Account delete

### 11.1 Deleting the account removes that person's quizzes and attempts

Tier: 2 (hz-04)

```gherkin
Given a signed-in person with a finished quiz and an open quiz
And a neighbour with a quiz and an open attempt
When the person deletes the account
Then that person's quizzes and attempts are gone
And the neighbour's quiz and attempt remain
```

### 11.2 A delete with no account removes nothing

Tier: 2 (hz-04)

```gherkin
Given a signed-in person with a quiz
And a neighbour with a quiz
When a quiz wipe is attempted with no account
Then both quizzes remain
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `a person who is not signed in` | No `Authorization` bearer token |
| `the refusal matches a missing quiz` | HTTP 404 `{"code":"quiz_not_found","message":"Quiz was not found"}`, identical for no session, a session-store failure, an unknown id, and another owner |
| `nothing is stored` | No new quiz row, question row, or attempt row |
| `session store fails` | Session lookup times out or errors. The response is still `quiz_not_found` |
| `a document of theirs that is <state>` | Own document with status `waiting`, `indexing`, `failed`, or a status outside that set |
| `the create is refused because the document is not ready` | HTTP 400 `{"code":"document_not_ready","message":"Document is not ready"}` |
| `the create is refused because there is no ready document` | HTTP 400 `{"code":"no_ready_document","message":"No ready document"}` |
| `reads the quiz list` | `GET /api/v1/quizzes` |
| `reads a quiz` / `reads the quiz again` | `GET /api/v1/quizzes/{id}` |
| `creates a quiz` | `POST /api/v1/quizzes` with a new `Idempotency-Key`, `document_id`, `topic`, and optional `question_count`. Success is HTTP 201 |
| `the same attempt` | The same `Idempotency-Key` |
| `a new attempt` | A different `Idempotency-Key` |
| `the create is refused because the topic is empty` | HTTP 400 `{"code":"empty_topic","message":"Topic is empty"}` for empty, spaces-only, omitted, and null topic |
| `the create is refused because the question count is not allowed` | HTTP 400 `{"code":"invalid_question_count","message":"Question count is not allowed"}` |
| `the count omitted` | Request body has `document_id` and `topic` and no `question_count` |
| `the completions fake returns a valid quiz` | Fake chat-completions body: `question_count` questions, four choices, exactly one correct, `page` drawn from the retrieved pieces. No request is sent to live freellmapi |
| `the model asked is auto` | Completions request `model` is `auto` |
| `the model is called once` | The completions fake records one call for that attempt |
| `the model is not called` | The completions fake records no call |
| `the response hides the page and the correct choice` | On `status=take`, unanswered questions have `page` and `correct_choice_id` null |
| `the citation is a page, not a slide` | `page` is an integer. The payload has no slide field |
| `the list shows this quiz first with no completed score` | `quizzes[0]` is the new id and `last_score` is null |
| `a Russian topic` / `an English topic` | Topic text in that language. The completions request carries the topic and that language. The fake's question and choice text is the marker for the language it was asked |
| `normalizes to the maximum length` | After trim and NFC the topic is 200 characters and includes a combining mark and an emoji. The raw decomposed form may be longer than 200. Stored `topic`, question text, and choice text compare byte-exact to NFC |
| `the create is refused because nothing was found` | HTTP 400 `{"code":"empty_retrieval","message":"Nothing was found for the topic"}` |
| `the create is refused because the quiz could not be assembled` | HTTP 400 `{"code":"generation_failed","message":"Quiz could not be assembled"}` |
| `that attempt did not call the model a second time` | One completions call for the failing try, then no further call until the person repeats the attempt |
| `the last write of the create fails` | The attempt insert fails after the quiz and questions are staged. The transaction rolls back. Zero quiz, question, and attempt rows, and the idempotency key is not bound |
| `newest first` / `higher id` | Order is `created_at` descending, then id descending |
| `more quizzes than the list cap` | 101 quizzes for this person. The response has at most 100, the newest by that order |
| `the quiz store is read a constant number of times` | Repository calls for the list do not grow with the number of quizzes |
| `chooses the correct choice` / `chooses a wrong choice` | `POST /api/v1/quizzes/{id}/answers` with that choice id. HTTP 200 |
| `the grade is right` / `the grade is wrong` | `correct` true or false, `chosen_choice_id` set, `page` and `correct_choice_id` set |
| `the answer is refused` | HTTP 400 `{"code":"invalid_choice","message":"Choice is not on the question"}` |
| `two different choices interleave before the grade is stored` | A latch between the read of the unanswered question and the grade write |
| `two creates with the same attempt interleave before the quiz is stored` | A latch between the idempotency read and the insert. Both requests use one `Idempotency-Key` |
| `goes to the next question` / `advances the quiz` / `finishes` | `POST /api/v1/quizzes/{id}/advance` |
| `the advance is refused because the question is not answered` | HTTP 400 `{"code":"unanswered","message":"The question is not answered"}` |
| `the score is 0 of 5` / `the score is <correct> of <count>` | `last_score.correct` and `last_score.total` are those integers. `status` is `result` |
| `the action is refused because there is no open attempt` | HTTP 400 `{"code":"no_open_attempt","message":"No open attempt"}` |
| `plays the quiz again` / `plays a quiz again` | `POST /api/v1/quizzes/{id}/retries` |
| `deletes the account` | Story 1 account delete. Quiz and attempt rows for that owner are removed |
| `a quiz wipe is attempted with no account` | The quiz-wipe port is invoked with an empty owner scope |
| `whose examiner series has three grades` | Story 4 examiner series. No quiz row is written by that series |
