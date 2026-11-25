# Presentations — Integration Tests

> External ports: virus, OCR, chat-LLM (weak OCR), embeddings, Qdrant. All faked in CI.

## 1. External failures

### 1.1 Virus timeout refuses the slide add

Tier: 1 (hz-02, hz-07)

```gherkin
Given a signed-in person with a draft
And the virus check times out
When the person adds a jpeg
Then the add is refused with virus_detected
And no slide is stored
```

### 1.2 OCR channel failure fails the index without leaving half-searchable pieces

Tier: 1 (hz-02, hz-04)

```gherkin
Given a signed-in person with one image slide
And OCR raises a transport failure
When the person indexes
Then status is failed
And search has no pieces for that presentation
```

### 1.3 Embeddings failure fails the index

Tier: 2 (hz-02)

```gherkin
Given a signed-in person with one image slide and successful OCR
And embeddings refuse the batch
When the person indexes
Then status is failed
And search has no pieces for that presentation
```

### 1.4 Chat LLM timeout on a weak OCR slide fails only that enrichment path per decision

Tier: 2 (hz-02, hz-07)

```gherkin
Given a signed-in person with one weak-OCR slide
And the chat LLM times out
When the person indexes
Then the slide keeps whatever OCR text existed
And the presentation can still become ready if that text is non-empty
And formula fields stay null
```

---

## 2. Cross-feature seams

### 2.1 A ready presentation can be bound in chat with slide citation

Tier: 1 (hz-04)

```gherkin
Given a signed-in person with a ready presentation that has searchable text
When the person opens chat on that presentation and asks a question answered from slide 1
Then the reply citation includes slide 1
And an ordinary ready PDF chat still cites page only
```

### 2.2 A ready presentation can start a quiz

Tier: 1 (hz-04)

```gherkin
Given a signed-in person with a ready presentation and vectors
When the person creates a quiz on that presentation
Then the quiz is stored
And a question citation may include a slide
```

### 2.3 A draft presentation cannot start a quiz or bind chat

Tier: 1 (hz-04, hz-05)

```gherkin
Given a signed-in person with a draft presentation
When the person creates a quiz on it
Then create is refused because the document is not ready
When the person binds chat to it
Then bind is refused because the document is not ready
```
