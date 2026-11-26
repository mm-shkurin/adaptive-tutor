# AFK issues — Story 3 — 2026-11-26d

Session: `/delivery-loop afk story 3 презентация` started **2026-11-26 22:07**, budget **110 min** (soft stop ~23:42, hard ~23:57).
Branch: `features/presentations`.
Prior: `AFK_ISSUES.md`, `AFK_ISSUES_2026-11-26.md`, `AFK_ISSUES_2026-11-26b.md`, `AFK_ISSUES_2026-11-26c.md`.

Questions are **not** asked in chat. Park here; keep shipping unblocked work.

---

## Session queue (ready without human)

1. Gap audit: test-spec vs pytest/vitest/selenium leftovers
2. Ship any missing Tier 1/2 coverage that code already supports
3. Selenium gaps if stack up (UI 2.1 / 3.2 / 3.3 / gallery if not flaky)
4. Refactor / repo-rules if oversized presentation files
5. Local CI sweep (presentation-focused + `--fast` if time)
6. End: progress + push + AFK report (no merge to `dev`)

## AFK defaults this session

| # | Open item | AFK default | Why |
|---|-----------|-------------|-----|
| S1 | Story ~99% — what to do for 110m | Harden remaining coverage + CI; do not invent new scope | Progress checklist complete except human gates |
| S2 | Live OCR / FormulaAssist | Stay FakeOcr + Noop; park only | Needs binary + poke (P3/P4) |
| S3 | Merge / D1–D5 / spec-skeptic | Human; not this AFK | delivery-loop: no merge in afk |

## Parking lot (do not block)

| # | Item | Notes |
|---|------|-------|
| D1 | Live OCR / Tesseract | Still FakeOcr |
| D2 | HttpFormulaAssist | Still Noop |
| D3 | Merge → `dev` | Human |
| D4 | Confirm D1–D5 | Human |
| D5 | Formal `/hazard-scan` `/tiering` `/spec-skeptic` | Optional |
| D6 | Headless gallery file upload | Flaky; UI 1.4 uses API seed |

## Session log

| Time | Event |
|------|-------|
| 22:07 | Resume AFK 110m; clean tree on `features/presentations`; start gap audit |
| 22:10 | Gap audit: Selenium UI 2.1/3.2/3.3 + FE line-limit leftovers shippable |
| 22:14 | Selenium UI 2.1 green; 3.2/3.3 selector fixes then green |
| 22:17 | Split documents hooks + bodyGuards + CSS under 200; vitest 47 green |
| 22:18 | Progress updated; commit + push next (no merge) |
