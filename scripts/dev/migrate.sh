#!/usr/bin/env bash
set -euo pipefail

# Always use the compose file in infra/
COMPOSE="docker compose -f infra/docker-compose.yml"

echo "[Migration] Bringing up containers..."
$COMPOSE up -d

echo "[Migration] Initializing database and seeding demo data..."
$COMPOSE exec api python -c "from app.core.database import init_db, seed_demo; init_db(); seed_demo()"

echo "[Migration] Done."
