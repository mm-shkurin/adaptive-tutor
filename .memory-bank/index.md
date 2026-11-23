# Memory Bank — AdaptiveTutor

## Overview

AdaptiveTutor учит по загруженным лекциям: индексирует PDF и презентации, отвечает в чате с цитатой на страницу или слайд, собирает викторины и показывает, какие темы слабые. Основной пользователь — студент. Преподаватель загружает материалы.

## Where to resume

1. `ProductSpecification/stories.md` — истории 1–2 в Done. Очередь: 4 Чат (интервью), 7 Викторины, 3 Презентации, 8 Прогресс. Истории 5 и 6 входят в 4.
2. Режим доставки по умолчанию: `/delivery-loop` → `/backend-delivery` или `/frontend-delivery` (код → тесты из test-spec → refactor). Полный red/green `/continue` — только по явной просьбе.
3. История 2 закрыта: PDF intake/index, куски в Postgres, live embeddings через TEI (`infra` service `embeddings`, `all-MiniLM-L6-v2`, dim 384, `--auto-truncate`). `FREE_LLM_API_URL=http://embeddings:80/v1`. Freellmapi не для embed. Порядок сдачи: **4 Чат → 7 Викторины → 3 Презентации → 8 Прогресс**.
4. История 4: Tier 1+Tier 2 сданы; harvest закрыт. Live `HttpTutor` + `FREE_LLM_CHAT_URL`. Следующий кусок — **Task 3** chat language/narrow layout (`tasks/3-bug-chat-language-and-narrow-layout`). AFK: `/delivery-loop afk`. Merge в `dev` — после Task 3, вручную. Затем история 7.
5. `ProductSpecification/stories/01-sign-in-profile/progress.md` — закрыта; браузерная проверка против стека пройдена 2026-11-07.
6. Мокап целиком: `adaptive-tutor-mockup.html`.
7. Локальный стек: Postgres/Redis/Qdrant/TEI в `infra/`, БД `adaptive_tutor_local`, backend `:8010`, Vite `:5174`. HttpEmbeddings/HttpQdrant timeout 60s (реальные PDF ~100+ кусков иначе `search store refused`).

Спеки API и тестов — по одной истории после интервью. Не выдумывать ответы интервью.

## Structure

- [Стек](tech-details/stack.md)
- [Истории](tasks/stories.md)
- [Как работать](steerings/development-conventions.md)

## CI

- Workflows: `.github/workflows/` (`rules`, `backend`, `frontend`, `audit`)
- Local: `bash scripts/ci-local.sh`
- Gates: `scripts/check_repo_rules.py`, `check_api_contract.py`, `check_contract_types.py`
- Not ported yet: `stack` (full compose e2e), `release` (GHCR deploy)
