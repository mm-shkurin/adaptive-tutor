.PHONY: up down build logs ps restart migrate shell psql smoke

up:
	docker compose up -d --build

build:
	docker compose build

down:
	docker compose down

ps:
	docker compose ps

logs:
	docker compose logs -f --tail=100

restart:
	docker compose restart backend gateway

migrate:
	docker compose exec backend alembic upgrade head

shell:
	docker compose exec backend sh

psql:
	docker compose exec postgres psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}

smoke:
	docker compose config -q
	curl -fsS http://127.0.0.1:$${BACKEND_HOST_PORT}/health
