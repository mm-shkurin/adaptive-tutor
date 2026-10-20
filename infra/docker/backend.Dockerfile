# Backend image. Build context is the repo root.
FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/domain domain
COPY backend/usecase usecase
COPY backend/adapters adapters
COPY backend/application application
COPY backend/alembic alembic
COPY backend/alembic.ini alembic.ini

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --retries=10 --start-period=30s \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)" || exit 1

# Migrations belong to the API process. A later worker can reuse the image
# without running them again by replacing this command.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn application.main:app --host 0.0.0.0 --port 8000"]
