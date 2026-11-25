# Presentations — API Tests

> **Implementation Order**: Prerequisite refusals → empty draft create → validation on add/index → happy index → materials list kind → edit ready text → delete → progress read. OCR/virus/embeddings faked. Live Tesseract/LLM out of green pipeline.

## 1. Prerequisite guards

### 1.1 A call with no session is refused like a missing presentation

Tier: 1 (hz-05)

```gherkin
Scenario Outline:
Given a person who is not signed in
When the person <asks>
Then the refusal matches a missing presentation
And nothing is stored

Examples:
  | asks |
  | creates a presentation |
  | reads a presentation |
  | patches a presentation |
  | adds slides |
  | deletes a slide |
  | indexes a presentation |
  | deletes a presentation |
  | reads progress |
```

### 1.2 A neighbour's presentation looks absent

Tier: 1 (hz-05)

```gherkin
Given a signed-in person
And a neighbour who owns a presentation
When the person reads, patches, indexes, or deletes the neighbour's id
Then the refusal matches a missing presentation
And the neighbour's presentation is unchanged
```

### 1.3 A PDF page slide requires a ready owned PDF

Tier: 1 (hz-04, hz-05)

```gherkin
Scenario Outline:
Given a signed-in person with a draft presentation
And a PDF of theirs that is <state>
When the person adds that PDF's page as a slide
Then the add is refused because the PDF is not a ready owned source
And no slide is stored

Examples:
  | state |
  | waiting |
  | indexing |
  | failed |
  | missing |
  | owned by a neighbour and ready |
```

---

## 2. Draft create and read

### 2.1 Creating a draft stores an empty presentation

Tier: 1

```gherkin
Given a signed-in person
When the person creates a presentation with title "LinAlg"
Then the presentation is draft
And slide_count is 0
And reading it back shows title "LinAlg" and no slides
And the materials list includes kind presentation with that title and status draft
```

### 2.2 An omitted title becomes the default draft title

Tier: 2

```gherkin
Given a signed-in person
When the person creates a presentation without a title
Then the stored title is "Новая презентация"
And status is draft
```

---

## 3. Add slides — validation

### 3.1 An image over 50 MB is refused

Tier: 1 (hz-05, hz-06)

```gherkin
Given a signed-in person with a draft
When the person adds a jpeg larger than 52428800 bytes
Then the add is refused with file_too_large
And no slide is stored
```

### 3.2 A virus on an image refuses the add

Tier: 1 (hz-02, hz-05)

```gherkin
Given a signed-in person with a draft
And the virus check will report a virus
When the person adds a jpeg
Then the add is refused with virus_detected
And no slide is stored
And no bytes remain for that payload
```

### 3.3 Adding slides without an Idempotency-Key is refused

Tier: 2 (hz-02)

```gherkin
Given a signed-in person with a draft
When the person adds a jpeg without Idempotency-Key
Then the add is refused
And no slide is stored
```

### 3.4 The same Idempotency-Key does not duplicate slides

Tier: 1 (hz-02)

```gherkin
Given a signed-in person with a draft
When the person adds one jpeg twice with the same Idempotency-Key
Then exactly one slide is stored
And both responses describe the same presentation
```

---

## 4. Index

### 4.1 Index with zero slides is refused

Tier: 1 (hz-04, hz-05)

```gherkin
Given a signed-in person with an empty draft
When the person indexes it
Then the index is refused with no_slides
And status stays draft
```

### 4.2 Index with more than forty slides is refused

Tier: 1 (hz-06)

```gherkin
Given a signed-in person with a draft of 41 image slides
When the person indexes it
Then the index is refused with too_many_slides
And status stays draft
```

### 4.3 A successful index reaches ready with searchable pieces

Tier: 1 (hz-02, hz-04)

```gherkin
Given a signed-in person with a draft of one jpeg
And OCR returns plain text for that image
When the person indexes with an Idempotency-Key
Then status becomes ready
And piece_count is at least 1
And slide empty is false
And bytes of the image are gone
And the materials list shows kind presentation status ready
And a second index with the same key does not create a second piece set
```

### 4.4 Empty OCR leaves the slide marked empty and out of search

Tier: 1 (hz-04, hz-07)

```gherkin
Given a signed-in person with two image slides
And OCR returns text for the first and empty for the second
When the person indexes
Then the presentation is ready
And the second slide is empty true and has no search piece
And the first slide is searchable
```

### 4.5 Weak OCR may call the chat LLM once per weak slide

Tier: 2 (hz-02, hz-07)

```gherkin
Given a signed-in person with one image slide
And OCR returns thin text for the image size
And the chat LLM returns phrase and LaTeX
When the person indexes
Then the slide stores formula_phrase and formula_latex
And embeddings used the phrase
And the LLM was called once for that slide
```

---

## 5. Edit, reorder, delete slide

### 5.1 Reorder changes Слайд N positions

Tier: 2 (hz-04)

```gherkin
Given a ready presentation with two slides A then B
When the person patches slide_order to B then A
Then positions are B=1 and A=2
```

### 5.2 Ready text edit keeps status ready

Tier: 1 (hz-04)

```gherkin
Given a ready presentation
When the person patches slide text
Then status remains ready
And the new text is returned on read
```

### 5.3 Deleting the only slide of a draft leaves slide_count 0

Tier: 2

```gherkin
Given a draft with one slide
When the person deletes that slide
Then slide_count is 0
And status is draft
```

---

## 6. Delete presentation

### 6.1 Delete removes searchability and refuses later get

Tier: 1 (hz-04, hz-05)

```gherkin
Given a signed-in person with a ready presentation
And searchable pieces for it
When the person deletes the presentation
Then get by id matches a missing presentation
And search returns no pieces for that id
And the person's chats and quiz attempts that referenced it still exist
```

---

## 7. Progress

### 7.1 Progress without session matches absent

Tier: 1 (hz-05)

```gherkin
Given a person who is not signed in
When the person reads progress
Then the refusal matches progress_not_found
```

### 7.2 Weak count matches topics under 40 percent

Tier: 1 (hz-01)

```gherkin
Given a signed-in person with topics at 30%, 45%, and 80% mastery
When the person reads progress
Then weak_topic_count is 1
And weak_topics contains only the 30% topic
And topics includes all three
And no graph edges field is required
```

### 7.3 Sessions this week count distinct active days

Tier: 2 (hz-07)

```gherkin
Given a signed-in person who finished a quiz today and sent chat yesterday and twice today
When the person reads progress
Then sessions_this_week is 2
```

### 7.4 A foreign material filter looks absent

Tier: 2 (hz-05)

```gherkin
Given a signed-in person
And a neighbour's material id
When the person reads progress with that material filter
Then the refusal matches progress_not_found
```
