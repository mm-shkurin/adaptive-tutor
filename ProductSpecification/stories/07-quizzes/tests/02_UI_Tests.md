# Quizzes — UI Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with who cannot see the quizzes, then the list, the form, and take, then generate, then grading, finish, and the links between those screens.
> Acceptance drives the completions fake. The screens do not call live freellmapi.

## 0. Prerequisite guards

### 0.1 A guest sees the landing and not the quizzes

Tier: 2

```gherkin
Given a guest
When the guest opens the product
Then the landing is shown
And the quiz list is not shown
```

### 0.2 No ready PDF shows that a quiz cannot be created

Tier: 2 (hz-04, hz-08)

```gherkin
Given a signed-in person with no ready PDF
When the person opens the quizzes
Then the empty state says a quiz needs a ready PDF
And generating adds no quiz
```

### 0.3 A document that is not ready cannot be chosen

Tier: 2 (hz-04)

```gherkin
Scenario Outline:
Given a signed-in person with a ready PDF
And a document of theirs that is <state>
When the person opens the create form
Then that document is not a choice
And no quiz is bound to it

Examples:
  | state |
  | waiting |
  | indexing |
  | failed |
```

---

## 1. Page display

### 1.1 An empty list shows the create entry

Tier: 1 (hz-08)

```gherkin
Given a signed-in person with no quiz
When the person opens the quizzes
Then the empty list is shown
And the loading state is not left in place of the empty list
And the create entry is shown
And the list does not show a time estimate or a sources badge
```

### 1.2 A card shows the document, the topic, the count, and only the last completed score

Tier: 2

```gherkin
Given a signed-in person with a finished quiz that was started again
When the person opens the quizzes
Then the card shows the document name, the topic, and the question count
And the card shows the last completed score
And the card does not show the open attempt as the score
And the card does not show a time estimate, a sources badge, or a slide
```

### 1.3 An unanswered question hides the page and does not offer skip

Tier: 1

```gherkin
Given a signed-in person on an unanswered question
When the person is taking the quiz
Then four choices are shown
And the page is hidden
And skip is not offered
And next is unavailable
And no slide label is shown
```

### 1.4 The result shows the score and a review of every question

Tier: 2

```gherkin
Given a signed-in person with a finished quiz
When the person opens the result
Then the score is shown as the number right out of the question count
And each question shows the chosen choice, the correct choice, and the page
And play again and back to the list are shown
```

### 1.5 A script in the topic, the question, and a choice is shown as text

Tier: 2 (hz-05, hz-08)

```gherkin
Given a signed-in person
And a topic, a question, and a choice that each contain a script
When the person opens that quiz
Then each of those texts is shown as text
And none of them is a script element
```

### 1.6 The list and the question stay reachable on a narrow window

Tier: 2

```gherkin
Given a signed-in person with a quiz in progress
When the person opens the quizzes on a narrow window
Then the list can be reached
And the question and its choices can be reached
```

### 1.7 The create form lists ready PDFs and defaults the count to five

Tier: 1 (hz-04)

```gherkin
Given a signed-in person with two ready PDFs
When the person opens the create form
Then both ready PDFs are choices
And the question count defaults to five
And the counts offered are three, five, and eight
And the form does not offer a model choice
```

---

## 2. User interaction

### 2.1 A choice shows right or wrong and reveals the page

Tier: 1

```gherkin
Scenario Outline:
Given a signed-in person on an unanswered question
When the person chooses <choice>
Then the grade is shown as <grade>
And the page is shown
And <marked> is marked
And next becomes available

Examples:
  | choice | grade | marked |
  | the correct choice | right | the correct choice |
  | a wrong choice | wrong | the chosen choice and the correct choice |
```

---

## 3. Form submission

### 3.1 Generate and start locks the control and opens the first question

Tier: 1 (hz-08)

```gherkin
Given a signed-in person on the create form
And a ready PDF, a topic, and a question count
And the completions fake returns a valid quiz
When the person generates and starts
Then the generate control stays locked until the quiz opens
And the first question is shown
And the page is hidden
```

### 3.2 A second press while generating stores one quiz

Tier: 2 (hz-02, hz-08)

```gherkin
Given a signed-in person on the create form
And the completions fake returns a valid quiz
When the person generates and starts twice before the first answer returns
Then one quiz is stored
And the first question is shown
```

---

## 4. Validation feedback

### 4.1 A blank topic leaves the list unchanged

Tier: 2

```gherkin
Given a signed-in person on the create form
When the person generates with a blank topic
Then the form says the topic is empty
And the quiz list is unchanged
```

### 4.2 A failed generation shows that the quiz could not be assembled

Tier: 2 (hz-08)

```gherkin
Given a signed-in person on the create form
And the completions fake fails
When the person generates and starts
Then the form says the quiz could not be assembled
And the failure is not an endless spinner
And the quiz list is unchanged
```

