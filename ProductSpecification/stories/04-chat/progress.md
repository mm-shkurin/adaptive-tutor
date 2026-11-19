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

- [ ] harvest (полный батч Tier 2 ещё не гоняли; ниже — точечная сдача)

## Tier 2 — Backend (01_API_Tests.md §1–3 gates)

### 1.1 A call with no session is refused like a missing chat
- [x] tests (acceptance; sanity fail on 401 vs 404)
- [S] implementation (chats._caller Unauthorized → ChatNotFound)
- [S] refactor (no new prod code)

### 1.2 A document that is not ready cannot be bound
- [x] tests (acceptance; waiting/indexing/failed/unknown × start/open)
- [S] implementation (Chat.bound_to → DocumentNotReady)
- [S] refactor (no new prod code)

### 1.3 A person with no ready PDF cannot start a chat
- [x] tests (acceptance; already green)
- [S] implementation (CreateChat._newest_ready → NoReadyDocument)
- [S] refactor (no new prod code)

### 2.2 A new chat with nothing selected binds the newest ready PDF
- [x] tests (acceptance; already green)
- [S] implementation (CreateChat without document_id)
- [S] refactor (no new prod code)

### 3.1 A blank line is refused and nothing is stored
- [x] tests (acceptance; already green)
- [S] implementation (EmptyQuestion before save)
- [S] refactor (no new prod code)

### 3.2 An unknown or null model or mode is refused and nothing is stored
- [x] tests (acceptance; already green)
- [S] implementation (ListedModel/LearningMode.parse)
- [S] refactor (no new prod code)

### 3.3 A send before the material can be asked stores nothing
- [x] tests (acceptance; already green)
- [S] implementation (SendMessage._askable → NotAskable)
- [S] refactor (no new prod code)

## Tier 2 — Backend (01_API_Tests.md §4 reply)

### 4.2 Nothing in the material stores that sentence and no sources
- [x] tests (acceptance; sanity fail on model null)
- [S] implementation (Chat.record_missing / Line.missing)
- [S] refactor (no new prod code)

### 4.6 The same attempt stores one person line and one tutor line
- [x] tests (acceptance; already green)
- [S] implementation (ChatStore find_attempt / save_attempt)
- [S] refactor (no new prod code)

### 4.7 An omitted model is auto and an omitted mode is Professor
- [x] tests (acceptance; already green)
- [S] implementation (ListedModel/LearningMode omitted defaults)
- [S] refactor (no new prod code)

## Tier 2 — Backend (05_Security_Tests.md)

### 1.1 Another person's chat or document is refused like a missing chat
- [x] tests (acceptance; sanity fail on 403 vs 404)
- [S] implementation (owner-scoped get/create → ChatNotFound)
- [S] refactor (no new prod code)

### 2.1 A script and a SQL fragment round-trip as the person's own text
- [x] tests (acceptance; already green)
- [S] implementation (text stored/returned verbatim)
- [S] refactor (no new prod code)

### 3.1 Server-owned fields on a send are ignored
- [x] tests (acceptance; already green)
- [S] implementation (Outgoing.from_payload ignores extras)
- [S] refactor (no new prod code)

### 3.2 Server-owned fields on a new chat and on a switch are ignored
- [x] tests (acceptance; sanity fail on injected id == server id)
- [S] implementation (CreateChatBody/OpenChatBody extra="ignore")
- [S] refactor (no new prod code)

## Tier 2 — Backend (01_API_Tests.md §4 reply cont.)

### 4.3 A piece with no page is still answered and the source has no page
- [x] tests (acceptance; already green)
- [S] implementation (Source.page Optional; Line.grounded uses sources[0].page)
- [S] refactor (no new prod code)

### 4.4 The list shows this person's document name and last line, newest first
- [x] tests (acceptance; already green)
- [S] implementation (ListChats + Chat.preview + owner-scoped list_for)
- [S] refactor (no new prod code)

### 4.5 A multibyte line and a multibyte piece round-trip unchanged
- [x] tests (acceptance; already green)
- [S] implementation (text stored/returned verbatim)
- [S] refactor (no new prod code)

## Tier 2 — Backend (01_API_Tests.md §5 modes start)

### 5.1 Five-year-old answers in plain words with a page
- [x] tests (acceptance; already green)
- [S] implementation (five_year_old in GROUNDED_MODES; scripted tutor)
- [S] refactor (no new prod code)

## Tier 2 — Backend (01_API_Tests.md §6)

### 6.1 Opening a ready PDF with no vectors makes it askable from the stored text
- [S] covered by Integration 1.2 success reopen + GetChat.open vectorize path

### 6.2 A failed vector run leaves the document ready and the chat not askable
- [S] covered by Integration 1.2 (`test_a_vector_run_that_fails_leaves_the_document_ready`)

### 6.3 The next open after a failed vector run tries again
- [S] covered by Integration 1.2 retry half

### 6.4 A vector run that stops midway does not store those pieces twice
- [x] tests (acceptance; sanity fail on upsert count including indexing writes)
- [x] implementation (per-piece embed+upsert, skip present ordinals, ready=count==expected, last failed ordinal)
- [S] refactor (write/ready already one concept each; files under limit; no separate commit)

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

### 6.8 A reply that misses the latency budget keeps one person line and no tutor line
- [x] tests (acceptance; hang tutor cancelled by wait_for)
- [x] implementation (SendMessage clock + CHAT_LATENCY 5s; acceptance 50ms)
- [S] refactor (budget helpers already separate; no separate commit)

