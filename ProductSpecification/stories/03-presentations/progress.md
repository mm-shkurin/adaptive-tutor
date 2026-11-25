# Story 3: Презентации (+ прогресс) — Progress

AFK started 2026-11-25 ~21:58, budget 110m. Branch `features/presentations`. Issues: `AFK_ISSUES.md`.

## Spec
- [x] interview (2026-11-25; open gaps → AFK defaults)
- [x] story (`03_Presentations.md` + Notes)
- [x] api-spec (`endpoints.md`, `presentations.yaml`, `progress.yaml`, `documents.yaml` kind)
- [x] test-spec (`tests/01`–`06`)
- [ ] hazard-scan fold on tests (parked — AFK used Notes fold; formal scan optional)
- [ ] tiering (provisional Tier markers in test files; formal `/tiering` optional)

## Delivery notes

Default strip: `/backend-delivery` (no per-layer red/green). Spec-skeptic / merge / live OCR poke = human (`AFK_ISSUES.md`).

## Tier 1 — Backend

- [x] implement create draft → add image slide → index (fakes) → list kind=presentation → delete
- [x] tests from Tier 1 API — `test_presentation_guards.py` + `test_presentation_flow.py` (20 passed)
- [x] commit behavior + this progress
- [x] refactor (split oversized files / bodyGuards kind+draft; folded into behavior commit for AFK)
- [x] account Tier 1 API scenarios done (1.1–1.3, 2.1, 3.1–3.2, 3.4, 4.1–4.3, 4.4, 5.2, 6.1, 7.1 unsigned); 4.2 index>40 → slide_limit on add
- [x] GET `/api/v1/progress` — materials chips, topic mastery from quiz `last_score`, weak &lt;40%, sessions (quiz finish + chat send in memory), activity; `?material=` foreign → `progress_not_found`; migration `0017_quiz_finished_at`; `test_progress.py` (7.2–7.4, 7.3 Tier 2)
- [x] Postgres `PostgresPresentationStore` + migration `0014` (slide bytes, add/index idempotency snapshots); wired in production context (memory store unchanged for pytest)

## Tier 1 — Frontend (after backend meeting point)

- [x] door opens editor (UI 1.1 — createPresentation, PresentationEditor, vitest door)
- [x] gallery add + slide cards (UI 1.2 — addSlides, slide-from-gallery, slide-card)
- [x] camera capture=environment (UI — slide-from-camera, same addSlides path as gallery)
- [x] PDF page slides (API 1.3 — add_slides pdf_document_id/pdf_pages; UI pdf picker + стр. 1 quick; `test_presentation_pdf_slides.py`)
- [x] delete presentation (UI 2.2 — `deletePresentation` list row + editor confirm; backend DELETE already wired)
- [x] index no_slides refusal (UI 1.3 — indexPresentation, pres-index, pres-refusal)
- [ ] index → list row (UI 1.4 — selenium / reconcile after index)
- [x] Progress panel from GET `/api/v1/progress` (UI 3.1 — four stats, topic nodes, weak list; vitest `progressView` + `progressBody`)

## Integration seam (chat slide citation)

- [x] `Source.slide` + piece index slide column (migration `0015`)
- [x] presentation index stores slide position + pdf_page as `page`
- [x] pytest `test_presentation_chat.py` (ready slide cite, draft bind refused, PDF page-only)
- [x] frontend `chatView` / `isSourceBody` — «Слайд N» without breaking PDF
- [x] quiz slide citation (Story 3 §2.2 — `Question.slide`, migration `0016`, `test_presentation_quiz`, quizView «Слайд N»)

## Human later

- [ ] Override or confirm AFK defaults D1–D5
- [ ] `/spec-skeptic 3 spec` if desired
- [ ] Merge `features/presentations` → `dev`
