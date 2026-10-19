# PDF documents — Security Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with a name that must stay text, then fields the person must not write, then whose document it is, then how many uploads a minute.

## 1. Name and reason as text

### 1.1 A hostile name and a hostile failure reason stay text

Tier: 2 (sec:XSS, sec:SQLi, hz-01, hz-05)

```gherkin
Given a signed-in person and a neighbour
When the person uploads a PDF whose name contains query metacharacters and markup
And a failed document's reason contains the same
Then the stored name equals the submitted name
And the list shows that name as text
And the failure reason is shown as text
And the markup is not treated as a control
And the query metacharacters are not treated as a command
And the neighbour's documents are unchanged
And a line break in the name stays inside that one field
And query metacharacters in the PDF text are not a command
```

---

## 2. Fields the person does not own

### 2.1 An upload cannot set the server's fields

Tier: 2 (sec:MassAssignment, hz-04, hz-05)

```gherkin
Given a signed-in person
When the person submits a valid PDF and also sends an id, an owner, a status, a page count, a piece count, and an error
Then the document is accepted only because the PDF itself is acceptable
And the id is server-set
And the owner is the signed-in person
And the status is waiting
And the page count is not the submitted count
And the piece count is not the submitted count
And the error is empty
And a submitted byte size is ignored
And a submitted upload time is ignored
And the stored size is the file's byte count
```

### 2.2 A file name past 255 characters is refused

Tier: 2 (sec:InputLength, hz-01, hz-06)

```gherkin
Given a signed-in person with one document
When the person submits a PDF whose name is 256 characters
Then the upload is refused
And the list is unchanged
```

---

## 3. Whose document

### 3.1 A missing document, a neighbour's document, and a guest's open look the same

Tier: 2 (sec:IDOR, hz-05, hz-07, hz-08)

```gherkin
Given a signed-in person and a neighbour with a document
When each of these opens a document: the neighbour's id, an id that does not exist, and a guest opening the person's id
Then each refusal is the same status and the same body
And none of them includes the document's name or text
```

### 3.2 A guest's list and upload match a missing document

Tier: 2 (hz-05, hz-08)

```gherkin
Given a guest
When the guest reads the document list without the screen
And the guest uploads a PDF without the screen
Then each refusal matches a missing document
And no document is added
And neither answer includes a document name or text
```

---

## 4. How many uploads

### 4.1 A sixth upload in the minute is refused and the five stay

Tier: 2 (sec:RateLimit, hz-06)

```gherkin
Given a signed-in person who has five accepted uploads in the current minute
When the person submits a sixth PDF
Then the upload is refused
And the five documents stay
```

### 4.2 Two uploads that arrive together on the last free slot accept only one

Tier: 2 (sec:RateLimit, hz-03)

```gherkin
Given a signed-in person with four accepted uploads in the current minute
When two uploads pass the count check together
Then one of them is accepted
And the other is refused
And five documents exist
```

### 4.3 An upload at the start of the next minute is accepted

Tier: 2 (sec:RateLimit, hz-07)

```gherkin
Given a signed-in person who has five accepted uploads in this minute
When the clock is just short of the next minute
Then a sixth upload is still refused
When the minute window has just opened
Then the next upload is accepted
And the five from the previous minute stay
```

### 4.4 An unreadable upload count refuses the upload

Tier: 2 (sec:RateLimit, hz-02, hz-05, hz-06)

```gherkin
Given a signed-in person
And the upload count cannot be read
When the person submits a valid PDF
Then the upload is refused
And no document is added
```

---

## 5. What a failure may say

### 5.1 A failure echoes no secret, file text, stack, or path

Tier: 2 (hz-07)

```gherkin
Given a known secret and a phrase that appears only in the PDF
When an upload is refused, indexing fails, the virus check rejects the file, or the upload count cannot be read
Then the answer and the log do not contain the secret
And the answer and the log do not contain that phrase
And the answer and the log do not contain a stack, a file path, or an internal name
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `query metacharacters and markup` | A name containing `' OR 1=1` and `<script>` |
| `shown as text` | The list renders the string; the script does not run |
| `sends an id, an owner, a status` | Extra multipart fields. They are ignored |
| `each refusal is the same status and the same body` | GET /api/v1/documents/{id} → 404 document_not_found, identical body for no session, unknown id, and another owner |
| `the upload count cannot be read` | The rate store errors or times out. 429 rate_unavailable |
| `a sixth upload` | 429 rate_limited |
