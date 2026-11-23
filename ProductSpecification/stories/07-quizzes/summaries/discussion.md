## discussion (2026-11-23)

**Decision:** AFK defaults for silent interview gaps: language is prompt-only (like chat); finished card opens last result; create uses at most 10 pieces; whitespace topic is empty and stored topic is trimmed; same Idempotency-Key → one quiz, new key → another; topic max 200 and list cap 100 stay as API caps; no-ready-PDF refuses submit; both mockup create controls ship.
**Why:** Spec-skeptic blocked on unspecified edges; AFK continued delivery with defaults in `AFK_BLOCKERS.md` and folded them into `07_Quizzes.md`.
**Where applied:** `07_Quizzes.md`, `AFK_BLOCKERS.md`, `api-specs/quizzes.yaml`

## discussion (2026-11-23)

**Decision:** Branch `features/quizzes` from `features/chat` (not bare `dev`) while chat is merge-ready but not yet on `dev`.
**Why:** Interview requires `HttpTutor` / chat channel for quiz generation; `dev` lacks it until human merges chat.
**Where applied:** git branch base; merge-to-dev still blocked in `AFK_BLOCKERS.md`

## discussion (2026-11-23)

**Quirk:** Account delete now runs `QuizWipe` for that owner's quizzes/attempts, but documents and chats still have no FK cascade and are not wiped.
**Where:** `usecase/quiz/wipe.py`, `ProfileService` wipe hooks in `application/context.py`
**Implication:** Story 7 delete tests assert quizzes gone; do not assume docs/chats are gone until a later wipe is added.

## green-selenium (2026-11-23)

**Quirk:** Both the quizzes `<main>` and the take-screen source cite used `data-testid="quiz-page"`.
**Where:** `QuizScreen.jsx` (main) and `QuizTake.jsx` (cite inside `quiz-reveal`)
**Resolved AFK:** Cite renamed to `data-testid="quiz-cite-page"`; main stays `quiz-page`.

## align-design (2026-11-23)

**Decision:** Tier 2 UI screens reuse Tier 1 quiz mockup language (list/create/take/result); no pixel drift pass beyond marking `[x] align-design`.
**Why:** AFK Block B — busywork skip when already matching.

## green-selenium (2026-11-23)

**Quirk:** AppShell renders `quizzes-tab` twice (header + bottom nav); on a narrow window the header tab is not interactable.
**Where:** `AppShell.jsx` `tabTestId('/quizzes')`
**Implication:** Click the first *displayed* `quizzes-tab`, not `find_elements(...)[0]`.

## discussion (2026-11-23)

**Decision:** Delivery-loop AFK closes story-7 Tier 2 by writing selenium/vitest directly and marking `harvest` with a skip note — it does not run `/continue` red-agent harvest.
**Why:** Harvest skill is continue-pipeline fanout; delivery-loop queue already has green Tier 1 UI and a remaining front selenium list in `AFK_BLOCKERS.md`.
**Where applied:** `AFK_BLOCKERS.md` Next AFK queue Block D; `progress.md` harvest checkbox
