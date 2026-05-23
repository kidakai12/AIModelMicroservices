# BackendMicro — IoT AI Training Platform (Microservices)

Python microservices backend for an IoT-focused AI model training platform (inspired by MaixHub-style workflows).
**Account:** kidakai12

**Implemented now:** `user-service` (register, login, JWT, profile)  
**Planned services:** `training-service`, `model-zoo-service`, `toolbox-service`

## Tech stack recommendation

| Stack | Verdict |
|-------|---------|
| **FastAPI** (chosen) | Best fit: async I/O, OpenAPI docs, Pydantic validation, fast to ship on DO with Docker. |
| Flask | Fine for small APIs; weaker async story for training jobs / WebSockets later. |
| **.NET** | Excellent for enterprise; heavier ops if your team is Python-first for ML tooling. |
| **Java (Spring)** | Same as .NET — great at scale, more boilerplate for a starter platform. |

For **IoT + cloud training + model artifacts**, Python (FastAPI) + PostgreSQL + object storage + a job queue (Celery/Redis or ARQ) is the usual path. Use .NET/Java later only if you need strict enterprise integration or a JVM-only team.

## Architecture

```
                    ┌─────────────┐
   Clients ────────►│   Gateway   │ :8080
                    │   (nginx)   │
                    └──────┬──────┘
           ┌───────────────┼───────────────┬──────────────┐
           ▼               ▼               ▼              ▼
    user-service    training-service  model-zoo-service  toolbox-service
    (PostgreSQL)         (stub)            (stub)           (stub)
```

## Quick start (Docker — recommended)

**Requirements:** Docker Desktop

```powershell
cd "c:\Users\vohoc\Project\New folder"
copy .env.example .env
# Edit .env — set JWT_SECRET_KEY to a long random string

docker compose up --build
```

Gateway: http://localhost:8080  
User API docs (direct): http://localhost:8000/docs — only if you expose user-service; via gateway use paths below.

### API examples (via gateway :8080)

**Register**

```http
POST http://localhost:8080/api/v1/auth/register
Content-Type: application/json

{
  "email": "dev@example.com",
  "password": "securepass123",
  "full_name": "Dev User"
}
```

**Login**

```http
POST http://localhost:8080/api/v1/auth/login
Content-Type: application/json

{
  "email": "dev@example.com",
  "password": "securepass123"
}
```

**Profile** (Bearer token from login)

```http
GET http://localhost:8080/api/v1/users/me
Authorization: Bearer <access_token>
```

**Health**

- Gateway: `GET http://localhost:8080/`
- Users: `GET http://localhost:8080/health/users`
- Training (stub): `GET http://localhost:8080/health/training`

## Local dev (user-service only, no Docker)

```powershell
cd services\user-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start Postgres locally or use Docker only for DB:
# docker run -d -p 5432:5432 -e POSTGRES_USER=platform -e POSTGRES_PASSWORD=platform -e POSTGRES_DB=user_db postgres:16-alpine

$env:DATABASE_URL = "postgresql+asyncpg://platform:platform@localhost:5432/user_db"
$env:JWT_SECRET_KEY = "dev-secret"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs

## Project layout

```
├── docker-compose.yml      # All services + Postgres + gateway
├── gateway/nginx.conf      # Routes /api/v1/* to services
├── packages/common/        # Shared JWT helpers (for future services)
├── services/
│   ├── user-service/       # ✅ Auth & users
│   ├── training-service/   # 🔜 Cloud training
│   ├── model-zoo-service/  # 🔜 Model catalog
│   └── toolbox-service/    # 🔜 Model conversion
├── render.yaml             # Render Blueprint (all services)
├── render.user-only.yaml   # Render Blueprint (user-service only — recommended for free tier)
└── deploy/
    ├── render/             # Render setup guide
    └── digitalocean/       # DO deployment notes
```

## Deploy on Render (free tier — test before production)

1. Push this repo to **GitHub**.
2. [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint** → connect repo.
3. Use **`render.user-only.yaml`** for minimal free testing (user API + Postgres only),  
   or **`render.yaml`** for user-service + stub services.
4. After deploy, open `https://iot-user-service.onrender.com/docs`.

Full steps, API URLs, and free-tier limits: **[deploy/render/README.md](deploy/render/README.md)**

## DigitalOcean deployment (production)

See [deploy/digitalocean/README.md](deploy/digitalocean/README.md) for:

- **Droplet + Docker Compose** (simplest, full control)
- **App Platform** (managed containers, managed Postgres)

## Roadmap

1. ✅ User service — register, login, JWT, `/users/me`
2. Training service — datasets, jobs, WebSocket progress
3. Model zoo — metadata DB + object storage (Spaces)
4. Toolbox — async convert workers
5. Shared auth middleware package for internal service calls

## License

Private / your project — add a license as needed.
