# Technology Profile

tech-profile:
  backend: python-fastapi
  frontend: react-js
  css: plain-css
  browser-testing: selenium

## Backend

| Concern | Technology |
|---------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Persistence | PostgreSQL |
| Migrations | Alembic |
| Vectors | Qdrant |
| Embeddings | TEI (`all-MiniLM-L6-v2`, OpenAI `/v1/embeddings`) via `FREE_LLM_API_URL` |
| Chat models | freellmapi OpenAI `/v1/chat/completions` via `FREE_LLM_CHAT_URL` → `HttpTutor` |

## Frontend

| Concern | Technology |
|---------|-----------|
| Language | JavaScript |
| Framework | React |
| Build tool | Vite |
| Test runner | Vitest |

## CSS

| Concern | Technology |
|---------|-----------|
| Framework | Plain CSS |
| Source of layout | `adaptive-tutor-mockup.html` |

## Browser Testing

| Concern | Technology |
|---------|-----------|
| Framework | Selenium WebDriver |

## Testing (Backend)

| Concern | Technology |
|---------|-----------|
| Unit/integration | pytest |
| Coverage | coverage.py |

## Conventions

### Backend

| Concern | Convention |
|---------|-----------|
| Test disable marker | @pytest.mark.skip(reason="RED: ...") |
| Not-implemented marker | raise NotImplementedError() |
| Run command | uvicorn application.main:app --reload |
| Test command | pytest |
| Acceptance test command | pytest acceptance |
| Coverage report | coverage.xml |

### Frontend

| Concern | Convention |
|---------|-----------|
| Test skip marker | it.skip |
| Dev command | npm run dev |
| Test command | npm test |

### Browser Testing

| Concern | Convention |
|---------|-----------|
| Acceptance test command | pytest acceptance |
