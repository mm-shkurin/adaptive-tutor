# Quizzes — Infrastructure Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with the quiz store down, then recovery and leaked connections, then a missing model key, then failure output that must stay safe.

## 1. Quiz store

### 1.1 A dead quiz store refuses a read

Tier: 2 (hz-05, hz-07)

```gherkin
Scenario Outline:
Given a signed-in person who has a quiz
And the quiz store is down
When the person <reads>
Then the read is refused
And no quiz is returned

Examples:
  | reads |
  | reads the quiz list |
  | reads the quiz |
```

### 1.2 A dead quiz store refuses a write and stores nothing

Tier: 2 (hz-02, hz-05, hz-07)

```gherkin
Scenario Outline:
Given a signed-in person with an open quiz
And the quiz store is down
When the person <writes>
Then the write is refused
And nothing new is stored

Examples:
  | writes |
  | creates a quiz |
  | answers the quiz |
  | advances the quiz |
  | plays the quiz again |
```

### 1.3 The list reads back after the store recovers

Tier: 2

```gherkin
Given the quiz store was down and is back
And a signed-in person who had a quiz
When the person reads the quiz list
Then the list is the list from before the outage
```

### 1.4 One quiz is stored after the store recovers

Tier: 2 (hz-02)

```gherkin
Given the quiz store was down and is back
And a signed-in person with a ready PDF
And the completions fake returns a valid quiz
When the person creates a quiz
Then that quiz is stored once
```

### 1.5 Repeated failed creates return the store connections to baseline

Tier: 2 (hz-06)

```gherkin
Given a signed-in person with a ready PDF
When several creates fail because the quiz store or the model call is unavailable
Then the open store connections return to the baseline
And a further create can still be stored once the store is back
```

---

## 2. Model key

### 2.1 A missing model key does not stop startup

Tier: 2 (hz-05, hz-07)

```gherkin
Given the model key is unset
When the app starts
Then the app is running
```

### 2.2 A missing model key fails the create and stores nothing

Tier: 2 (hz-05, hz-07)

```gherkin
Given the app is running with the model key unset
And a signed-in person with a ready PDF
When the person creates a quiz
Then the create is refused because the quiz could not be assembled
And nothing is stored
And the failure shows no secret, no stack, and no file path
```

---

## 3. Failure signal and redaction

### 3.1 A failure body and its log omit the document text, a secret, and another person's quiz

Tier: 2 (hz-05, hz-07)

```gherkin
Scenario Outline:
Given a seeded secret, a seeded sentence of this PDF, and a seeded quiz of a neighbour
And the <call> fails
When the person creates a quiz
Then the body is the sanctioned error
And nothing is stored
And the body and the log omit the secret, the sentence, and the neighbour's quiz
And the body has no stack, no path, and no internal class name

Examples:
  | call |
  | model call |
  | search |
  | reply of the wrong shape |
  | model key unset |
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `the quiz store is down` / `the quiz store was down and is back` | PostgreSQL connection refused, then restored. Refused calls are HTTP 503 `{"code":"unavailable","message":"Quiz store is unavailable"}` |
| `reads the quiz list` | `GET /api/v1/quizzes` |
| `reads the quiz` | `GET /api/v1/quizzes/{id}` |
| `creates a quiz` / `answers the quiz` / `advances the quiz` / `plays the quiz again` | The story's create, answer, advance, and retry routes |
| `nothing new is stored` | Quiz, question, and attempt rows are unchanged |
| `open store connections return to the baseline` | Checked-out pool connections after the failures equal the count from before them |
| `the model call is unavailable` | The completions fake refuses the call. The failure path releases its connection |
| `the model key is unset` | `FREE_LLM_API_KEY` absent. Startup does not raise. Create fails as `generation_failed` |
| `the create is refused because the quiz could not be assembled` | HTTP 400 `{"code":"generation_failed","message":"Quiz could not be assembled"}` |
| `the failure shows no secret, no stack, and no file path` | Body is `code` and `message` only |
| `a seeded secret` | A fixed sentinel API-key value |
| `a seeded sentence of this PDF` | A fixed sentinel sentence in the retrieved piece text |
| `a seeded quiz of a neighbour` | The neighbour's topic and question text |
| `the body is the sanctioned error` | `generation_failed` for model, search, wrong shape, and a missing key. Message is `Quiz could not be assembled` |
| `the body and the log omit` | The sentinels are absent from the JSON body and from captured logs. A logged secret is the redaction token, not the raw sentinel |
| `no stack, no path, and no internal class name` | Body contains no traceback marker, no filesystem path, and no Python class path |
| `the failure signal is not recorded` | The failure log event and the failure counter do not increment on HTTP 201 |
