# Chat — UI Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with who cannot see the composer, then the chat screen, then new chat, switch, and the paperclip, then a whole reply and the four turns.

## 0. Prerequisite guards

### 0.1 A guest sees the landing and not the chat

Tier: 2

```gherkin
Given a guest
When the guest opens the product
Then the landing is shown
And the chat list is not shown
And the composer is not shown
```

### 0.2 No ready PDF shows an empty state and send adds nothing

Tier: 2 (hz-04, hz-08)

```gherkin
Given a signed-in person with no ready PDF
When the person opens the chat
Then the empty state is shown
And sending adds no line
```

### 0.3 A document that is not ready cannot be chosen

Tier: 2 (hz-04)

```gherkin
Scenario Outline:
Given a signed-in person with a ready PDF
And a document of theirs that is <state>
When the person opens the chat
Then that document is not a choice for a new chat or a switch
And no chat is bound to it

Examples:
  | state |
  | waiting |
  | indexing |
  | failed |
```

### 0.4 The material that cannot be asked yet shows the sentence and send adds nothing

Tier: 2 (hz-04)

```gherkin
Given a signed-in person whose chat cannot be asked yet
When the person opens that chat
Then the chat says the material cannot be asked yet
And sending adds no line
```

---

## 1. Page display

### 1.1 The chat screen shows the list, the thread, and the sources

Tier: 1

```gherkin
Given a signed-in person with a chat that has a person line and a tutor line
When the person opens that chat
Then the list row shows the document name and the last person line
And the thread shows the person line, the tutor line, the model, and the page
And the sources show the page and the piece text
And the citation is a page, not a slide
```

### 1.2 Nothing in the material shows an empty sources panel

Tier: 2

```gherkin
Given a signed-in person whose last reply is not in the material
When the person opens that chat
Then the tutor says it is not in the material
And the sources panel is empty
```

### 1.3 A source without a page shows the piece text and no page number

Tier: 2 (hz-04)

```gherkin
Given a signed-in person whose reply cites a piece with no page
When the person opens that chat
Then the bubble has no page
And the source shows the piece text without a page number
```

### 1.4 History and sources stay reachable on a narrow window

Tier: 2

```gherkin
Given a signed-in person with a chat that has a tutor line and a source
When the person opens that chat on a narrow window
Then the history can be reached
And the sources can be reached
```

### 1.5 A script in the thread, the preview, and the source is shown as text

Tier: 2 (hz-05)

```gherkin
Given a signed-in person
And a person line, a tutor line, a list preview, and a source that each contain a script
When the person opens that chat
Then each of those texts is shown as text
And none of them is a script element
```

---

## 2. New chat, switch, and the paperclip

### 2.1 New chat opens an empty thread on the selected PDF

Tier: 1 (hz-04)

```gherkin
Given a signed-in person with a selected ready PDF
When the person starts a new chat
Then the thread is empty
And the chat is bound to the selected PDF
```

### 2.2 Switching document keeps the old chat and shows the chosen PDF

Tier: 2 (hz-04)

```gherkin
Given a signed-in person reading a chat that has a person line
When the person switches to another ready PDF
Then the old chat remains in the list with that person line
And the thread shown is the chat for the PDF just chosen
```

### 2.3 The paperclip opens Documents and adds no document

Tier: 2

```gherkin
Given a signed-in person on the chat
When the person uses the paperclip
Then Documents is shown
And no document is added
```

### 2.4 The last model and the last mode stay on this device

Tier: 2

```gherkin
Given a signed-in person who chose a model and a mode
When the person opens the chat again on this device
Then that model is still chosen
And that mode is still chosen
```

### 2.5 A double-clicked new chat or switch stores one chat

Tier: 2 (hz-08)

```gherkin
Scenario Outline:
Given a signed-in person with a selected ready PDF
When the person activates <control> twice without waiting
Then one chat effect is stored

Examples:
  | control |
  | new chat |
  | switch document |
```

### 2.6 Unsent text is still in the composer after leaving and returning

Tier: 2 (hz-08)

```gherkin
Given a signed-in person who has typed a line and not sent it
When the person switches documents and returns to that chat
Then the unsent line is still in the composer
```

---

## 3. Replies

### 3.1 Send shows the whole tutor line with the page

Tier: 1

```gherkin
Given a signed-in person with an askable chat
When the person sends a question
Then the tutor line appears whole
And the line shows the model and the page
```

### 3.2 A blank line leaves the thread unchanged

Tier: 2

```gherkin
Given a signed-in person with an askable chat
When the person sends a blank line
Then the thread is unchanged
And the refusal is shown
```

### 3.3 A double-clicked send stores one line

Tier: 2 (hz-08)

```gherkin
Given a signed-in person with an askable chat
When the person activates send twice without waiting
Then the thread shows one person line and one tutor line
```

### 3.4 Socratic shows a question without a page

