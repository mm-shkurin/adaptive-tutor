# Coding Rules

Always-on architectural core. The DDD smell catalogue, code-style catalogue and
per-layer detail live in `.claude/guidelines/coding-detail.md` — read it before writing
or refactoring backend code. Frontend equivalents: `.claude/guidelines/frontend-rules.md`.
Test discipline: `.claude/guidelines/tdd-rules.md`. Recurring failure classes to review
against: `.claude/guidelines/hazard-catalogue/`.

## Deployment

- The backend runs as multiple instances (uvicorn workers plus an ARQ worker on the
  same image). Never store application state in-memory — module-level `dict`/`set`,
  mutable default arguments, singleton caches in closures, class-level mutable
  attributes. State that must be consistent across instances goes to Postgres or Redis.

## Layers

Clean Architecture under `backend/` (see `CLAUDE.md`):

```
application → adapters → usecase → domain
```

| Module | Role | May import |
|--------|------|------------|
| `domain` | entities, value objects, domain rules | nothing outer; no FastAPI/SQLAlchemy |
| `usecase` | application services, port interfaces | `domain` only |
| `adapters` | HTTP, storage, Redis, PDF, vector search | `usecase`, `domain` |
| `application` | entry point, wiring | all modules |

Dependency direction is enforced by `.claude/skills/sprint-check/probes/config.json`
(and `scripts/check_repo_rules.py`). Do not add new outer←inner violations.

## File Size

- **Hard limit: 200 lines per file.** After any creation or refactoring, verify with
  `wc -l`. Applies to every source file regardless of type. Exemptions: Alembic
  migrations under `backend/alembic/versions/`, and seed/data dumps that cannot be
  split without inventing a meaningless boundary.

## Comments

- Comments earn their place by preserving what the code cannot express: rationale,
  external constraints, contracts, safety hazards. Delete comments that narrate what the
  code already says.
- A retained rationale must affect a maintainer's present decision, must not be
  recoverable from names, types, tests or version control, and must state the
  irreducible fact briefly. Implementation history and migration stories belong in
  commit messages, not in source.
