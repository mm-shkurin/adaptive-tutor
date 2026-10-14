# AdaptiveTutor

AdaptiveTutor — агентная мультимодальная RAG-система для обучения. Система "читает" лекции, учебники, слайды, методички (включая формулы, таблицы, графики) и помогает студентам учиться через интерактивный диалог с AI-агентами.

## Monorepo Structure

```
adaptive-tutor/
├── backend/              # FastAPI backend (hexagonal architecture)
│   ├── domain/          # Business logic (agents, models, ports)
│   ├── application/     # Use cases (orchestration)
│   ├── infrastructure/  # Adapters (Qdrant, PostgreSQL, freellmapi, ClamAV)
│   └── api/             # FastAPI routes
├── frontend/            # React 19 frontend (Feature-Sliced)
│   ├── src/
│   │   ├── pages/      # Screens (Chat, Quiz, Progress, Documents)
│   │   ├── widgets/    # Reusable components
│   │   ├── features/   # Feature-level logic
│   │   └── shared/     # Shared utilities
│   └── package.json
├── ProductSpecification/ # Product context
│   ├── BriefProductDescription.md
│   ├── ExpectedLoad.md
│   ├── stories.md
│   ├── stories/        # Story-specific specs
│   └── api-specs/      # OpenAPI 3.0.3 specs
├── .claude/             # Claude Code configuration
│   ├── agents/         # Subagents (security-reviewer, e2e-runner)
│   ├── skills/         # Workflow skills (interview, api-spec, test-spec)
│   ├── rules/          # Always-follow guidelines (git, coding, workflow)
│   ├── hooks/          # Trigger-based automations (memory-persistence)
│   └── templates/      # TDD, refactoring, testing templates
├── scripts/            # Utility scripts (replica-diff, package-manager)
└── docker-compose.yml  # Infrastructure (Qdrant, PostgreSQL, ClamAV, freellmapi)
```

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Architecture**: Hexagonal (Domain → Use Cases → Adapters)
- **Database**: PostgreSQL 15+ (metadata)
- **Vector DB**: Qdrant (self-hosted via Docker)
- **LLM/Embeddings**: freellmapi (free tier, 7.4B tokens/month)
- **Virus Scanning**: ClamAV (Docker)
- **Task Queue**: FastAPI BackgroundTasks (MVP) / Celery (v2)
- **Testing**: pytest, pytest-asyncio

### Frontend
- **Framework**: React 19 + Vite
- **Architecture**: Feature-Sliced Design
- **State Management**: React Context / Zustand (v2)
- **Testing**: Vitest (unit), Playwright (E2E)
- **Styling**: Tailwind CSS / CSS Modules

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions (future)

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### 1. Clone repository
```bash
git clone https://github.com/mm-shkurin/adaptive-tutor.git
cd adaptive-tutor
```

### 2. Start infrastructure
```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Qdrant (port 6333)
- ClamAV (port 3310)
- freellmapi (port 3001)

### 3. Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn api.main:app --reload
```

### 4. Frontend setup
```bash
cd frontend
npm install
npm run dev
```

### 5. Run tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
npm run test:e2e
```

## Development Workflow

### Git Workflow (GitHub Flow)

**Branches:**
- `main` — Deploy branch (protected, no direct commits)
- `dev` — Integration branch (target for feature work)
- `features/<name>` — Feature branches (branched from `dev`)

**Flow:** `features/<name>` → `dev` → `main`

**Rules:**
- Branch off `dev`, never off `main`
- Feature branch names: `features/` + kebab-case (e.g., `features/document-ingestion`)
- Merge into `dev` via Pull Request (reviewed)
- Release: merge `dev` into `main` via Pull Request
- Rebase feature branches on `dev` before opening PR
- Delete feature branches after merge

### Commit Messages

Conventional Commits: `<type>: <short description in imperative mood>`

**Types:**
- `feat` — New feature
- `fix` — Bug fix
- `chore` — Tooling, deps, config
- `docs` — Documentation
- `refactor` — Code change (no bug/feature)
- `test` — Adding/fixing tests
- `perf` — Performance improvement
- `build` — Build system, Docker
- `ci` — CI configuration
- `style` — Formatting only

**Examples:**
- `feat(documents): add PDF upload endpoint`
- `fix(qdrant): handle connection timeout`
- `refactor(chat): extract message validation`

### Story Workflow

Each feature goes through:

1. **`/interview`** — Gather story context (scope, decisions, constraints)
2. **`/api-spec`** — Generate OpenAPI specifications
3. **`/test-spec`** — Generate BDD test specifications (6 categories)
4. **Implementation** — Backend + frontend (parallel sessions)
5. **Tests** — Unit + integration + E2E
6. **Review** — Code review against spec
7. **Merge** — Into `dev`

**Read first:** `.claude/skills/delivery-loop/SKILL.md`

### Coding Rules

- **Layer cap:** 200 lines per file
- **Dependency direction:** Domain ← Application ← Infrastructure
- **No inter-layer imports:** Infrastructure cannot import Domain
- **TDD discipline:** Red → Green → Refactor
- **Coverage:** 80%+ for backend, 70%+ for frontend

**Read:** `.claude/rules/coding-rules.md`

## Claude Code Skills

This project uses Claude Code with custom skills from absolute555 and WorldFlowAI:

**Skills:**
- `interview` — Story context gathering
- `api-spec` — OpenAPI specification generation
- `test-spec` — BDD test specification (6 categories)
- `backend-delivery` — Backend implementation pipeline
- `frontend-delivery` — Frontend implementation pipeline
- `verification-loop` — Continuous quality checks

**Agents:**
- `security-reviewer` — Security vulnerability analysis
- `e2e-runner` — Playwright E2E test generation

**Hooks:**
- `memory-persistence` — Session context saving/loading

**Read:** `.claude/CLAUDE.md`

## MVP Stories

| # | Story | Status |
|---|-------|--------|
| 1 | Document ingestion | TODO |
| 2 | Chat agent core | TODO |
| 3 | Quiz generation | TODO |
| 4 | Knowledge Tracer basic | TODO |
| 5 | UI dashboard | TODO |
| 6 | Citation rendering | TODO |
| 7 | Learning modes | TODO |

**Read:** `ProductSpecification/stories.md`

## Product Context

- **Brief description:** `ProductSpecification/BriefProductDescription.md`
- **Expected load:** `ProductSpecification/ExpectedLoad.md`
- **Story mapping:** `ProductSpecification/stories.md`

## Contributing

1. Read `.claude/rules/git.md` before any branch or commit
2. Read `.claude/rules/coding-rules.md` before writing code
3. Follow Conventional Commits for commit messages
4. All changes must pass tests (pytest + Vitest + Playwright)
5. Open Pull Request against `dev` branch
6. Request review before merge

## License

MIT License — see LICENSE file

## Author

Maxim Shkurin — [GitHub](https://github.com/mm-shkurin)
