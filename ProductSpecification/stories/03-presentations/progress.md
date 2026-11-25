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
- [x] account Tier 1 API scenarios done (1.1–1.2, 2.1, 3.1–3.2, 3.4, 4.1–4.4, 5.2, 6.1, 7.1 stub)

## Tier 1 — Frontend (after backend meeting point)

- [ ] door opens editor
- [ ] (more from test-spec)

## Human later

- [ ] Override or confirm AFK defaults D1–D5
- [ ] `/spec-skeptic 3 spec` if desired
- [ ] Merge `features/presentations` → `dev`