### 4.3 Leaving the form before generate stores nothing

Tier: 2 (hz-08)

```gherkin
Given a signed-in person who has typed a topic on the create form
When the person goes back to the list without generating
Then no quiz is stored
And the list does not show that topic as a quiz
```

---

## 5. Server response

### 5.1 Finish shows the score and the review

Tier: 1

```gherkin
Given a signed-in person on the last question
And the person has answered every question
When the person finishes
Then the result shows the score
And the review shows the chosen choice, the correct choice, and the page for every question
```

### 5.2 Play again returns to the first question and the card keeps the previous score

Tier: 1 (hz-02)

```gherkin
Given a signed-in person on the result of a finished quiz
When the person plays again
Then the first question is shown
And the page is hidden
And the card still shows the previous score until the new attempt is finished
```

---

## 6. Navigation

### 6.1 Create opens the form

Tier: 1

```gherkin
Scenario Outline:
Given a signed-in person on the quiz list
When the person uses <entry>
Then the create form is shown

Examples:
  | entry |
  | the create button |
  | the new-quiz tile |
```

### 6.2 Cancel and back return to the list

Tier: 2

```gherkin
Scenario Outline:
Given a signed-in person on the create form
When the person uses <control>
Then the quiz list is shown
And no quiz was stored

Examples:
  | control |
  | cancel |
  | back to the quizzes |
```

### 6.3 Back to the list during a quiz leaves the attempt open

Tier: 1 (hz-04)

```gherkin
Given a signed-in person on an open question
And the card shows a previous completed score
When the person goes back to the quizzes
Then the quiz list is shown
And the card still shows that previous score
And the attempt is still open
```

### 6.4 Opening the card resumes the saved question

Tier: 1

```gherkin
Given a signed-in person whose quiz is open on a later question
When the person opens that card from the list
Then that question is shown
And the earlier answer is still graded
```

### 6.5 Reload resumes the saved question and does not grade again

Tier: 2 (hz-02, hz-08)

```gherkin
Given a signed-in person who has answered the current question
When the person reloads the quiz
Then the same question is shown
And the grade is unchanged
And the model is not called
```

### 6.6 Back to the list from the result shows the completed score

Tier: 2

```gherkin
Given a signed-in person on the result
When the person goes back to the list
Then the quiz list is shown
And the card shows the score from that result
```

### 6.7 The progress screen does not show the quiz score

Tier: 2

```gherkin
Given a signed-in person who just finished a quiz
When the person opens progress
Then the progress screen is unchanged
And that quiz's score is not shown there
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `a guest` | No session. The landing is the story 1 landing |
| `opens the quizzes` | Route `/quizzes` for a signed-in person. This story replaces the soon page |
| `the empty state says a quiz needs a ready PDF` | Create stays visible and generate does not post a quiz. Copy states that a ready PDF is required |
| `a document of theirs that is <state>` | Own document with status `waiting`, `indexing`, or `failed`. The picker lists only `ready` PDFs |
| `the create entry` / `the create button` / `the new-quiz tile` | «Создать викторину» and the «Новая викторина» tile |
| `a time estimate or a sources badge` | No «~12 мин» and no «с источниками» on a card |
| `a slide` | No «Слайд N» on a card or a citation. The citation is the PDF page |
| `skip is not offered` | The skip control from the mockup stays hidden |
| `next is unavailable` | «Далее» is disabled until a choice. On the last question the control reads «Завершить» |
| `the question count defaults to five` | The count control's selected value is 5. Options are 3, 5, and 8 |
| `the form does not offer a model choice` | No model `<select>` on the create form. The request uses `auto` |
| `generates and starts` | «Сгенерировать и начать». The control is disabled while the request is in flight and sends one `Idempotency-Key` |
| `generates and starts twice before the first answer returns` | Two activations before the create response. One `POST /api/v1/quizzes` |
| `the form says the topic is empty` | Inline error for an empty or spaces-only topic. No create request that stores a quiz |
| `the form says the quiz could not be assembled` | The create failure `generation_failed` is shown as text, with the form usable again |
| `goes back to the quizzes` / `back to the quizzes` / `cancel` | «К викторинам», «Отмена», or «К списку» |
| `plays again` | «Пройти ещё раз» |
| `finishes` | «Завершить» on the last answered question |
| `reloads the quiz` | Browser reload of the open take route |
| `the progress screen is unchanged` | The progress route renders the same screen as before this story and does not list this quiz's score |
| `the completions fake` | The story's fake. The browser flow does not call live freellmapi |
| `shown as text` / `a script element` | The characters `<script>` are text nodes, not executable markup |
| `on a narrow window` | Viewport at the mobile mockup width. List and take are reachable without a second layout |
