# AFK issues — Story 3 — 2026-11-26b

Session: `/delivery-loop afk story 3` started **2026-11-26 08:59**, budget **110 min** (soft stop ~10:34, hard ~10:49).
Branch: `features/presentations`.
Prior parked items: `AFK_ISSUES.md`, `AFK_ISSUES_2026-11-26.md`. This file is **this session only**.

Questions are **not** asked in chat. Defaults / park notes go here; work continues on unblocked chunks.

---

## Session queue (ready without human)

1. Integration Tier 1 gaps: virus timeout add (1.1), OCR transport fail index (1.2)
2. Integration / infra Tier 2: embeddings fail (1.3), fakes wiring (infra 1.1), missing virus config (infra 1.2) — already have formula timeout 1.4
3. D1 tombstone UI «Источник удалён» when material join fails (quiz/chat cards)
4. Split oversized files breaking `check_repo_rules` (chat_store, support, test_presentation_flow)
5. Selenium presentation/progress only if Docker stack comes up
6. End: progress + commits + push + report (no merge to `dev`)

## AFK defaults this session

| # | Open item | AFK default | Why |
|---|-----------|-------------|-----|
| T1 | Where to show «Источник удалён» | Quiz list / chat material label when document join missing after hard-delete | Matches D1; list/editor of presentations already 404 absent |
| T2 | Virus timeout refusal code | Same body as virus_detected (PDF pattern) | Spec says `virus_detected` on timeout |
| T3 | OCR / embeddings index failure status | `failed`; no searchable pieces left | Spec 1.2 / 1.3 |
| T4 | Recovery after failed index | **Re-index and add slides allowed from `failed`**; keep slide bytes on fail (erase only on ready) | Otherwise deck is stuck until delete |

## Parking lot (do not block)

| # | Item | Notes |
|---|------|-------|
| R1 | Live OCR / Tesseract | Still FakeOcr — P3/P13; needs binary + adapter design poke |
| R2 | HttpFormulaAssist multimodal | Prod Noop; need FREE_LLM image enricher decision |
| R3 | Merge → `dev` | Human |
| R4 | Confirm D1–D5 | Human |
| R5 | Docker daemon / Selenium | Docker later up; Selenium UI 1.1/1.3/2.2/3.1 green. UI 1.4 gallery upload parked — `slide-from-gallery` is a button, hidden file input has no testid |
| R6 | Formal hazard-scan / tiering / spec-skeptic | Optional; Notes + provisional Tier markers exist |
| R7 | Load 40-slide 5-min budget | Needs real OCR timing; keep Tier 2 parked or synthetic deadline test |
| R8 | Drag-and-drop reorder | ↑↓ already shipped |
| R9 | Docker backend image / alembic head | **Done this AFK** — rebuilt `adaptive-tutor-backend:local`; alembic now `0018_chat_line_created_at` |

## Session log

| Time | Event |
|------|-------|
| 08:59 | Start AFK 110m; queue from progress + test-spec gaps |
| 09:05 | IndexPresentation fail paths (OCR / StoreUnavailable); FakeOcr.fail; virus timeout + embeddings + infra tests |
| 09:08 | Tombstone D1: DELETED_SOURCE_NAME on quiz/chat after delete; Postgres chat outerjoin |
| 09:10 | Split chat_store attempts + support_auth; flow/index test split; repo rules green |
| 09:12 | material_row error + libraryView failed meta; load budget; FE tombstone vitest |
| 09:14 | Docker Desktop up; AcceptanceServer wire presentations; Selenium UI 1.1 / 3.1 green |
| 09:16 | Note: docker backend alembic still at `0012_quizzes` — needs image rebuild + upgrade for live poke (R9) |
