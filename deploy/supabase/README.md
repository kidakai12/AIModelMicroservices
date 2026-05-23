# Local dev: Supabase CLI + Docker Compose

Use **Supabase local** as your Postgres (and optional Auth/Storage/Studio) while running **FastAPI microservices in Docker**.

## Can FastAPI run with Supabase local?

**Yes.** This project uses Supabase local in the simplest way:

| Piece | Role |
|-------|------|
| **Supabase CLI** | Starts Postgres + Studio + Auth + Storage in Docker |
| **FastAPI user-service** | Connects to Supabase **Postgres** with `DATABASE_URL` + **Alembic** migrations |
| **Your JWT auth** | Stays in FastAPI (register/login) — not Supabase Auth (you can switch later) |

FastAPI does **not** need to run inside Supabase’s containers. It only needs the **database connection string** on port **54322**.

Later you can also call Supabase REST (`:54321`) or use Supabase Auth from a frontend — user-service can stay on custom JWT.

---

## How Docker pieces communicate

Two **separate** Docker setups work together on your machine:

```mermaid
flowchart TB
    subgraph supabase_docker["Supabase CLI (supabase start)"]
        DB[(Postgres :54322)]
        API[Supabase API :54321]
        ST[Studio :54323]
        AUTH[GoTrue Auth]
    end

    subgraph app_docker["docker compose -f docker-compose.supabase.yml"]
        US[user-service :8000]
        GW[gateway nginx :8080]
        TR[training-service stub]
    end

    Browser -->|API tests| GW
    GW --> US
    US -->|SQL asyncpg| DB
    Browser -->|DB UI| ST
```

1. **`supabase start`** — CLI tells Docker to run Supabase’s stack (official images). Postgres listens on **`localhost:54322`**.
2. **`docker compose -f docker-compose.supabase.yml up`** — Builds **your** images (FastAPI, nginx).  
   `user-service` reaches Postgres via **`host.docker.internal:54322`** (host port forwarded from Supabase’s container).
3. **Gateway** (`:8080`) proxies HTTP to `user-service` inside the app compose network (not through Supabase).

### Two compose files compared

| File | Postgres | Use when |
|------|----------|----------|
| `docker-compose.yml` | Bundled `postgres:16` container | Simplest, no Supabase CLI |
| `docker-compose.supabase.yml` | Supabase local on host `:54322` | Match production Supabase / use Studio |

---

## Prerequisites

1. **Docker Desktop** (running)
2. **Supabase CLI** — install:
   - Windows (scoop): `scoop bucket add supabase https://github.com/supabase/scoop-bucket.git && scoop install supabase`
   - Or: `npm install -g supabase`
   - Or: https://supabase.com/docs/guides/cli/getting-started

---

## Quick start

From the repo root:

### 1. Start Supabase

```powershell
supabase start
```

First run downloads images (several minutes). Then note output:

```text
Studio URL: http://127.0.0.1:54323
DB URL:     postgresql://postgres:postgres@127.0.0.1:54322/postgres
```

### 2. Configure env

```powershell
copy .env.supabase.example .env.supabase
```

### 3. Start FastAPI stack

```powershell
docker compose -f docker-compose.supabase.yml --env-file .env.supabase up --build
```

### 4. Test

| What | URL |
|------|-----|
| API (via gateway) | http://localhost:8080/api/v1/auth/register |
| Swagger | http://localhost:8000/docs |
| Supabase Studio | http://127.0.0.1:54323 |
| Health | http://localhost:8080/health/users |

Register/login examples are in the root [README.md](../../README.md).

### 5. Stop

```powershell
# Ctrl+C to stop compose, then:
docker compose -f docker-compose.supabase.yml down
supabase stop
```

---

## Helper script (Windows)

```powershell
.\scripts\start-local-supabase.ps1
```

Runs `supabase start` then compose (if CLI is installed).

---

## Run FastAPI on host (no app Docker)

Useful for debugging with breakpoints:

```powershell
supabase start
cd services\user-service
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres"
$env:JWT_SECRET_KEY = "dev-secret"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

---

## Can this whole project deploy to Docker?

**Yes — it already does.**

| Target | How |
|--------|-----|
| **Local + Supabase** | `supabase start` + `docker-compose.supabase.yml` |
| **Local + bundled DB** | `docker compose up` (`docker-compose.yml`) |
| **Render** | `render.yaml` / Dockerfiles |
| **DigitalOcean** | Droplet + `docker compose` |

Each **microservice** has its own `Dockerfile`. Compose wires them together; Supabase is only the database layer when you choose that mode.

---

## Where is the `users` table?

Created by **Alembic** when `user-service` starts (`alembic upgrade head` in Dockerfile).

In Studio → **Table Editor** → schema `public` → table `users`.

Supabase `seed.sql` is optional; schema ownership for auth is in `services/user-service/alembic/`.

---

## Troubleshooting

**`connection refused` to database**

- Run `supabase status` — DB must be healthy.
- On Windows, ensure `host.docker.internal` works (Docker Desktop default).
- Try `DATABASE_URL` with `@127.0.0.1:54322` only when running uvicorn **on the host**, not inside Docker.

**`supabase` command not found**

- Install CLI (see Prerequisites).

**Port 54322 already in use**

- `supabase stop` or change `[db] port` in `supabase/config.toml` and update `DATABASE_URL`.

**Gateway 502**

- Wait for `user-service` healthcheck (migrations on first boot can take ~30s).

---

## Optional next steps

- Use **Supabase Auth** instead of custom JWT (frontend uses `@supabase/supabase-js`).
- Store model files in **Supabase Storage** from training-service.
- Link **Row Level Security** if tables are accessed via PostgREST.
