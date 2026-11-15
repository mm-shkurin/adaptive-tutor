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

### 1.2 A vector run that fails leaves the document ready and the next open can finish (06_Integration_Tests.md)
- [x] tests (acceptance: timeout / 4xx / 5xx / malformed → not askable; повторный open после успеха → askable)
- [x] implementation (`GET /api/v1/chats/{id}` векторизует сохранённые куски; сбой эмбеддинга оставляет ready и notice; следующий open дописывает векторы без повторной записи кусков)
- [x] refactor (DocumentVectors в ports; GetChat короче лимита; отдельный рефактор-коммит не нужен)

## Tier 1 — Frontend

### 1.1 The chat screen shows the list, the thread, and the sources (02_UI_Tests.md)
- [x] tests (vitest chatView; acceptance Selenium)
- [x] implementation (экран чата по мокапу: список, лента, источники; цитата — страница, не слайд)
- [x] refactor (типы/файлы по одному понятию; отдельный коммит не нужен)

### 2.1 New chat opens an empty thread on the selected PDF (02_UI_Tests.md)
- [x] tests (acceptance Selenium)
- [x] implementation («Новый чат» создаёт пустую ленту на том же ready PDF)
- [x] refactor (вместе с экраном 1.1; отдельный коммит не нужен)

### 3.1 Send shows the whole tutor line with the page (02_UI_Tests.md)
- [x] tests (acceptance Selenium; sanity fail на «Слайд» → страница)
- [x] implementation (отправка целиком, model + страница на строке тьютора)
- [x] refactor (вместе с экраном 1.1; отдельный коммит не нужен)

## Next
- [ ] Tier 2 API 6.x остаток / `/harvest` (UI Tier 1 закрыт)
