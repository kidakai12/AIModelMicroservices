# Deploy on DigitalOcean

Two practical options for this stack.

## Option A — Droplet + Docker Compose (recommended to start)

1. Create a **Droplet** (Ubuntu 24.04, 2 GB RAM minimum; 4 GB+ when training workers are added).
2. Install Docker:

   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   ```

3. Clone the repo on the Droplet and configure:

   ```bash
   cp .env.example .env
   nano .env   # set JWT_SECRET_KEY, tighten passwords
   ```

4. For production, change Postgres credentials in `docker-compose.yml` or use **DigitalOcean Managed PostgreSQL** and set:

   ```env
   DATABASE_URL=postgresql+asyncpg://user:pass@your-db-host:25060/user_db?ssl=require
   ```

5. Run:

   ```bash
   docker compose up -d --build
   ```

6. Point a domain with **HTTPS** (Caddy or nginx + Let's Encrypt) to port 8080, or map gateway to 80/443.

### Firewall

- Allow: `22`, `80`, `443`
- Do **not** expose Postgres `5432` publicly

---

## Option B — App Platform (managed)

Deploy each service as a **component** in one App:

| Component | Source | HTTP Port | Routes |
|-----------|--------|-----------|--------|
| user-service | `services/user-service` | 8000 | `/api/v1/auth`, `/api/v1/users` |
| training-service | `services/training-service` | 8000 | `/api/v1/training` |
| model-zoo-service | `services/model-zoo-service` | 8000 | `/api/v1/models` |
| toolbox-service | `services/toolbox-service` | 8000 | `/api/v1/toolbox` |

Add a **Dev Database** (PostgreSQL) and attach to `user-service`:

- `DATABASE_URL` → use App Platform injected `${db.DATABASE_URL}` (convert to `postgresql+asyncpg://` if needed)
- `JWT_SECRET_KEY` → App secret

**Note:** App Platform does not run the repo’s nginx gateway by default. Either:

- Use **one public service** (gateway) as a custom nginx image, or  
- Register route prefixes per component in the App spec (simpler for MVP: deploy only `user-service` first).

### Managed Postgres connection string

Async SQLAlchemy needs the `asyncpg` driver:

```
postgresql+asyncpg://doadmin:PASSWORD@HOST:25060/defaultdb?sslmode=require
```

---

## Object storage (later)

For datasets and model files, add **DigitalOcean Spaces** (S3-compatible):

- Bucket per environment
- Pre-signed uploads from training-service
- CDN in front of public model downloads

---

## Secrets checklist

- [ ] `JWT_SECRET_KEY` — 32+ random bytes
- [ ] Postgres password — not `platform` in production
- [ ] `CORS_ORIGINS` — your real frontend URL only
- [ ] TLS on all public endpoints
