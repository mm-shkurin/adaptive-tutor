# AFK session issues — Story 7 (2026-11-23 ~20:37)

Budget: **110 min** (user: 1h50m). Branch: `features/quizzes`.
Mode: sequential blocks A→E; no mid-loop questions. Problems land here; work continues.

## Parked / needs human

| # | Item | Severity | Note |
|---|------|----------|------|
| P1 | Merge `features/chat` → `dev` | human | Do not push quizzes `:dev` until H1 |
| P2 | Merge `features/quizzes` → `dev` | human | After H1 |
| P3 | `/spec-skeptic 7 spec` still `block` | human | AFK defaults stand; do not invent product rules |
| P4 | `/demo` headed smoke | human | Skipped in AFK by design |
| P5 | 3.2 `green-frontend` / `green-frontend-api` | low | Selenium covers double-generate; no separate vitest for createLock yet |
| P6 | `check_repo_rules.py --scope front` line-cap | pre-existing | Failures include `useQuizzesScreen.js` (299), `quiz.css` (410), `quizView.test.js` (249) plus chat/docs files — not introduced by Block A; split later |
| P7 | Docker backend image stale migrations | fixed 2026-11-25 | Rebuild `adaptive-tutor-backend:local` so alembic sees `0011`/`0012`; poke via gateway `:80` + API `:8010` |

## Session log

- 20:37 start. Queue: Block A selenium → B align → C cite rename → D harvest → E push.
- Block A: 6 selenium green (hold/fail probe wired). XSS assert ignores Vite `<script>` tags; checks quiz surfaces + no alert(1) injection.
- Block B–D: align-design marks; `quiz-cite-page`; harvest checked.
- Block E: vitest 64; quiz selenium 25; rules line-cap parked P6; push without `:dev`.
