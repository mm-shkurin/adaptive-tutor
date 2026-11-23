# Story 7: Викторины — Progress

## Spec
- [x] interview
- [x] story
- [x] api-spec
- [x] test-spec

## Delivery notes

Default strip: `/backend-delivery` (code → tests from test-spec → refactor). Spec-skeptic still open — see `AFK_BLOCKERS.md`.

Backend Tier 2 API / security / integration / infra leftovers covered in the second AFK pass (session-store fail, examiner isolation, language, Unicode, last-write fail, list cap, invalid/concurrent answer, wipe-none, XSS text, mass-assignment ignore, key length, dead store, missing model key). Selenium Tier 1 and harvest still open.

Frontend lane: `/quizzes` replaces SoonPage (list, create, take, result, resume) and talks to `/api/v1/quizzes`. Vitest covers the view and create logic. Tier 1 screens match the quiz mockup; the card still omits the time estimate and the sources badge, and take still omits skip. Selenium and demo stay open, and Tier 2 align-design stays clear. `green-frontend` and `green-frontend-api` are checked for the Tier 1 scenarios the screens and client implement.

## Tier 1 — Backend (API 4.1, 7.1, 8.1, 8.3, 9.1, 10.1)

- [x] implement domain + usecase + HTTP + store (create → answer → advance → finish → resume → retry)
- [x] tests from Tier 1 API (sanity fail once, then green)
- [x] commit behavior + this progress
- [x] refactor (quiz types already one concept each, files under 200 lines; no high-value smell; no separate commit)
- [x] account Tier 1 API scenarios done

## Tier 1 — Frontend Scenarios (02_UI_Tests.md)

### 1.1 An empty list shows the create entry
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [x] align-design
- [x] green-selenium
- [ ] demo

### 1.3 An unanswered question hides the page and does not offer skip
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [x] align-design
- [x] green-selenium
- [ ] demo

### 1.7 The create form lists ready PDFs and defaults the count to five
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [x] align-design
- [x] green-selenium
- [ ] demo

### 2.1 A choice shows right or wrong and reveals the page
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [x] align-design
- [x] green-selenium
- [ ] demo

### 3.1 Generate and start locks the control and opens the first question
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [x] align-design
- [x] green-selenium
- [ ] demo

### 5.1 Finish shows the score and the review
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [x] align-design
- [x] green-selenium
- [ ] demo

### 5.2 Play again returns to the first question and the card keeps the previous score
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [x] align-design
- [x] green-selenium
- [ ] demo

### 6.1 Create opens the form
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [x] align-design
- [x] green-selenium
- [ ] demo

### 6.3 Back to the list during a quiz leaves the attempt open
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [x] align-design
- [x] green-selenium
- [ ] demo

### 6.4 Opening the card resumes the saved question
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [x] align-design
- [x] green-selenium
- [ ] demo

## Harvest — Tier 1 → Tier 2

- [ ] harvest — Tier 1 UI selenium green; demo still open. AFK skips headed demo; harvest can start for Tier 2 frontend after human demo or intentionally without demo.

## Tier 2 — Backend Scenarios (01_API_Tests.md)

Done AFK — tests from the spec, green on the backend-delivery strip. The red/green boxes under each heading stay the unused chain.

- [x] 2.1 An empty quiz list is the person's own list
- [x] 3.1 A blank topic is refused and nothing is stored
- [x] 3.2 A question count outside 3, 5, and 8 is refused and nothing is stored
- [x] 5.1 An empty search for the topic stores nothing
- [x] 5.2 A reply of the wrong shape stores nothing and does not pin the attempt
- [x] 6.1 The list is newest first and an open attempt does not change the completed score
- [x] 4.4 The same create attempt stores one quiz and a new attempt may store another
- [x] 4.5 Two creates in flight with the same attempt store one quiz
- [x] 8.2 Advance before a choice is refused
- [x] 8.4 Choose and advance after finish are refused
- [x] 11.1 Deleting the account removes that person's quizzes and attempts
- [x] Security 1.1 Another person's quiz or document is refused like a missing quiz
- [x] Security 1.2 The quiz list does not include another person's quiz
- [x] 1.1 A call with no session is refused like a missing quiz
- [x] 1.2 A session store failure is refused like a missing quiz
- [x] 1.3 A document that is not ready cannot start a quiz
- [x] 1.4 A person with no ready PDF cannot start a quiz
- [x] 2.2 An examiner series does not appear on the quiz list
- [x] 4.2 The questions and the choices follow the topic's language
- [x] 4.3 Topic, questions, and choices round-trip as Unicode
- [x] 5.3 A failed last write leaves no quiz, no questions, and no attempt
- [x] 6.2 The list returns at most the declared cap
- [x] 7.2 A choice that is not on the question is refused
- [x] 7.3 Two answers at the same moment leave one grade
- [x] 11.2 A delete with no account removes nothing

