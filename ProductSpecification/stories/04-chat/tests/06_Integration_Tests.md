# Chat — Integration Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with a reply that comes back from stored vectors, then a vector run that fails, then a model call that fails, then a search that fails.

Acceptance never calls the live model or the live search store. These scenarios drive the fakes.

## 1. Vectors and the reply

### 1.1 A newly indexed PDF is answered from its vectors and the stored starting page

Tier: 1 (hz-04)

```gherkin
Given a signed-in person
And a new PDF that finishes indexing
When the person asks a question that the PDF contains
Then the vectors are 384-dimensional
And the reply uses only pieces of this PDF
And the page is the starting page stored while the file was in hand
```

### 1.2 A vector run that fails leaves the document ready and the next open can finish

Tier: 2 (hz-02, hz-04, hz-05)

```gherkin
Scenario Outline:
Given a signed-in person
And a ready PDF with no vectors
And the embedding call <fails>
When the person opens a chat on that PDF
Then the chat says the material cannot be asked yet
And the library row stays ready
When the embedding call succeeds and the person opens the chat again
Then the chat becomes askable
And pieces already stored are not stored again

Examples:
  | fails |
  | times out |
  | returns a 4xx status |
  | returns a 5xx status |
  | returns a malformed body |
```

---

## 2. The model call

### 2.1 A failed model call keeps one person line and no tutor line

Tier: 2 (hz-02, hz-05)

```gherkin
Scenario Outline:
Given a signed-in person with an askable chat
And the model call <fails>
When the person sends a line
Then the thread has one person line
And the thread has no tutor line
When the person repeats that same attempt
Then the thread still has one person line

Examples:
  | fails |
  | times out |
  | returns a 4xx status |
  | returns a 5xx status |
  | returns a malformed body |
```

---

## 3. Search

### 3.1 A failed search keeps one person line and no tutor line

Tier: 2 (hz-02, hz-05)

```gherkin
Scenario Outline:
Given a signed-in person with an askable chat
And the search <fails>
When the person sends a line
Then the thread has one person line
And the thread has no tutor line

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
| `a new PDF that finishes indexing` | Story 2 indexing, plus this story's vector write and `page` on each piece before the file is deleted |
| `the vectors are 384-dimensional` | Fake embeddings `POST /v1/embeddings`, all-MiniLM-L6-v2, stored in the Qdrant fake |
| `the embedding call <fails>` | The embeddings fake times out, returns 4xx, returns 5xx, or returns a body that is not a 384-vector. Both statuses leave the PDF ready and the chat not askable. A 5xx does not retry inside the open |
| `the model call <fails>` | The chat-completions fake times out, returns a non-2xx status, or returns a body with no assistant text. A missing `FREE_LLM_API_KEY` is the infrastructure scenario, not this outline |
| `the search <fails>` | The Qdrant fake times out, returns a non-2xx status, or returns a body that is not a hit list |
| `the same attempt` | The same `Idempotency-Key` |
| `pieces already stored are not stored again` | Vector ids already written are unchanged after the next open |
| `the material cannot be asked yet` | `askable` false, notice «Материал пока нельзя спросить.», document status `ready` |
