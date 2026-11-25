# AFK blockers — Story 7 Викторины

Branch: `features/quizzes` (from `features/chat`). Session issues: `AFK_SESSION_ISSUES.md`.

Ignore unused `/continue` boxes (`red-acceptance` / `design` / `red-usecase` / …). In delivery-loop, **Done AFK** + green pytest/selenium is enough for that scenario.

---

## Close status (AFK 2026-11-23 ~20:37, budget 110m)

Blocks A–D done in this session. Block E: push without `:dev`.

| Block | Status |
|-------|--------|
| A Tier 2 UI selenium (0.3, 1.2, 1.4, 1.5, 3.2, 4.2) | done |
| B Tier 2 align-design marks | done (same mockup language) |
| C cite `quiz-cite-page` + delivery notes | done |
| D harvest accounting | done |
| E checklist + push (no `:dev`) | this session |

### Remaining human-only

| # | Item | When |
|---|------|------|
| H1 | Merge `features/chat` → `dev` | **done** 2026-11-25 (`6fb5ac9` on `dev`) |
| H2 | Merge `features/quizzes` → `dev` (after H1) | **done** 2026-11-25 (`a0656fb` on `dev`) |
| H3 | `/spec-skeptic 7 spec` until not `block` | Optional before calling story-spec final |
| H4 | `/demo` headed smoke on quizzes (or skip deliberately) | Manual poke |
| H5 | Confirm or override AFK defaults table below | Anytime |

If H3 still blocks: keep AFK defaults; do not invent new product rules.

## AFK defaults (unchanged)

| # | Question | AFK default |
|---|----------|-------------|
| 1 | Wrong-language model body? | Prompt rule only; store if shape valid |
| 2 | Open finished card? | Show last **result** |
| 3 | Pieces in create? | At most **10** |
| 4 | Whitespace topic? | Empty → refuse; store **trimmed** |
| 5 | Second create same PDF+topic? | New key → may store another; same key → one |
| 6 | Topic 200 / list 100? | Keep API caps |
| 7 | No ready PDF UI? | Create entry visible; submit refused |
| 8 | Both create controls? | Header + tile |

## Already done (do not redo)

- Spec: interview, story, api-spec, test-spec
- Tier 1 backend + frontend (incl. green-selenium ×10)
- Tier 2 backend API / security / integration / infra (pytest Done AFK)
- Tier 2 UI selenium: 0.1–0.3, 1.2, 1.4–1.6, 3.2, 4.1–4.3, 6.2, 6.5–6.7 (+ Block A leftovers)
- Cite testid: `quiz-cite-page` (main stays `quiz-page`)
- Harvest checkbox (delivery-loop skip note)

## Parking lot (out of story 7 close)

- ExpectedLoad old quiz ceiling
- Story 8 reads last completed score
- Live freellmapi poke out of green pipeline
- Account delete docs/chats wipe quirk (pre-existing); quizzes wipe is story-owned
- 3.2 `green-frontend` / `green-frontend-api` unchecked — selenium covers; optional vitest later

## Session log

- 16:53–17:20 AFK: Tier 2 API leftovers + T1 selenium + partial T2 UI → pushed through `1a646bc`.
- 20:37 AFK (110m): Block A–E close-out on front strip; issues parked in `AFK_SESSION_ISSUES.md`.
