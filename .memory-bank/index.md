# Memory Bank — AdaptiveTutor

## Overview

AdaptiveTutor учит по загруженным лекциям: индексирует PDF и презентации, отвечает в чате с цитатой на страницу или слайд, собирает викторины и показывает, какие темы слабые. Основной пользователь — студент. Преподаватель загружает материалы.

## Where to resume

1. `ProductSpecification/stories.md` — история 1 в Done; история 2 в Progress; 3–8 в Backlog без спеки.
2. Режим доставки по умолчанию: `/delivery-loop` → `/backend-delivery` или `/frontend-delivery` (код → тесты из test-spec → refactor). Полный red/green `/continue` — только по явной просьбе.
3. `ProductSpecification/stories/02-document-ingestion/progress.md` — Tier 1 и harvest закрыты; фронт Tier 2 закрыт; 2.4 grapheme name закрыт; следующий кусок бэкенда: **4.2 A failed index names the part and leaves nothing searchable**.
4. `ProductSpecification/stories/01-sign-in-profile/progress.md` — закрыта; браузерная проверка против стека пройдена 2026-11-07.
5. Мокап целиком: `adaptive-tutor-mockup.html`.
6. Локальный стек для проверки: Postgres/Redis в `infra/`, чистая БД `adaptive_tutor_local` (старая `adaptive_tutor` загрязнена `0005_shop_cart`), API fake-OAuth `:8010`, Vite `:5174` (`:8000`/`:5173` заняты чужими проектами).

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
