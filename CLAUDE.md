# CLAUDE.md

TDD Framework — Clean Architecture backend + frontend + acceptance tests.

Technology stack and commands are declared in `ProductSpecification/technology.md`. Read that file for build commands, test commands, and framework-specific conventions.

## Architecture

```
application → adapters → usecase → domain
```

All backend modules live under `backend/`. Never place them in the project root.

| Module | Description | Dependencies |
|--------|-------------|--------------|
| `backend/domain` | Entities, value objects, exceptions | None |
| `backend/usecase` | Application services, port interfaces | domain |
| `backend/adapters` | HTTP, storage, vector search, external models | usecase |
| `backend/application` | Entry point, wiring | all modules |
| `acceptance` | Black-box tests (HTTP + browser) | None |

Dependency flow is strictly inward. Never import from outer layers in inner layers.

## On-Demand Guidelines

The always-on rules (`.claude/rules/*.md`) hold only the high-level map, invariants, and safety guardrails. The per-topic detail is deferred to `.claude/guidelines/` and is **not** auto-loaded — read the matching file **before** doing that kind of work.

| When you are about to… | Read first |
|------------------------|-----------|
| Write or refactor backend code (any layer) | `.claude/guidelines/coding-detail.md` |
| Write or refactor frontend code or browser tests | `.claude/guidelines/frontend-rules.md` |
| Write or run TDD tests | `.claude/guidelines/tdd-rules.md` |
| Execute a scenario or task work unit | `.claude/guidelines/workflow-detail.md` |
| Understand the commit-time review passes | `.claude/guidelines/review-passes-detail.md` |
| Start/stop services or run load tests | `.claude/guidelines/infrastructure-detail.md` |
| Edit prompt-library docs | `.claude/guidelines/prompt-rules.md` |
| Load a technology binding | `.claude/guidelines/technology-loading.md` |
| Emit sub-agent progress to the live log | `.claude/guidelines/agent-logging.md` |

## Session memory

State of a story lives in `ProductSpecification/stories/*/progress.md`. Why a decision was made lives in that story's journey summary, written only by `/handoff`. The project encyclopedia is `.memory-bank/index.md`. A new session reads these before asking the user to restate the plan.

## Git

Commits land on the working branch. This project does not use pull requests. See `.claude/rules/workflow.md`.
