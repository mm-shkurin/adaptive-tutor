# Quizzes

Decisions below were accepted on 2026-11-23 from `interview.md`, with AFK defaults for silent gaps recorded in `AFK_BLOCKERS.md`. The primary person is a signed-in student. The feature works when that student can create a quiz from one ready PDF, answer with immediate grading, leave and resume, finish, and replay the same questions without calling the model again.

## Brief Description

A signed-in person builds a quiz from one of their ready PDFs, answers four-choice questions with an immediate grade and PDF page, finishes to a score, and can replay the stored questions.

## Prerequisites

- The person is signed in. A guest sees the landing, as in story 1.
- The quiz's document is a ready PDF owned by this person. Waiting, indexing, and failed documents cannot be chosen.
- Create reads this PDF's pieces and vectors; it does not write pieces or vectors. Empty retrieval for the topic refuses creation and stores nothing. A ready PDF with no vectors yields empty retrieval the same way.

## Flow

1. A guest sees the landing. A signed-in person opens `/quizzes` (replaces SoonPage). Their quiz list is shown. Another person's quiz looks absent. A call with no session is refused.
2. The list shows this person's quizzes, newest first. Each card shows the document name, the topic, the question count, and the last completed score N of M when one exists. An open unfinished attempt does not change the card's completed score. Header "Create quiz" and the "+" tile both open create.
3. Create needs a ready owned PDF, a non-empty topic after trim, and a count of 3, 5, or 8 (form default 5). Whitespace-only topic is empty. Topic longer than 200 characters is refused. No ready PDF: submit is refused. Blank topic is refused, the model is not called, nothing is stored. Stored topic is the trimmed string. The card heading is that stored topic (one string).
4. "Generate and start" requires an Idempotency-Key. It searches up to ten pieces of that PDF by the topic, makes one freellmapi call (`auto`, same chat channel), validates the reply, stores the quiz and questions, opens take at question 1. The language rule is a prompt (same language as the topic), not a refuse-on-wrong-language store rule. The same key stores one quiz. A new key stores another quiz even on the same PDF and topic. A missing key is refused and nothing is stored. Wrong shape, empty retrieval, timeout, or any channel failure stores nothing and shows creation failed. Create does not rewrite the index.
5. Each stored question has four choices, exactly one correct, and a page from a piece that was sent in the call. The app grades; the model does not. Until a choice is made, the page stays hidden. A wrong choice highlights both the chosen and the correct options. A second choice on the same question leaves the stored grade unchanged. Skip is not a control. Next and Finish do not advance until this question has a stored choice.
6. Leaving for the list before finish keeps one open attempt. Opening that quiz resumes the same question. If that question already has a choice, the choice and page stay shown and are not re-graded. If it has no choice yet, the page stays hidden and Next and Finish stay disabled. Finish shows score N of M and a per-question review (chosen, correct, page).
7. Opening a card with no open attempt and a last completed score shows that result. "Play again" on the result screen starts a new attempt at question 1 with the same stored questions and no model call. The card keeps the previous completed score until the new attempt finishes; then the card shows that new score. Attempt history is not kept — only the last completed score.
8. Deleting the account removes this person's quizzes and attempts and leaves every other owner's quizzes and attempts in place. Examiner chat questions never appear in this list.

## Acceptance Criteria

- Only ready owned PDFs appear for create; other statuses and other people's documents are refused.
- Empty topic, empty retrieval, malformed model reply, timeout, and channel failure store no quiz. Create does not write vectors or pieces.
- Same Idempotency-Key create stores one quiz. A new key stores another. A missing key stores nothing. Replay and resume never call the model.
- Grading is from the stored correct choice; a second answer on that question does not change the grade. Next/Finish require a stored choice on the current question.
- Unfinished attempt resumes on the same question; answered questions keep choice and page; unanswered ones keep the page hidden. Card score stays the last completed one until a new finish.
- Foreign quiz id looks absent. Account delete leaves no quiz or attempt for that person and leaves every other owner's quizzes and attempts.
- Acceptance uses fake completions (valid body, bad body, timeout, empty search). Live freellmapi poke is out of the green pipeline.

## Validation Rules

| Field | Rule |
|-------|------|
| Document | Ready PDF owned by this person. Any other document is refused. |
| Session | Signed-in owner required. |
| Topic | Non-empty after trim. Empty or whitespace-only is refused; model not called. Longer than 200 characters is refused. Language follows the topic via the prompt, like chat. |
| Question count | Only 3, 5, or 8. Form default is 5. Any other value is refused. |
| Choice | One of the four choices on the open question. A second answer does not change the stored grade. |
| Idempotency | Required on create. Same key stores one quiz. A new key stores another. Missing key stores nothing. |

## Screen States

- Guest: landing. No quiz list.
- List at `/quizzes`: cards and both create controls. Empty list with create controls.
- Create form: document, topic, count; failure visible when assembly fails.
- Take: question counter, four choices; unanswered (page hidden); answered right or wrong with page; next / finish enabled only after a choice. No skip.
- Result: score N of M, per-question review, play again, back to list.
- Resume take after leave or reload: same question, stored choice and page, no re-grade.
- Finished card with no open attempt: last result.

## Core Requirements

- One model call per successful create; replay and resume read storage only.
- Citation is a PDF page from a sent piece, never a slide. At most ten pieces in the create call.
- Last completed score is stored on the quiz for story 8; this story does not change the Progress screen.
- Progress UI, presentations, Examiner-to-list bridge, time estimate, and "with sources" badge are out of scope.
