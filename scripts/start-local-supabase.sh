#!/usr/bin/env bash
# Start Supabase local + app Docker stack
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v supabase >/dev/null 2>&1; then
  echo "Install Supabase CLI: https://supabase.com/docs/guides/cli/getting-started"
  exit 1
fi

[[ -f .env.supabase ]] || cp .env.supabase.example .env.supabase

echo "Starting Supabase local..."
supabase start

echo "Starting FastAPI microservices..."
docker compose -f docker-compose.supabase.yml --env-file .env.supabase up --build
