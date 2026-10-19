# PDF documents — Infrastructure Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with the document store down, then recovery, then leftover connections, then missing settings at startup.

## 1. Document store

### 1.1 A dead document store refuses the upload and adds no document

Tier: 2 (hz-02, hz-05)

```gherkin
Given a signed-in person
And the document store is down
When the person submits a valid PDF
Then the upload is refused
And no document is stored
And the document is not marked ready
```

### 1.2 The same person uploads after the store recovers

Tier: 2

```gherkin
Given the document store was down and is back
When the person submits a valid PDF
Then the document is accepted
And the person can read it back
```

### 1.3 Repeated failed uploads return the store connections to baseline

Tier: 2 (hz-02, hz-06)

```gherkin
Given a signed-in person
When several uploads fail because the store, the virus check, or the search store is unavailable
Then the open connections return to the baseline
And the open file handles and temporary files return to the baseline
And a further upload can still be accepted once the store is back
```

---

## 2. Startup

### 2.1 The app refuses to start when indexing settings are missing

Tier: 2 (hz-05, hz-07)

```gherkin
Scenario Outline:
Given <setting> is missing
When the app starts
Then startup fails before it accepts an upload
And it does not pretend the check passed

Examples:
  | setting |
  | the virus check |
  | the search store |
  | the document store |
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `the document store is down` | PostgreSQL connection refused |
| `the open connections return to the baseline` | Pool checked-out count back to the pre-run value |
| `the virus check` | ClamAV settings |
| `the search store` | Qdrant settings |
