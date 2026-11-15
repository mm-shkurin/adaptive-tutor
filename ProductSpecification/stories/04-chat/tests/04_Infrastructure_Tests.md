# Chat — Infrastructure Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with the chat store down, then recovery and leaked connections, then a missing model key that must not stop startup.

## 1. Chat store

### 1.1 A dead chat store refuses the list

Tier: 2 (hz-05, hz-07)

```gherkin
Given a signed-in person who has a chat
And the chat store is down
When the person reads the chat list
Then the read is refused
And no chat is returned
```

### 1.2 A dead chat store refuses the send and stores no line

Tier: 2 (hz-05, hz-07)

```gherkin
Given a signed-in person with an askable chat
And the chat store is down
When the person sends a line
Then the send is refused
And no line is stored
```

### 1.3 The thread reads back after the store recovers

Tier: 2

```gherkin
Given the chat store was down and is back
And a signed-in person with an askable chat
When the person reads the chat
Then the thread is the thread from before the outage
```

### 1.4 One send is stored after the store recovers

Tier: 2

```gherkin
Given the chat store was down and is back
And a signed-in person with an askable chat
When the person sends a line
Then that line is stored once
```

### 1.5 Repeated failed sends return the store connections to baseline

Tier: 2 (hz-06)

```gherkin
Given a signed-in person with an askable chat
When several sends fail because the chat store or the search store is unavailable
Then the open store connections return to the baseline
And a further send can still be stored once the store is back
```

### 1.6 A dead chat store refuses a read, a new chat, and a switch

Tier: 2 (hz-05)

```gherkin
Scenario Outline:
Given a signed-in person
And the chat store is down
When the person <asks>
Then the call is refused
And no chat is created

Examples:
  | asks |
  | reads a chat |
  | starts a chat |
  | opens a chat for a document |
```

### 1.7 Repeated failed model and embedding calls return connections to baseline

Tier: 2 (hz-06)

```gherkin
Given a signed-in person with an askable chat
When several model calls and embedding calls fail
Then the open connections return to the baseline
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

### 2.2 A missing model key fails the send

Tier: 2 (hz-05, hz-07)

```gherkin
Given the app is running with the model key unset
And a signed-in person with an askable chat
When the person sends a line
Then the reply fails
And the thread has one person line and no tutor line
And the failure shows no secret, no stack, and no file path
```

---

## 3. Failure signal and redaction

### 3.2 A failure body and its log omit a secret, the document text, and another person's chat

Tier: 2 (hz-07)

```gherkin
Scenario Outline:
Given a seeded secret, a seeded piece of this PDF, and a seeded line from another person's chat
And the <call> fails
When the person meets that failure
Then the body is the sanctioned error
And the body and the log omit the secret, the piece, and the other person's line
And the body has no stack, no path, and no internal class name

Examples:
  | call |
  | model call |
  | search |
  | embedding call |
  | reply that misses the latency budget |
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `the chat store is down` / `the chat store was down and is back` | PostgreSQL connection refused, then restored. Refused calls are HTTP 503 `{"code":"unavailable","message":"Chat store is unavailable"}` |
| `the search store is unavailable` | The Qdrant fake refuses the call. Startup still has `QDRANT_URL` set. Story 2 already refuses to start when that setting is missing |
| `open store connections return to the baseline` | Checked-out pool connections after the failures equal the count from before them |
| `the model key is unset` | `FREE_LLM_API_KEY` absent. `load_settings` does not raise. The send's model call fails as `reply_failed` |
| `the failure shows no secret, no stack, and no file path` | Response body has `code` and `message` only. A seeded key value, traceback, and path are absent |
