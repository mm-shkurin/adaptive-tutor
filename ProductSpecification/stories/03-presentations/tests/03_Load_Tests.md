# Presentations — Load Tests

> Profile: single-user local ExpectedLoad. No multi-tenant flood. Index ceiling matches PDF (5 minutes). Skip if no matching challenge in ExpectedLoad beyond single-user indexing.

## 1. Index budget

### 1.1 Forty-slide index finishes or fails within five minutes

Tier: 2 (hz-06, hz-07)

```gherkin
Given a signed-in person with a draft of 40 image slides
And OCR and embeddings are faked fast
When the person indexes
Then within 5 minutes status is ready or failed
And the run does not leave status indexing forever
```

### 1.2 Presentation add does not consume the PDF upload rate slot

Tier: 3 (hz-06)

```gherkin
Given a signed-in person who already accepted five PDF uploads this minute
When the person adds a jpeg slide to a draft
Then the add is not refused with rate_limited
```

Moved intent: interview said no new presentation rate; confirm PDF rate untouched. Tier 3 — nice confirmation, not critical path.
