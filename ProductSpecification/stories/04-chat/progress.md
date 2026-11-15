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

### 4.1 A question is answered from this PDF with the model, the first page, and at most ten sources (01_API_Tests.md)
- [x] tests (acceptance: посев поиска 404, затем 200)
- [x] implementation (ответ профессора по кускам этого PDF, не больше 10; страница — старт первого. Сократический и Экзаменатор пока `invalid_mode`. `Idempotency-Key` обязателен, повтор попытки — сценарий 4.6. Боевой поиск пуст, пока нет векторов из 1.1, поэтому отправка без них — 409)
- [x] refactor (типы уже по одному понятию, файлы короче лимита; правок нет, отдельный рефактор-коммит не нужен)

### 1.1 A newly indexed PDF is answered from its vectors and the stored starting page (06_Integration_Tests.md)
- [x] tests (acceptance: без записи векторов тело пустое, затем 384 и страница куска)
- [x] implementation (индексация пишет страницу куска и 384-вектор all-MiniLM-L6-v2 в фейк Qdrant до удаления файла; ответ берёт только куски этого PDF)
- [x] refactor (типы по одному понятию, файлы короче лимита; правок нет, отдельный рефактор кода не нужен)

## Next
- [ ] 1.2 A vector run that fails leaves the document ready and the next open can finish (06_Integration_Tests.md)
- [ ] UI 1.1 / 2.1 / 3.1 — фронтовая полоса
