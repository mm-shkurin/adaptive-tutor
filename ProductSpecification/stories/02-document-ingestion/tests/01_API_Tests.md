# PDF documents — API Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with an empty list, then refuse a bad file before accepting a good one, then one submission stored once, then indexing to ready or failed.

## 1. List

### 1.1 A person with no documents sees an empty list

Tier: 2

```gherkin
Given a signed-in person with no documents
When the person reads their documents
Then the list is empty
```

### 1.2 The list is this person's newest page

Tier: 2 (hz-05, hz-06)

```gherkin
Given a signed-in person with more documents than one page
And a neighbour with a document of their own
When the person reads the first page
Then the page holds at most fifty documents
And the newest document is first
And a later page holds the rest
And the neighbour's document is absent
```

### 1.3 A page read while a document arrives still covers each document once

Tier: 2 (hz-06)

```gherkin
Given a signed-in person who has read the first page
When a new document sorts into that page and the person reads the next page
Then each document appears once across the two pages
And two documents uploaded at the same instant keep the same order on a second read
```

---

## 2. Refusal and the edges

### 2.1 An unacceptable file adds no document

Tier: 2 (hz-01, hz-05, hz-06, hz-08)

```gherkin
Scenario Outline:
Given a signed-in person with one document
When the person <submits>
Then the upload is refused
And the list is unchanged

Examples:
  | submits |
  | submits no file |
  | submits a file that is not a PDF |
  | submits a PDF with no text |
  | submits a PDF one byte under the minimum |
  | submits a PDF one byte over the maximum |
  | submits an encrypted PDF |
  | submits a PDF with no file name |
```

### 2.2 A file at either size edge is stored as that byte count

Tier: 2 (hz-01, hz-06)

```gherkin
Scenario Outline:
Given a signed-in person
When the person submits a PDF of <size>
Then the document is accepted
And the stored size is <size>
And the size the person reads back is <size>

Examples:
  | size |
  | the minimum |
  | the maximum |
```

### 2.3 A name of 255 characters is kept unchanged

Tier: 2 (hz-01)

```gherkin
Given a signed-in person
When the person submits a PDF whose name is 255 characters and contains letters outside ASCII
Then the document is accepted
And the stored name equals the submitted name byte for byte after canonical composition
And the name the person reads back equals that stored name
```

### 2.4 A name that would split a letter at the limit is not stored broken

Tier: 2 (hz-01)

```gherkin
Given a signed-in person
When the person submits a PDF whose 255th place falls inside one letter
Then the stored name contains no broken letter
And the stored name contains no replacement character
```

---

## 3. One submission

### 3.1 The same submission stored twice is one document

Tier: 2 (hz-02)

```gherkin
Given a signed-in person
When the same submission is delivered twice
Then one document exists for that submission
And the second delivery does not add a second document
And the second delivery does not count as another upload in the minute
```

### 3.2 Two overlapping copies of one submission store one document

Tier: 2 (hz-02, hz-03)

```gherkin
Given two deliveries of one submission pass the existence check together
When both deliveries complete
Then one document exists for that submission
```

### 3.3 Uploading the same PDF again creates another document

Tier: 2

```gherkin
Given a signed-in person who already uploaded a PDF
When the person uploads that PDF again as a new submission
Then two documents exist
And the earlier document is unchanged
```

---

## 4. Indexing

### 4.1 An accepted PDF becomes ready and its text and tables can be searched

Tier: 1 (hz-01, hz-03, hz-04, hz-05)

```gherkin
Given a signed-in person
And a neighbour with indexed text
When the person submits a valid PDF that contains text and a table
Then the upload is answered before indexing finishes
And the next read shows the document as waiting, not a stale copy
And the document then becomes ready
And the ready document shows the file name, the byte size, the page count, and the piece count
And the ready document has no failure reason
And the person's search finds the text and the table
And the extracted text matches the PDF byte for byte after canonical composition
And the neighbour's text is absent
And a piece of 500 tokens is kept
And a shorter piece is joined onward
And the original file is gone
And the neighbour's file is still there
```

### 4.2 A failed index names the part and leaves nothing searchable

Tier: 2 (hz-02, hz-04, hz-07)

```gherkin
Given a signed-in person with a neighbour's document
When indexing fails on one table after an earlier step succeeded
Then the document is failed
And the failure names that table
And nothing from the file can be searched
And no piece rows remain
And the original file is gone
And the neighbour's document and file are unchanged
And a retry does not run the virus check again
And a retry does not add a second set of pieces
```

