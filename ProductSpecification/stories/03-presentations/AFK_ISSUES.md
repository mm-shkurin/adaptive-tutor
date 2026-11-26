# AFK issues — Story 3 Презентации

Session: `/delivery-loop afk` 2026-11-25 ~21:58, budget **110 min**.
Branch: `features/presentations` (from `origin/dev`).
User said «story 3 викторины» — treated as **story 3 Presentations** (queue); story 7 Quizzes already Done.

Questions are **not** asked in chat. Defaults below are in force until a human overrides.

---

## AFK defaults (interview gaps)

| # | Open item | AFK default | Why |
|---|-----------|-------------|-----|
| D1 | Delete presentation: chats + quiz attempts? | **Hard-delete the presentation material, vectors, and pieces.** Chats and quiz attempts that pointed at it stay, but open/create against that id is refused as absent (`document_not_found` / quiz document missing). Card/list that needs the title shows a tombstone label «Источник удалён» when the join fails. | Matches «удаление одной» without cascading wipe of learning history; same absent-shape as foreign id. |
| D2 | Graph edges between topics | **No edges in v1 of this story.** Nodes only (topic + mastery color). Edges out of scope until a later decision names a rule (co-occurrence / shared material). Mockup lines are decorative until then. | Interview left edges unset; inventing a graph model blocks delivery. |
| D3 | Weak-topic counter vs list (mockup shows 45% and 52%) | **Counter = count of topics with mastery &lt; 40%.** The weak list under the graph shows only those (&lt;40%). Medium (40–69%) stay on the graph in amber but are not in the weak list / counter. | Aligns counter with the «слабо» color band already decided. |
| D4 | What is a «session this week»? | **One session = one calendar day with ≥1 chat message sent or ≥1 quiz attempt finished**, counted in the last 7 local midnights of the owner. Max one per day → «сессий за неделю» ≤ 7. | Simple, auditable; avoids counting every message as a session. |
| D5 | Virus scan for photo / PPTX / DOCX | **Same virus gate as PDF** before bytes are kept for indexing. Timeout / unreadable → refuse that add (slide or office import), no row for that payload. | Interview noted PDF already has it; reuse avoids a second security story. |

## Absorbed story 8

Progress screen («Ваш прогресс») is **in story 3**. Remove story 8 as a separate backlog delivery when this interview+defaults are accepted by a human poke. AFK already updates `stories.md` accordingly.

## Parking lot (do not block AFK)

| # | Item | Notes |
|---|------|-------|
| P1 | Dirty WIP stashed from `features/quizzes` as `afk-wip-quizzes-before-story3` | Restore on quizzes branch only if still needed; origin/dev already has quiz harden tip. |
| P2 | Spec-skeptic `block` / second `revise` | Fold safe findings; leave remainder here — do not wait in AFK. |
| P3 | Live OCR / Tesseract / real camera | Tests use fakes; **production still wires `FakeOcr`** until live Tesseract lands — human poke for real OCR. |
| P7 | Postgres presentation store | Migration `0014_presentation_store_support` + `PostgresPresentationStore` wired in `context_build.py`; requires `alembic upgrade head` before presentations persist in prod. |
| P8 | Progress chat sessions in Postgres | **Done 2026-11-26** — `chat_lines.created_at` (migration `0018`) + `PostgresChatStore.person_send_times`. Run `alembic upgrade head` before poke. |
| P4 | Formula LLM live HTTP | Path + FakeAssist tests land 2026-11-26; prod still `NoopFormulaAssist` — wire FREE_LLM_CHAT_URL enricher + prompt quality poke. |
| P5 | Mockups HTML screenshots / align-design | Frontend strip; after api-spec exists. |
| P6 | Merging `features/presentations` → `dev` | Human order; AFK only `git push -u origin HEAD`. |
| P9 | PDF-page slides index without PyMuPDF text yet | Add path stores metadata; index/OCR may leave those slides empty until text extract lands. |
| P10 | PPTX/DOCX import | **Done this AFK** — `PythonOfficeParser`, multipart `file`, virus gate, 40-slide cap, editor picker; tests use `FakeOfficeParser`. |
| P11 | Formal hazard-scan + tiering-agent + spec-skeptic | Parked; Notes fold + provisional Tier markers only. |
| P12 | Selenium for presentations / progress | Not run this AFK. |
| P13 | Live OCR (Tesseract) in production | Still FakeOcr in context_build. |
| P14 | Postgres chat `person_send_times` empty | Closed by P8 / `0018`. |
| P15 | Run `alembic upgrade head` (0013–0018) | Required before poke against local/prod DB. |

## Session log

| Time | Event |
|------|-------|
| 21:58 | Start AFK 110m; stash quizzes WIP; branch `features/presentations` from `origin/dev` |
| 22:00 | AFK defaults D1–D5; story + api-spec + test-spec; story 8 absorbed into 3 |
| 22:30 | Tier-1 backend slice green (20); later split to guards/flow tests; bodyGuards kind+draft |
| 22:15 | Behavior commit + continue frontend door if budget |
| 22:47 | AFK soft stop (~49m of 110m). PPTX/DOCX landed. Remaining: live OCR, Selenium, alembic upgrade, merge, formal hazard/tiering/skeptic |
| 22:20 | Tier-1 frontend UI 1.1: presentation door → POST draft → editor (title 80, 0 slides) |
| 22:18 | Tier-1 frontend UI 1.2–1.3: gallery addSlides, slide cards, index no_slides → pres-refusal |
| ~22:45 | Integration §2.1/§2.3: chat `Source.slide`, piece index + Qdrant payload, `test_presentation_chat`, chatView «Слайд N» |
| ~23:30 | Integration §2.2: quiz `Question.slide` + `0016`, `test_presentation_quiz`, `quizView` / `quiz-cite-slide` |
| 2026-11-25 | Progress API real read: `GetProgress` + `test_progress.py`; `0017_quiz_finished_at`; P8 parked for prod chat session days |
| 2026-11-25 | Progress frontend: `/progress` → `ProgressPage` + `GET /api/v1/progress`; UI 3.1 stats/nodes/weak; vitest guards + view |
| 2026-11-25 | Chunk A+B: PDF page add (API 1.3 + editor picker), delete presentation UI 2.2, camera `capture=environment`; PPTX/DOCX still out |
