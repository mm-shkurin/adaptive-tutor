# PDF documents — Load Tests

Latency. The story's bar is the document-indexing line in `ProductSpecification/ExpectedLoad.md`: a 10 MB PDF ready within 30 seconds, and an upload that answers while chat is busy.

---

## 1. Indexing time

### 1.1 A lecture becomes ready within the indexing ceiling

Tier: 2

```gherkin
Given the standard indexing baseline
When the person uploads that lecture
Then the document becomes ready
And indexing finishes within the indexing ceiling
```

Ceiling: 30 seconds for the 10 MB lecture in ExpectedLoad. Catches an index that misses the bar the story promises.

---

## 2. Upload while chat is busy

### 2.1 An upload during peak chat is answered before indexing finishes

Tier: 2

```gherkin
Given the peak chat baseline
When the person uploads a PDF
Then the upload is answered before indexing finishes
And the document later becomes ready
```

Threshold: one upload while 15 chats are in flight, from ExpectedLoad. Catches an upload that waits on indexing or on the chat load.

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `the standard indexing baseline` | One 10 MB text PDF, as in ExpectedLoad |
| `the indexing ceiling` | 30 seconds until status ready |
| `the peak chat baseline` | 15 concurrent chat requests, as in ExpectedLoad |
| `the upload is answered` | POST /api/v1/documents returns before status leaves waiting |
