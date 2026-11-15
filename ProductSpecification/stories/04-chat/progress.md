# Story 4: Чат — Progress

## Spec
- [x] interview
- [x] story
- [x] api-spec
- [x] test-spec

Набор принят: Tier 1 — 6, Tier 2 — 95, Tier 3 — 1. Не сокращать. Ветка `features/chat` от `features/document-ingestion`: на `dev` ещё нет готовых PDF, без них чат не к чему привязать.

## Tier 1 — Backend

### 2.1 A new chat binds the selected ready PDF and starts empty (01_API_Tests.md)
- [x] tests (acceptance: 404, затем 201)
- [x] implementation
- [x] refactor (новые типы уже по одному понятию, короче лимита; отдельный коммит не нужен)

## Next
- [ ] 4.1 A question is answered from this PDF with the model, the first page, and at most ten sources (01_API_Tests.md)
- [ ] 1.1 A newly indexed PDF is answered from its vectors and the stored starting page (06_Integration_Tests.md)
- [ ] UI 1.1 / 2.1 / 3.1 — фронтовая полоса