### 4.3 A document whose indexing never started still finishes

Tier: 2 (hz-03, hz-04)

```gherkin
Given an accepted document whose indexing was not started
When indexing is due
Then the document becomes ready or failed
And it does not stay waiting
```

### 4.4 Three failed tries end as failed and the next document still indexes

Tier: 2 (hz-03)

```gherkin
Given a document whose indexing fails every time
And a later valid document
When indexing has been tried three times
Then the failing document is failed
And the later document still becomes ready
```

### 4.5 Indexing that would store more than 2000 pieces fails the document

Tier: 2 (hz-06)

```gherkin
Given a signed-in person
When the person submits a PDF that would store more than 2000 pieces
Then the document is failed
And nothing from the file can be searched
```

### 4.6 Indexing that has not finished in 5 minutes is failed

Tier: 2 (hz-02, hz-04, hz-07)

```gherkin
Given an accepted document that is still indexing
When the clock is just short of five minutes
Then the document is still indexing
When five minutes have passed
Then the document is failed
And in-flight indexing is cancelled
And nothing is stored after that instant
And nothing from the file can be searched
```

### 4.7 A finished document is not indexed again

Tier: 2 (hz-02, hz-04)

```gherkin
Scenario Outline:
Given a document that is <finished>
When indexing is requested again for that document
Then the document stays <finished>
And no second set of pieces is stored

Examples:
  | finished |
  | ready |
  | failed |
```

### 4.8 A step that skips or reverses indexing is refused

Tier: 2 (hz-04)

```gherkin
Scenario Outline:
Given a document that is <from>
When the document is moved <toward>
Then the move is refused
And the document stays <from>
And its pieces, its search entries, and its file are untouched

Examples:
  | from | toward |
  | waiting | ready |
  | waiting | failed |
  | indexing | waiting |
  | ready | waiting |
  | ready | failed |
  | ready | indexing |
  | failed | waiting |
  | failed | ready |
  | failed | indexing |
```

### 4.9 An unknown status is not treated as ready

Tier: 2 (hz-05)

```gherkin
Given an accepted document
When the document is given a status that is not waiting, indexing, ready, or failed
Then the document is not ready
And nothing from the file is newly searchable
```

### 4.10 Two indexing claims of one document store one set of pieces

Tier: 2 (hz-02, hz-03)

```gherkin
Given an accepted document
When two indexing claims pass the status check together
Then one claim proceeds
And one set of pieces is stored
```

### 4.11 A second indexing run started while the first is going stores one set

Tier: 2 (hz-02, hz-03)

```gherkin
Given indexing of a document is still running
When a second indexing run starts for that document
Then the two runs do not both write pieces
And one set of pieces exists
```

### 4.12 A stale status write does not erase a newer one

Tier: 2 (hz-03)

```gherkin
Given a document loaded twice while it is indexing
When one save marks it ready and the other save marks it failed
Then the later save does not silently discard the earlier one
And the document ends in exactly one of those statuses
And the pieces match that status
```

### 4.13 A pathological PDF does not keep indexing busy past five minutes

Tier: 2 (hz-06)

```gherkin
Given a signed-in person
When the person submits a PDF that is costly to read but within the size limit
Then indexing finishes or fails within five minutes
And it does not keep running after that
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `a signed-in person` | Bearer access token for that account |
| `reads their documents` | GET /api/v1/documents?page= |
| `the list is unchanged` | Same ids, in the same order, as before the call |
| `submits a PDF` | POST /api/v1/documents with multipart file and a new Idempotency-Key |
| `the same submission` | The same Idempotency-Key |
| `a new submission` | A different Idempotency-Key, even when the bytes match |
| `the minimum` | 1048576 bytes, accepted |
| `the maximum` | 52428800 bytes, accepted |
| `one byte under the minimum` | 1048575 bytes, 400 file_too_small, no row |
| `one byte over the maximum` | 52428801 bytes, 400 file_too_large, no row |
| `the upload is refused` | 400 and no new row. Codes: file_missing, invalid_pdf, empty_pdf, file_too_small, file_too_large, encrypted_pdf, name_missing |
| `the person's search finds` | Pieces for that document only. No public search route in this story; the assertion reads the index through the test double |
| `five minutes have passed` | Clock fixed, then advanced |
