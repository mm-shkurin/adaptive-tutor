# AFK issues — Story 3 — 2026-11-26

Session: `/delivery-loop afk story 3` started **2026-11-26 08:38**, budget **110 min** (soft stop ~10:13, hard ~10:28).
Branch: `features/presentations`.
Prior parked items remain in `AFK_ISSUES.md`; this file is **this session only**.

Questions are **not** asked in chat. Defaults / park notes go here; work continues on unblocked chunks.

---

## Session queue (ready without human)

1. UI 1.4 — index → documents list ready presentation row (libraryView draft + presentation meta + tests; selenium if stack allows)
2. Close editor after successful index so Documents is visible (AFK default if UX silent)
3. Tier 2 harvest candidates if budget: API 2.2 default title, UI 2.1 ready text, UI 3.2 weak list, reorder 5.1
4. Optional formal hazard-scan / tiering — only if remaining time ≥15m and no higher-value code left
5. End: progress + commits + push + report (no merge to `dev`)

## AFK defaults this session

| # | Open item | AFK default | Why |
|---|-----------|-------------|-----|
| S1 | After successful index, stay in editor or show Documents? | **Close editor after ready index** so Documents list with ready row is visible (matches UI 1.4 wording). | Spec says list shows ready row when indexing finishes; list is unmounted while editor open. |
| S2 | Presentation row meta without `page_count` | **Kind-specific meta:** draft → «черновик»; ready → «N чанков» (no «null стр.»); indexing/waiting labels without fake page counts. | `Document.presentation_row` leaves `page_count=None`. |

## Parking lot (do not block)

| # | Item | Notes |
|---|------|-------|
| Q1 | Dirty newline-only `__init__.py` WIP + discussion.md from prior AFK | Fold discussion into handoff/commit if still valid; discard empty `__init__` noise or leave unstaged. |
| Q2 | Live OCR / Tesseract | Still FakeOcr — prior P3/P13. |
| Q3 | Merge `features/presentations` → `dev` | Human order. |
| Q4 | Confirm AFK defaults D1–D5 | Human poke. |
| Q5 | Selenium full presentation journey if infra down | Vitest covers row mapping; park selenium fail reason here. |
| Q6 | P8 chat `person_send_times` in Postgres | Prior parking; touch only if budget after Tier 1 UI. |

## Session log

| Time | Event |
|------|-------|
| 08:38 | Start AFK 110m on `features/presentations`; queue from progress.md |
| 08:40 | UI 1.4: libraryView draft+ready presentation rows; leaveEditorAfterIndex; close editor on ready; CSS draft pill; sanity fail observed |
| 08:42 | Open row via GET; UI 2.1 ready text helpers; API 2.2/5.1/5.3 pytest green (13) |
