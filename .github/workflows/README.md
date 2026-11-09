# CI — AdaptiveTutor

Прогоны перенесены из absolute555 и урезаны под текущий стек (Postgres, Redis, Clean Architecture, Selenium acceptance локально).

| Прогон | Когда | Что проверяет |
|---|---|---|
| `rules` | каждый пуш / PR | лимит 200 строк, направление слоёв, секреты (gitleaks), пути фронта ↔ api-specs |
| `backend` | пуш с правкой `backend/**` | alembic up/down, pytest + coverage, сборка Docker-образа |
| `frontend` | пуш с правкой `frontend/**` | `npm test`, `npm run build` |
| `audit` | понедельник / вручную | pip-audit, npm audit (high+) |

Пока **нет** (есть в absolute555 — следующий шаг): `stack` (полный compose + e2e), `release` (GHCR + deploy).

## Локально

```bash
bash scripts/ci-local.sh              # rules + backend + frontend
bash scripts/ci-local.sh --fast       # только pytest на одноразовом Postgres/Redis
bash scripts/ci-local.sh --rules      # только гейты исходников
bash scripts/ci-local.sh --backend
bash scripts/ci-local.sh --frontend
```

Храповики: известные нарушения в `scripts/*-baseline.json`. После починки:

```bash
python scripts/check_repo_rules.py --update-baseline
python scripts/check_api_contract.py --update-baseline
python scripts/check_contract_types.py --update-baseline
```

## Ветки

Прогоны слушают `dev`, `main`, `features/**`. `cancel-in-progress` оставляет один прогон на ветку — последний.
