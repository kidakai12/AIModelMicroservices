# Start Supabase local + app Docker stack (Windows)
# Requires: Docker Desktop, Supabase CLI

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

if (-not (Get-Command supabase -ErrorAction SilentlyContinue)) {
    Write-Host "Supabase CLI not found. Install: https://supabase.com/docs/guides/cli/getting-started" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".env.supabase")) {
    Copy-Item ".env.supabase.example" ".env.supabase"
    Write-Host "Created .env.supabase from example."
}

Write-Host "Starting Supabase local (Docker)..." -ForegroundColor Cyan
supabase start

Write-Host "Starting FastAPI microservices..." -ForegroundColor Cyan
docker compose -f docker-compose.supabase.yml --env-file .env.supabase up --build