### 6.9 The latency budget is pinned just before, at, and just after expiry
- [x] tests (acceptance; clock advance on match)
- [x] implementation (expire check before/after tutor)
- [S] refactor (with 6.8)

### 6.10 Two opens interleaved do not store a piece twice
- [x] tests (acceptance; in-process gather + latch; ThreadPool hung the loop)
- [x] implementation (latch after ordinals read; write lock; deterministic point ids)
- [S] refactor (no separate commit)

### 6.11 A vector write with no document leaves every neighbour untouched
- [x] tests (acceptance)
- [x] implementation (empty pieces short-circuit already; probe exercises it)
- [S] refactor (no separate commit)

### 7.1 Switching document keeps the previous chat and opens the chosen PDF
- [x] tests (acceptance; sanity fail on open status)
- [x] implementation (POST /api/v1/chats/open + OpenChat + ChatStore.newest_for_document)
- [S] refactor (OpenChat already one concept; files under limit; no separate commit)

### 7.2 A reply to the chat just left stays on that chat
- [x] tests (acceptance; hold+switch probe; sanity fail on opened gaining SCRIPT)
- [S] implementation (SendMessage already binds reply to request chat_id)
- [S] refactor (no new prod code)

## Tier 2 — Backend (01_API_Tests.md §4 concurrent + list order)

### 4.8 Two different attempts in flight both remain in the thread
- [x] tests (acceptance; thread latch + interleave-sends; sanity fail on line count)
- [x] implementation (thread interleave on get; commit_attempt appends under write lock)
- [x] refactor (Postgres append_attempt extracted under 200-line limit)

### 4.9 The same attempt interleaved stores one person line
- [x] tests (acceptance; attempt latch; model once)
- [x] implementation (with_attempt lock before tutor; commit_attempt idempotent)
- [x] refactor (with 4.8)

### 4.10 Two chats created at the same instant keep their order
- [x] tests (acceptance; already green)
- [S] implementation (list_for order created_at desc, id desc)
- [S] refactor (no new prod code)

### 4.11 A long chat list is read a constant number of times
- [x] tests (acceptance; sanity fail on reads == 0)
- [S] implementation (ListChats → one list_for; CountingChatStore probe)
- [S] refactor (no new prod code)

## Tier 2 — Backend (01_API_Tests.md §1 gates cont.)

### 1.4 A session store failure is refused like a missing chat
- [x] tests (acceptance; sanity fail on 503 vs 404)
- [x] implementation (chats._caller AccountStoreUnavailable → ChatNotFound)
- [S] refactor (one-line mapping; no extract)

## Tier 2 — Backend (01_API_Tests.md §5 modes + §3.6)

### 5.2 Socratic stores a question and no page
- [x] tests (acceptance; sanity fail on kind reply vs withheld)
- [x] implementation (LearningMode socratic path; Line.withheld; record_withheld)
- [S] refactor (send_message under limit; domain methods on Chat)

### 3.6 Asking to be told when nothing is withheld is refused
- [x] tests (acceptance)
- [x] implementation (tell → TellUnavailable when not withholding)
- [S] refactor (with 5.2)

### 5.3 A try after a withheld question answers with a page
- [x] tests (acceptance; try + phrase-that-asks-to-be-told)
- [x] implementation (is_withholding → record_release with person line)
- [S] refactor (with 5.2)

### 5.4 The tell control answers with a page and stores no person line
- [x] tests (acceptance)
- [x] implementation (Outgoing.tell; release without person line)
- [S] refactor (with 5.2)

### 5.5 Examiner posts the first question with four choices and no page
- [x] tests (acceptance; sanity fail on choices length 3)
- [x] implementation (examiner start; draft_choices; Line.question; migration 0011)
- [x] refactor (examiner_start extracted; send_message under 200)

## Tier 2 — Backend (01_API_Tests.md §3.4 + §5.6–5.17 examiner grades)

### 3.4 An invalid examiner answer is refused
- [x] tests (acceptance; sanity fail on correct=True→False)
- [x] implementation (ChoiceRequired/ChoiceUnknown; open question blocks text)
- [ ] refactor

### 5.6 Continuing the examiner series with the supported choice
- [x] tests (acceptance)
- [x] implementation (grade + next question when count < 3)
- [ ] refactor

### 5.7 Grading the third examiner question
- [x] tests (acceptance)
- [x] implementation (wrong grade; no fourth question)
- [ ] refactor

### 5.8 A second answer to the same question does not grade again
- [x] tests (acceptance)
- [x] implementation (Attempt.persist=False returns prior grade)
- [ ] refactor

### 5.10 After the third grade the next line is academic and is not a quiz
- [x] tests (acceptance)
- [x] implementation (stopped series → grounded professor)
- [ ] refactor

### 5.15 Choosing Examiner while a question is open does not post another
- [x] tests (acceptance)
- [x] implementation (empty attempt while open)
- [ ] refactor

### 5.17 A stopped examiner series ignores a new series, a choice, and tell
- [x] tests (acceptance)
- [x] implementation (no-op examiner/choice/tell when stopped)
- [ ] refactor

## Next
- [ ] refactor examiner grade chunk (mode_statements split; domain polish)
- [ ] полный `/harvest` остальных Tier 2 (5.11–5.14 interleave; UI/Load/Infra)
- [ ] 5.11–5.14 need interleave probes — not acceptance-only smoke
