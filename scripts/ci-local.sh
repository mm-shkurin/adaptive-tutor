#!/usr/bin/env bash
# Локальный прогон того же, что делает CI (.github/workflows/{rules,backend,frontend}.yml).
# Одна команда перед пушем: bash scripts/ci-local.sh
#
# Postgres и Redis поднимаются одноразовыми контейнерами — не трогают рабочий compose.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_BACKEND=1
RUN_FRONTEND=1
RUN_RULES=1
FAST=0
SUITE=""
PG_PORT="${PG_PORT:-55432}"
REDIS_PORT="${REDIS_PORT:-56379}"
STACK="$$"
PG_CONTAINER="adaptive-tutor-ci-pg-$STACK"
REDIS_CONTAINER="adaptive-tutor-ci-redis-$STACK"
CI_NETWORK="adaptive-tutor-ci-net-$STACK"
FAILED=()
RESULTS=()
STARTED_AT=$SECONDS

for arg in "$@"; do
  case "$arg" in
    --backend)  RUN_FRONTEND=0 ;;
    --frontend) RUN_BACKEND=0; RUN_RULES=0 ;;
    --rules)    RUN_BACKEND=0; RUN_FRONTEND=0 ;;
    --fast)     FAST=1; RUN_FRONTEND=0; RUN_RULES=0 ;;
    tests/*|usecase/*|adapters/*) SUITE="$SUITE $arg" ;;
    -h|--help)
      echo "usage: bash scripts/ci-local.sh [--backend|--frontend|--rules] [--fast] [tests/...]"
      echo ""
      echo "  --fast   только pytest против одноразового Postgres/Redis (без rules/frontend)"
      echo "  --rules  только check_repo_rules / api contract"
      exit 0 ;;
    *) echo "неизвестный аргумент: $arg" >&2; exit 2 ;;
  esac
done

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_OK=$'\033[32m'; C_FAIL=$'\033[31m'; C_STEP=$'\033[1;36m'; C_OFF=$'\033[0m'
else
  C_OK=""; C_FAIL=""; C_STEP=""; C_OFF=""
fi

step() {
  local name="$1"; shift
  local started=$SECONDS
  echo ""
  echo "${C_STEP}${name}${C_OFF}"
  if "$@"; then
    echo "${C_OK}ok${C_OFF}  ${name}"
    RESULTS+=("ok|$((SECONDS - started))|$name")
  else
    echo "${C_FAIL}fail${C_OFF}  ${name}"
    RESULTS+=("fail|$((SECONDS - started))|$name")
    FAILED+=("$name")
  fi
}

to_docker_path() {
  if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s' "$1"; fi
}

docker_run() {
  MSYS_NO_PATHCONV=1 docker "$@"
}

cleanup() {
  if [ "$FAST" = 1 ]; then
    if [ -n "${ENV_BACKUP:-}" ] && [ -f "$ENV_BACKUP" ]; then
      mv -f "$ENV_BACKUP" "$ROOT/backend/.env"
    fi
    return 0
  fi
  if [ -n "${PG_STARTED:-}" ]; then
    docker rm -f "$PG_CONTAINER" "$REDIS_CONTAINER" >/dev/null 2>&1 || true
  fi
  if [ -n "${NET_STARTED:-}" ]; then
    docker network rm "$CI_NETWORK" >/dev/null 2>&1 || true
  fi
  if [ -n "${ENV_BACKUP:-}" ] && [ -f "$ENV_BACKUP" ]; then
    mv -f "$ENV_BACKUP" "$ROOT/backend/.env"
  elif [ -n "${ENV_WRITTEN:-}" ]; then
    rm -f "$ROOT/backend/.env"
  fi
}
trap cleanup EXIT

write_backend_env() {
  if [ -f "$ROOT/backend/.env" ]; then
    ENV_BACKUP="$ROOT/backend/.env.ci-local.bak"
    cp -f "$ROOT/backend/.env" "$ENV_BACKUP"
  fi
  ENV_WRITTEN=1
  cp "$ROOT/infra/.env.example" "$ROOT/backend/.env"
  {
    echo "DATABASE_URL=postgresql+asyncpg://absolute:absolute@127.0.0.1:${PG_PORT}/adaptive_tutor"
    echo "REDIS_URL=redis://127.0.0.1:${REDIS_PORT}/0"
    echo "OAUTH_PROVIDER=fake"
    echo "JWT_ACCESS_SECRET=ci-access-secret-not-used-elsewhere-000000"
    echo "JWT_REFRESH_SECRET=ci-refresh-secret-not-used-elsewhere-0000"
    echo "OAUTH_FRONTEND_CALLBACK_URL=http://localhost:5173/auth/callback"
    echo "PUBLIC_BASE_URL=http://localhost:8000"
    echo "CORS_ORIGINS=http://localhost:5173"
    echo "QDRANT_URL=http://localhost:6333"
    echo "FREE_LLM_API_URL=http://localhost:3001/v1"
    echo "FREE_LLM_API_KEY=ci-placeholder"
  } >> "$ROOT/backend/.env"
}

stack_is_up() {
  docker exec "$PG_CONTAINER" pg_isready -U absolute -d adaptive_tutor >/dev/null 2>&1 \
    && docker exec "$REDIS_CONTAINER" redis-cli ping >/dev/null 2>&1
}

start_services() {
  command -v docker >/dev/null 2>&1 || { echo "нужен docker" >&2; return 1; }

  if [ "$FAST" = 1 ] && stack_is_up; then
    echo "стек уже поднят — переиспользую"
    PG_STARTED=1
    return 0
  fi

  # Fast mode keeps fixed names so the next --fast reuses them.
  if [ "$FAST" = 1 ]; then
    PG_CONTAINER="adaptive-tutor-ci-pg"
    REDIS_CONTAINER="adaptive-tutor-ci-redis"
    CI_NETWORK="adaptive-tutor-ci-net"
  fi

  docker rm -f "$PG_CONTAINER" "$REDIS_CONTAINER" >/dev/null 2>&1 || true
  docker network create "$CI_NETWORK" >/dev/null 2>&1 && NET_STARTED=1
  PG_STARTED=1

  docker_run run -d --name "$PG_CONTAINER" --network "$CI_NETWORK" \
    -e POSTGRES_USER=absolute -e POSTGRES_PASSWORD=absolute -e POSTGRES_DB=adaptive_tutor \
    -p "${PG_PORT}:5432" postgres:16-alpine >/dev/null || return 1

  docker_run run -d --name "$REDIS_CONTAINER" --network "$CI_NETWORK" \
    -p "${REDIS_PORT}:6379" redis:7-alpine >/dev/null || return 1

  for _ in $(seq 1 30); do
    if docker exec "$PG_CONTAINER" pg_isready -U absolute -d adaptive_tutor >/dev/null 2>&1 \
       && docker exec "$REDIS_CONTAINER" redis-cli ping >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  echo "postgres или redis не поднялись за 60 секунд" >&2
  return 1
}

rules() {
  local scope=""
  [ "$RUN_FRONTEND" = 0 ] && [ "$RUN_BACKEND" = 1 ] && scope="--scope back"
  [ "$RUN_BACKEND" = 0 ] && [ "$RUN_FRONTEND" = 1 ] && scope="--scope front"

  step "правила репозитория" python "$ROOT/scripts/check_repo_rules.py" $scope
  step "контракт API"        python "$ROOT/scripts/check_api_contract.py"
  step "типы фронтенда"      python "$ROOT/scripts/check_contract_types.py"
}

backend() {
  start_services || return 1
  write_backend_env

  (
    cd "$ROOT/backend" || exit 1
    if [ -d venv ]; then
      # shellcheck disable=SC1091
      source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
    fi
    export PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}"
    step "backend: миграции" alembic upgrade head
    if [ "$FAST" = 0 ]; then
      step "backend: откат ревизии" bash -c "alembic downgrade -1 && alembic upgrade head"
    fi
    step "backend: pytest" python -m pytest ${SUITE:-} -q
  )
}

frontend() {
  (
    cd "$ROOT/frontend" || exit 1
    if [ ! -d node_modules ]; then
      step "frontend: npm ci" npm ci
    fi
    step "frontend: test" npm test
    step "frontend: build" npm run build
  )
}

echo "ci-local — AdaptiveTutor"
[ "$RUN_RULES" = 1 ] && rules
[ "$RUN_BACKEND" = 1 ] && backend
[ "$RUN_FRONTEND" = 1 ] && frontend

echo ""
echo "----"
for row in "${RESULTS[@]:-}"; do
  IFS='|' read -r status secs name <<<"$row"
  printf '%4ss  %s  %s\n' "$secs" "$status" "$name"
done
echo "всего: $((SECONDS - STARTED_AT))с"

if [ "${#FAILED[@]}" -gt 0 ]; then
  echo "упало: ${FAILED[*]}"
  exit 1
fi
echo "зелёный"
exit 0
