# Backend

FastAPI backend with hexagonal architecture.

## Structure
- `domain/` — Business logic (agents, models, ports)
- `application/` — Use cases (orchestration)
- `infrastructure/` — Adapters (Qdrant, PostgreSQL, freellmapi, ClamAV)
- `api/` — FastAPI routes

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn api.main:app --reload
```

## Test
```bash
pytest
```
