# Quizzes — Integration Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with a valid fake body, then a completions call that fails, then a search that fails.

Acceptance never calls live freellmapi. These scenarios drive the completions fake and the search fake. Replay and resume read storage and must not call either one.

## 1. A valid fake

### 1.1 A valid completions body creates one quiz and the live model is not called

Tier: 2 (hz-07)

```gherkin
Given a signed-in person with a ready PDF that has retrieved pieces
And the completions fake returns a valid quiz
When the person creates a quiz
Then one quiz is stored from that body
And the model is called once
And the live model is not called
And the page on each question is a page of a retrieved piece
```

### 1.2 Resume and play again do not call the model

Tier: 2 (hz-02)

```gherkin
Scenario Outline:
Given a signed-in person with <quiz>
When the person <acts>
Then the model is not called
And the questions are the stored questions

Examples:
  | quiz | acts |
  | an open quiz | reads the quiz again |
  | a finished quiz | plays the quiz again |
```

---

## 2. The model call

### 2.1 A failed completions call stores nothing and does not pin the attempt

Tier: 2 (hz-02, hz-05, hz-06)

```gherkin
Scenario Outline:
Given a signed-in person with a ready PDF
And the model call <fails>
When the person creates a quiz
Then the create is refused because the quiz could not be assembled
And nothing is stored
And that attempt did not call the model a second time
When the model call succeeds and the person repeats that same attempt
Then one quiz is stored
And the model is called once for the successful try

Examples:
  | fails |
  | times out |
  | returns a 4xx status |
  | returns a 5xx status |
  | returns a malformed body |
```

---

## 3. Search

### 3.1 A failed search stores nothing and does not call the model

Tier: 2 (hz-02, hz-05)

```gherkin
Scenario Outline:
Given a signed-in person with a ready PDF
And the search <fails>
When the person creates a quiz
Then the create is refused because the quiz could not be assembled
And nothing is stored
And the model is not called

Examples:
  | fails |
  | times out |
  | returns a 4xx status |
  | returns a 5xx status |
  | returns a malformed body |
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `the completions fake returns a valid quiz` | Fake `POST` body for chat completions: the asked count of questions, four choices, exactly one correct, `page` from the retrieved pieces. `model` on the request is `auto` |
| `the live model is not called` | No connection to the configured live freellmapi host. `FREE_LLM_CHAT_URL` in acceptance points at the fake. A live poke is outside the green pipeline |
| `the model is called once` | The fake records one completions call |
| `the model is not called` | The fake records no completions call |
| `reads the quiz again` | `GET /api/v1/quizzes/{id}` |
| `plays the quiz again` | `POST /api/v1/quizzes/{id}/retries` |
| `the model call <fails>` | The completions fake times out, returns 4xx, returns 5xx, or returns a body that is not quiz JSON. A 4xx and a 5xx are the same outcome: store nothing, no inner retry. A missing `FREE_LLM_API_KEY` is the infrastructure scenario |
| `the search <fails>` | The Qdrant fake times out, returns a non-2xx status, or returns a body that is not a hit list. An empty hit list is `empty_retrieval` in the API tests, not this outline |
| `the create is refused because the quiz could not be assembled` | HTTP 400 `{"code":"generation_failed","message":"Quiz could not be assembled"}` |
| `that attempt did not call the model a second time` | One failing completions call for that `Idempotency-Key`, then no further call until the person repeats the attempt |
| `the same attempt` | The same `Idempotency-Key` |
| `the model is called once for the successful try` | The successful repeat adds one completions call and one quiz |
| `a page of a retrieved piece` | Each stored `page` is among the pages returned by the search fake for this PDF |
