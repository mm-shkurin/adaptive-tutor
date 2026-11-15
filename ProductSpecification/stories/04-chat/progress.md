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

## Harvest — Tier 1 → Tier 2

- [ ] harvest (полный батч Tier 2 ещё не гоняли; ниже — точечная сдача API 6.x)

## Tier 2 — Backend (01_API_Tests.md §6)

### 6.1 Opening a ready PDF with no vectors makes it askable from the stored text
- [S] covered by Integration 1.2 success reopen + GetChat.open vectorize path

### 6.2 A failed vector run leaves the document ready and the chat not askable
- [S] covered by Integration 1.2 (`test_a_vector_run_that_fails_leaves_the_document_ready`)

### 6.3 The next open after a failed vector run tries again
- [S] covered by Integration 1.2 retry half

### 6.4 A vector run that stops midway does not store those pieces twice
- [ ] tests
- [ ] implementation

### 6.5 Opening a PDF that already has vectors does not write them again
- [x] tests (acceptance; sanity fail by disabling GetChat ready short-circuit)
- [x] implementation (already in GetChat.open early `ready`; upsert counter on fake)
- [S] refactor (no new prod behavior; acceptance-only)

### 6.6 A failed reply keeps one person line for that attempt
- [x] tests (acceptance; sanity fail on reply_failed message)
- [x] implementation (ReplyFailed → person-only + error; Idempotency-Key replay)
- [x] refactor (ReplyError; HTTP locals; Postgres get→_owned)

### 6.7 A new attempt after a failed reply is kept
- [x] tests (acceptance)
- [x] implementation (new key appends another person line)
- [x] refactor (same pass as 6.6)

### 6.8–6.11
- [ ] latency budget / pin / interleaved opens / empty-document vector write

## Next
- [ ] Tier 2 API 6.4, then 6.8–6.11; полный `/harvest` остальных Tier 2