### 1.1 A call with no session is refused like a missing quiz — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.2 A session store failure is refused like a missing quiz — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.3 A document that is not ready cannot start a quiz — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.4 A person with no ready PDF cannot start a quiz — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 An empty quiz list is the person's own list — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.2 An examiner series does not appear on the quiz list — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 3.1 A blank topic is refused and nothing is stored — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 3.2 A question count outside 3, 5, and 8 is refused and nothing is stored — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.2 The questions and the choices follow the topic's language — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.3 Topic, questions, and choices round-trip as Unicode — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.4 The same create attempt stores one quiz and a new attempt may store another — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.5 Two creates in flight with the same attempt store one quiz — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 5.1 An empty search for the topic stores nothing — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 5.2 A reply of the wrong shape stores nothing and does not pin the attempt — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 5.3 A failed last write leaves no quiz, no questions, and no attempt — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 6.1 The list is newest first and an open attempt does not change the completed score — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 6.2 The list returns at most the declared cap — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 7.2 A choice that is not on the question is refused — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 7.3 Two answers at the same moment leave one grade — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 8.2 Advance before a choice is refused — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 8.4 Choose and advance after finish are refused — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 11.1 Deleting the account removes that person's quizzes and attempts — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 11.2 A delete with no account removes nothing — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

## Tier 2 — Integration Scenarios (06_Integration_Tests.md)

Done AFK — tests from the spec, green on the backend-delivery strip. Empty search does not call the model: API 5.1.

- [x] 1.1 A valid completions body creates one quiz and the live model is not called
- [x] 1.2 Resume and play again do not call the model
- [x] 2.1 A failed completions call stores nothing and does not pin the attempt
- [x] 3.1 A failed search stores nothing and does not call the model

### 1.1 A valid completions body creates one quiz and the live model is not called — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.2 Resume and play again do not call the model — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 A failed completions call stores nothing and does not pin the attempt — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 3.1 A failed search stores nothing and does not call the model — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

## Tier 2 — Frontend Scenarios (02_UI_Tests.md)

### 0.1 A guest sees the landing and not the quizzes
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [x] green-selenium
- [ ] demo

### 0.2 No ready PDF shows that a quiz cannot be created
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [x] green-selenium
- [ ] demo

### 0.3 A document that is not ready cannot be chosen
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 1.2 A card shows the document, the topic, the count, and only the last completed score
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 1.4 The result shows the score and a review of every question
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 1.5 A script in the topic, the question, and a choice is shown as text
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 1.6 The list and the question stay reachable on a narrow window
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [x] green-selenium
- [ ] demo

### 3.2 A second press while generating stores one quiz
- [ ] red-selenium
- [ ] red-frontend
- [ ] green-frontend
- [ ] red-frontend-api
- [ ] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 4.1 A blank topic leaves the list unchanged
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [x] green-selenium
- [ ] demo

### 4.2 A failed generation shows that the quiz could not be assembled
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 4.3 Leaving the form before generate stores nothing
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [x] green-selenium
- [ ] demo

### 6.2 Cancel and back return to the list
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [x] green-selenium
- [ ] demo

### 6.5 Reload resumes the saved question and does not grade again
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [x] green-selenium
- [ ] demo

### 6.6 Back to the list from the result shows the completed score
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [x] green-selenium
- [ ] demo

### 6.7 The progress screen does not show the quiz score
- [ ] red-selenium
- [ ] red-frontend
- [x] green-frontend
- [ ] red-frontend-api
- [x] green-frontend-api
- [ ] align-design
- [x] green-selenium
- [ ] demo

## Tier 2 — Security Scenarios (05_Security_Tests.md)

### 1.1 Another person's quiz or document is refused like a missing quiz — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.2 The quiz list does not include another person's quiz — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 A script and a SQL fragment round-trip as the person's own text — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 3.1 Server-owned fields on create are ignored — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 3.2 Server-owned fields on an answer are ignored — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.1 A topic or an idempotency key past its maximum is refused — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

## Tier 2 — Infrastructure Scenarios (04_Infrastructure_Tests.md)

Done AFK — dead store, recovery, connection baseline, missing model key, redacted failure body.

### 1.1 A dead quiz store refuses a read — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.2 A dead quiz store refuses a write and stores nothing — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.3 The list reads back after the store recovers — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.4 One quiz is stored after the store recovers — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.5 Repeated failed creates return the store connections to baseline — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 A missing model key does not stop startup — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.2 A missing model key fails the create and stores nothing — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 3.1 A failure body and its log omit the document text, a secret, and another person's quiz — Done AFK
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance
