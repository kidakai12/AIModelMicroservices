# User Service

Handles authentication and user profiles.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/register` | No | Create account |
| POST | `/api/v1/auth/login` | No | Returns JWT |
| GET | `/api/v1/users/me` | Bearer | Current user |
| PATCH | `/api/v1/users/me` | Bearer | Update profile |
| GET | `/health` | No | Health check |

## Environment

| Variable | Default |
|----------|---------|
| `DATABASE_URL` | `postgresql+asyncpg://platform:platform@postgres:5432/user_db` |
| `JWT_SECRET_KEY` | (required in production) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `CORS_ORIGINS` | comma-separated list |
