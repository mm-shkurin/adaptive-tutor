---
name: backend-delivery
description: Провести историю через бэкендовый конвейер AdaptiveTutor — интервью, спека, тест-спека, реализация без red/green, тесты из test-spec, рефактор, учёт. Используется, когда начинают новую историю по бэкенду, спрашивают что делать дальше, или когда история дошла до слияния в dev.
---

# /backend-delivery

Конвейер одной истории для **бэкенд-полосы**. Общая рамка — `/delivery-loop`. Парная
полоса — `/frontend-delivery`. Точка встречи: `ProductSpecification/api-specs/`.

## Режим (без послойного TDD)

```
ветка ──► интервью ──► спека ──► тест-спека ──► реализация ──► тесты
                                                                 │
                          учёт ◄── рефактор ◄── коммит поведения ◄┘
                            │
                            └──► пуш ветки ──► пуш branch:dev
```

Кусок работы = Tier 1 сценарий (или небольшой связный набор). Не разворачивать
`red-usecase` → `green-adapter` цепочку из `/continue`, пока пользователь явно не
попросил полный TDD.

### 0. Ветка — от `dev`, одна на историю

```
git checkout -b features/<имя> dev
```

`dev` не выкатывать локально, если рядом фронтовая сессия на том же дереве.

### 1. Интервью — раз на историю

`/interview`. 3–4 вопроса пачкой. На выходе: scope in / out, `DECISION:` с основанием.

### 2. Спека — до реализации

`endpoints.md` в папке истории + YAML в `ProductSpecification/api-specs/`. Отход от YAML —
правка YAML в том же коммите.

### 3. Тест-спека — сценарии и тиры

`/test-spec`, затем тиринг:

- **Tier 1** — без чего история мёртва для пользователя (цель: узкий набор).
- **Tier 2** — строится после Tier 1, предпочтительно через `/harvest`.
- **Tier 3** — в `tests/tier3/`, **не строится**.

Если набор уже принят («не сокращать» в `progress.md`) — не выкидывать сценарии из файлов;
менять только **порядок доставки** (сначала Tier 1).

### 4. Реализация

Слои: `application → adapters → usecase → domain` (`CLAUDE.md`). Писать код под api-spec
сразу (usecase + adapters + HTTP), без отдельной red-фазы на слой.

Лимит размера / стиль — `.claude/guidelines/coding-detail.md` (читать перед правкой).

### 5. Тесты из test-spec

1. Написать/включить тесты по Tier 1 сценарию из `tests/*.md`.
2. Хотя бы раз увидеть **fail** (сломанный assert / выключенное поведение) — sanity.
3. Починить до зелёного.

Команды (`ProductSpecification/technology.md`):

```bash
cd backend && pytest
cd backend && pytest path/to/focused_test.py
pytest acceptance   # HTTP/browser acceptance, когда кусок чёрного ящика готов
```

### 6. Коммит поведения

Вместе с `progress.md`. Сообщение — **почему**. Только путями:

```
git commit -m "..." -- backend ProductSpecification
```

### 7. Рефактор — после зелёного, отдельным коммитом

`/refactor`. Прогон ещё раз → `refactor:` коммит. Нечего менять — одна строка почему.

### 8. Учёт

`progress.md`, строка в `stories.md`. Найденное вне scope →
`ProductSpecification/tasks/BACKLOG.md`.

### 9. Слияние

```
git push origin features/<имя>
git push origin features/<имя>:dev
git fetch origin dev:dev
```

Порядок пуша согласуется с фронтовой сессией.

## Гейты

| Гейт | Команда |
|---|---|
| Правила слоёв / 200 строк | `python scripts/check_repo_rules.py --scope back` |
| Контракт путей | `python scripts/check_api_contract.py` |
| Поведение | `bash scripts/ci-local.sh --backend` или `cd backend && pytest` |
| Acceptance | `pytest acceptance` |

Полный локальный круг перед пушем: `bash scripts/ci-local.sh`. CI: `.github/workflows/`.

## Стык с фронтом

Спека раньше обеих реализаций. Расхождение — в api-spec / карту контракта, не «починить
только у себя». После куска — `/clear-session`.