Tier: 2 (hz-04)

```gherkin
Given a signed-in person with an askable chat
When the person sends a question in Socratic mode
Then the tutor shows a question without a page
```

### 3.5 A try shows the answer with a page

Tier: 2 (hz-04)

```gherkin
Given a signed-in person whose tutor is withholding
When the person sends a try
Then the tutor shows the answer with a page
```

### 3.6 The tell control shows the page without a person line

Tier: 2 (hz-04)

```gherkin
Given a signed-in person whose tutor is withholding
When the person uses the tell control
Then the answer with a page is shown
And no person line is added
```

### 3.7 Examiner shows one question with four choices and no page

Tier: 2 (hz-04)

```gherkin
Given a signed-in person with an askable chat
When the person chooses Examiner
Then one question with four choices is shown
And the page is not shown yet
```

### 3.8 A choice shows right or wrong with the page

Tier: 2 (hz-04)

```gherkin
Given a signed-in person with an open examiner question
When the person chooses a choice
Then right or wrong is shown with the page
```

### 3.9 After three grades an academic answer is shown

Tier: 2 (hz-04)

```gherkin
Given a signed-in person whose examiner series has three grades
When the person sends a line
Then an academic answer with a page is shown
And the quiz list does not contain those questions
```

### 3.10 A second click on the same choice does not change the grade

Tier: 2 (hz-04)

```gherkin
Given a signed-in person whose examiner question is already graded
When the person chooses again
Then the grade is unchanged
```

### 3.11 A failed reply is shown on the chat

Tier: 2 (hz-08)

```gherkin
Given a signed-in person whose reply failed
When the person looks at the chat
Then the person's line is shown
And no tutor line is shown
And the failure message is shown
And the screen is not left spinning
```

### 3.12 After a failed reply a new line can be sent

Tier: 2

```gherkin
Given a signed-in person whose reply failed
When the person sends a new line
Then that line is shown
```

### 3.13 A late reply is not painted on the chat now shown

Tier: 2 (hz-08)

```gherkin
Given a signed-in person who sent a line and then switched documents
When the reply for the chat they left arrives
Then that reply is not painted on the chat now shown
```

### 3.14 A double-clicked Examiner, choice, or tell stores one effect

Tier: 2 (hz-08)

```gherkin
Scenario Outline:
Given a signed-in person who can <act>
When the person activates that control twice without waiting
Then one effect is stored

Examples:
  | act |
  | choose Examiner |
  | choose a choice on an open question |
  | use the tell control |
```

### 3.15 A later response that arrives first is not replaced by the earlier one

Tier: 2 (hz-08)

```gherkin
Given a signed-in person with two sends still in flight on the open chat
When the later response arrives before the earlier one
Then the thread shows the later response
And the earlier response does not remove it
```

### 3.16 While the reply is in flight the screen shows that it is working

Tier: 2 (hz-08)

```gherkin
Given a signed-in person with an askable chat
When the reply is still in flight
Then the screen shows that it is working
And that state is not the failure message
```

---

## 4. Navigation

### 4.1 A source card does not open the PDF

Tier: 2

```gherkin
Given a signed-in person whose chat has a source
When the person activates that source
Then the PDF does not open
And the source still shows the page and the piece text
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `a guest` | No session. The app opens on the landing from story 1 |
| `opens the chat` | The chat tab is the active panel |
| `the empty state` | Copy that there is no ready PDF. The send control does not submit |
| `not a choice` | The document is absent from the new-chat and switch choices |
| `the material cannot be asked yet` | The notice «Материал пока нельзя спросить.» |
| `a narrow window` | Viewport under 960px. History and sources remain in the tab order or a control that reveals them. They are not `display: none` with no other way to reach them |
| `starts a new chat` | The «Новый чат» button |
| `switches to another ready PDF` | The «Сменить документ» button, then that PDF |
| `uses the paperclip` | The attach control. Navigation goes to the Documents tab. No upload request is sent |
| `on this device` | `localStorage` keys for the last model id and the last mode. The server is not sent a preference write |
| `the tutor line appears whole` | One bubble is inserted when the response arrives. No partial tokens |
| `a blank line` | The composer text is empty or whitespace. Inline refusal, no POST body stored |
| `activates send twice without waiting` | Two clicks before the first response. One `POST /api/v1/chats/{id}/messages` |
| `Socratic mode` / `Examiner` / `the tell control` | The mode buttons «Сократический», «Экзаменатор», and the control on a withheld question |
| `the quiz list` | The quizzes tab does not gain a card from the three questions |
| `whose reply failed` | The send returned `reply_failed`. The person bubble stays. The composer stays usable |
| `the reply is not painted` | The response body is ignored by the screen whose open chat id differs from `chat_id` |
| `activates that source` | Click or keyboard activation of the source card does not navigate and does not open a PDF viewer |
