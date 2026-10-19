# PDF documents — Integration Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with a clean file that becomes ready, then a virus check that does not clear it, then a search store that does not accept the index.

## 1. Virus check

### 1.1 A clean PDF passes the virus check and becomes ready

Tier: 2

```gherkin
Given a signed-in person
And the virus check clears files
When the person submits a valid PDF
Then the document becomes ready
And its text can be searched
```

### 1.2 A virus check that does not clear the file adds no document

Tier: 2 (hz-02, hz-05)

```gherkin
Scenario Outline:
Given a signed-in person with one document
And the virus check <outcome>
When the person submits a PDF
Then the upload is refused
And the list is unchanged
And the file is not indexed

Examples:
  | outcome |
  | finds a virus |
  | times out |
  | answers unreadable |
```

---

## 2. Search store

### 2.1 A search store that does not accept the index fails the document

Tier: 2 (hz-02, hz-05, hz-07)

```gherkin
Scenario Outline:
Given an accepted document
And the search store <outcome>
When indexing runs
Then the document is failed
And the document is not ready
And nothing from the file can be searched
And the failure is visible on the document

Examples:
  | outcome |
  | times out |
  | refuses |
  | answers unreadable |
```

### 2.2 A retry after a partial index does not write the pieces twice

Tier: 2 (hz-02)

```gherkin
Given indexing wrote the pieces and then failed before recording ready
When indexing runs again
Then one set of pieces exists
And the virus check is not run again
And the document becomes ready or failed
And it is not ready while the pieces are incomplete
```

### 2.3 An embedding refusal stops, and a server error stays inside the three tries

Tier: 2 (hz-02)

```gherkin
Scenario Outline:
Given an accepted document
And the embedding call <outcome>
When indexing runs
Then <result>

Examples:
  | outcome | result |
  | refuses | the document is failed and is not tried again for that refusal |
  | answers unreadable | the document is failed |
  | fails as a server error | the try counts toward the three |
```

### 2.4 Many indexes that fail together do not retry on the same tick

Tier: 2 (hz-02, hz-06)

```gherkin
Given many accepted documents
And the search store fails once for all of them
When they retry
Then the retries are not all issued at the same instant
And none of them is tried more than three times
```

### 2.5 A call that finishes just before its deadline still counts

Tier: 2 (hz-02, hz-07)

```gherkin
Given a virus check and a search store call
When the call finishes just before its deadline
Then it still counts as answered
When the call reaches its deadline
Then the virus check refuses the upload
And the search store fails the document
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `the virus check` | ClamAV. Tests use a double, not a live daemon |
| `the search store` | Qdrant, after the embedding call. Tests use a double |
| `finds a virus` | 400 virus_detected, no row |
| `times out` | The call exceeds its deadline. Virus check: 400 virus_detected. Search store: status failed |
| `answers unreadable` | Empty or malformed body, treated as the same refusal or failure |
| `wrote the pieces and then failed` | Search-store write succeeded, the status write did not |
