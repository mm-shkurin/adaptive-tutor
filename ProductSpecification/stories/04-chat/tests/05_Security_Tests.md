# Chat — Security Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with someone else's chat, then text that must stay text, then fields the client must not be able to set.

Rows not generated: rate limiting, because this story sets no new limit; input length, because no line-length cap was chosen; JWT, because this story does not issue tokens; CSRF and password hashing, because the session is a bearer token and there is no password.

## 1. Someone else's chat

### 1.1 Another person's chat or document is refused like a missing chat

Tier: 2 (sec:IDOR, hz-04, hz-05, hz-08)

```gherkin
Scenario Outline:
Given a signed-in person
And a neighbour who owns <target>
When the person <asks>
Then the refusal matches a missing chat
And nothing of the neighbour's is stored or returned

Examples:
  | target | asks |
  | a chat | reads that chat |
  | a chat | sends a line to that chat |
  | a ready PDF | starts a chat on that PDF |
  | a ready PDF | opens a chat for that PDF |
```

---

## 2. Text stays text

### 2.1 A script and a SQL fragment round-trip as the person's own text

Tier: 2 (sec:XSS, sec:SQLi, hz-05)

```gherkin
Given a signed-in person with an askable chat
And a retrieved piece whose text contains a script and a SQL fragment
When the person sends a line that contains a script and a SQL fragment
Then the thread shows that line unchanged
And the source shows that piece unchanged
And the chat list still contains only this person's chats
```

---

## 3. Fields the client does not own

### 3.1 Server-owned fields on a send are ignored

Tier: 2 (sec:MassAssignment, hz-04, hz-05)

```gherkin
Given a signed-in person with an askable chat
When the person sends a line that also names an owner, a page, a source, a role, and whether a grade is correct
Then the chat still belongs to the signed-in person
And the page and the sources are the retrieved piece's
And the grade flag in the request is not the stored grade
And the role in the request is not stored
And the line id and the document id are the ones the server stored
```

### 3.2 Server-owned fields on a new chat and on a switch are ignored

Tier: 2 (sec:MassAssignment, hz-05)

```gherkin
Scenario Outline:
Given a signed-in person with a ready PDF
When the person <binds> and names an owner, an id, a creation time, a role, and a preview
Then the chat belongs to the signed-in person
And the id, the creation time, the role, and the preview are the ones the server stored

Examples:
  | binds |
  | starts a chat on that PDF |
  | opens a chat for that PDF |
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `the refusal matches a missing chat` | HTTP 404 `{"code":"chat_not_found","message":"Chat was not found"}` for the neighbour's id and for an unknown id |
| `a script and a SQL fragment` | The characters `<script>` and `' OR 1=1` stored and returned as text. The list query is parameterized |
| `names an owner, a page, a source, a role, and whether a grade is correct` | Extra JSON fields `owner`, `page`, `sources`, `role`, `correct` on `POST /api/v1/chats/{id}/messages`. They are not bound |
