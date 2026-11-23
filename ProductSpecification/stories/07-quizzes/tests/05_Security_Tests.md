# Quizzes — Security Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with someone else's quiz, then text that must stay text, then fields the client must not be able to set, then lengths.

Rows not generated: rate limiting, because this story sets no new limit; CSRF, because the session is a bearer token; password hashing, because there is no password; JWT, because this story does not issue tokens. A missing session is refused like a missing quiz in the API tests, not as a token-algorithm check.

## 1. Someone else's quiz

### 1.1 Another person's quiz or document is refused like a missing quiz

Tier: 2 (sec:IDOR, hz-04, hz-05)

```gherkin
Scenario Outline:
Given a signed-in person
And a neighbour who has a quiz and a ready PDF
When the person <asks>
Then the refusal matches a missing quiz
And the neighbour's quiz and PDF are unchanged

Examples:
  | asks |
  | reads the neighbour's quiz |
  | answers the neighbour's quiz |
  | advances the neighbour's quiz |
  | plays the neighbour's quiz again |
  | creates a quiz on the neighbour's PDF |
  | creates a quiz on a document that does not exist |
  | reads a quiz that does not exist |
```

### 1.2 The quiz list does not include another person's quiz

Tier: 2 (sec:IDOR, hz-05)

```gherkin
Given a signed-in person with a quiz
And a neighbour with a quiz
When the person reads the quiz list
Then the list contains only this person's quiz
And the neighbour's topic is absent
```

---

## 2. Text stays text

### 2.1 A script and a SQL fragment round-trip as the person's own text

Tier: 2 (sec:XSS, sec:SQLi, sec:InputValidation, hz-05)

```gherkin
Given a signed-in person with a ready PDF
And a retrieved piece whose text contains a script and a SQL fragment
And the completions fake returns a question and a choice that contain a script and a SQL fragment
When the person creates a quiz with a topic that contains a script and a SQL fragment
Then the list shows that topic unchanged
And the question and the choice show that text unchanged
And the quiz list still contains only this person's quizzes
```

---

## 3. Fields the client does not own

### 3.1 Server-owned fields on create are ignored

Tier: 2 (sec:MassAssignment, hz-05)

```gherkin
Given a signed-in person with a ready PDF
And the completions fake returns a valid quiz
When the person creates a quiz that also names an owner, an id, a score, a status, a correct choice, a creation time, and a role
Then the quiz belongs to the signed-in person
And the id, the score, the status, the creation time, and the role are the ones the server stored
And the correct choice is the one from the fake, not the one in the request
And the list shows no completed score
```

### 3.2 Server-owned fields on an answer are ignored

Tier: 2 (sec:MassAssignment, hz-05)

```gherkin
Given a signed-in person on an unanswered question
When the person chooses a wrong choice and also names a right grade, a page, and a perfect score
Then the grade is wrong
And the page is the retrieved piece's page
And the list score is unchanged
```

---

## 4. Length

### 4.1 A topic or an idempotency key past its maximum is refused

Tier: 2 (sec:InputLength, hz-01, hz-06)

```gherkin
Scenario Outline:
Given a signed-in person with a ready PDF
When the person creates a quiz with <value>
Then the create is refused
And nothing is stored
And the model is not called

Examples:
  | value |
  | a topic past the maximum |
  | an idempotency key past the maximum |
  | an empty idempotency key |
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `the refusal matches a missing quiz` | HTTP 404 `{"code":"quiz_not_found","message":"Quiz was not found"}` for the neighbour's id, a missing id, and a missing or foreign `document_id` |
| `the neighbour's quiz and PDF are unchanged` | Neighbour quiz, attempt, and document rows are unchanged |
| `reads the neighbour's quiz` / `reads a quiz that does not exist` | `GET /api/v1/quizzes/{id}` |
| `answers the neighbour's quiz` | `POST /api/v1/quizzes/{id}/answers` |
| `advances the neighbour's quiz` | `POST /api/v1/quizzes/{id}/advance` |
| `plays the neighbour's quiz again` | `POST /api/v1/quizzes/{id}/retries` |
| `creates a quiz on the neighbour's PDF` / `creates a quiz on a document that does not exist` | `POST /api/v1/quizzes` with that `document_id` |
| `reads the quiz list` | `GET /api/v1/quizzes`. HTTP 200. `quizzes` contains only the caller's id |
| `the neighbour's topic is absent` | The neighbour's topic string is not in the response body |
| `a script and a SQL fragment` | The characters `<script>` and `' OR 1=1` stored and returned as text. The list query is parameterized |
| `names an owner, an id, a score, a status, a correct choice, a creation time, and a role` | Extra JSON fields `owner_id`, `id`, `last_score`, `status`, `correct_choice_id`, `created_at`, and `role` on `POST /api/v1/quizzes`. They are not bound |
| `names a right grade, a page, and a perfect score` | Extra JSON fields `correct`, `page`, and `last_score` on `POST /api/v1/quizzes/{id}/answers` beside a wrong `choice_id`. They are not bound |
| `a topic past the maximum` | After trim and NFC the topic is 201 characters. HTTP 400 `{"code":"empty_topic","message":"Topic is empty"}` |
| `an idempotency key past the maximum` | `Idempotency-Key` longer than 128 characters. HTTP 400 `{"code":"invalid_idempotency_key","message":"Idempotency key is not allowed"}` |
| `an empty idempotency key` | `Idempotency-Key` empty. Same `invalid_idempotency_key` body |
| `the create is refused` | The status and body in the row above. No quiz row |
