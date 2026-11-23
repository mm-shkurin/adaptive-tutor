# AFK blockers — Story 7 Викторины

Started: 2026-11-23 14:03 (local). Budget: 110 min. Branch: `features/quizzes` (from `features/chat`).

Items that need a human decision or that stopped automated delivery. Work continues on everything else.

## Open (human)

1. **Merge `features/chat` → `dev` still human.** Do **not** push `features/quizzes:dev` until chat is on `dev` and merge order with any frontend strip is confirmed.
2. **Stash on `features/chat`:** `afk-wip-frontend-docs` (documents screen WIP). Restore if still needed.
3. **Spec-skeptic still `block` after one revise.** Remaining HIGH were reduced by rewriting `07_Quizzes.md` (definite second-create rule, missing key refused, topic>200 refused, resume unanswered vs answered, account-delete leaves other owners' attempts). **Human should re-run `/spec-skeptic 7 spec` before treating story-spec as done.** AFK continues to Tier 1 implementation with the revised text + defaults below.

## AFK defaults for skeptic questions (confirm or override)

| # | Question | AFK default | Why |
|---|----------|-------------|-----|
| 1 | Wrong-language model body? | Prompt rule only (like chat). Store if shape is valid. Mixed-script topic → still one prompt language hint from dominant script / first letters; no hard reject. | interview.md:50–51 points at chat language rule; chat does not refuse wrong-language bodies. |
| 2 | Open finished card (no open attempt)? | Show last **result** (review + play again). | Result is a required screen; yaml already had status=result; mockup always-Q1 conflicts — result wins until human says otherwise. |
| 3 | How many pieces in the create call? | At most **10**, same as chat `MaterialSearch`. Stored page ∈ pages of pieces actually sent. | Reuse story 4 bound; interview silent on a number. |
| 4 | Whitespace-only topic? Stored topic? | Whitespace-only = empty (refuse, no model). Stored topic = **trimmed**. | Aligns with chat blank-line refuse. |
| 5 | Second create same PDF+topic? Double press two keys? | Later create **may** store another quiz. Same Idempotency-Key → one quiz. Two keys → two quizzes. | Matches chat send attempts. |
| 6 | Topic max 200 / list cap 100? | Keep as **API/adapter caps** in OpenAPI (not interview product rules). Soft until human changes. | Hazard fold; chat had no cap — human may drop. |
| 7 | No ready PDF UI? | Create entry visible; submit refused (`no_ready_document`). | Interview: cannot create. |
| 8 | Both mockup create controls? | **Yes** — header button + tile. | Mockup has both. |

## Resolved in-session

- Branch base: `features/chat` (HttpTutor present).
- Dirty frontend docs stashed off the quizzes branch.
- Hazard GAPs folded or dismissed in `07_Quizzes_Notes.md`; over-invented AC trimmed after skeptic (see revised `07_Quizzes.md`).

## Parking lot

- ExpectedLoad old quiz ceiling not applied.
- Story 8 reads last completed score later.
- Live freellmapi poke out of green pipeline.
- Account delete today only wipes account+avatar for docs/chats (pre-existing); this story still wipes quizzes/attempts for that owner and must not touch other owners'.
