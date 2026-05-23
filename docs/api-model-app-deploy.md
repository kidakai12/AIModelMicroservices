# Model Zoo, App Store & Deployment APIs

All routes go through the gateway at `http://localhost:8080` unless noted.

**Auth:** `Authorization: Bearer <token>` from `POST /api/v1/auth/login`

---

## Model Zoo — discover & share models

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/models` | Optional | List public models (+ yours if logged in) |
| POST | `/api/v1/models` | Yes | Upload model (`multipart/form-data`) |
| GET | `/api/v1/models/{id}` | Optional | Model metadata |
| PATCH | `/api/v1/models/{id}` | Yes | Update metadata / publish (`is_public`) |
| DELETE | `/api/v1/models/{id}` | Yes | Delete model |
| GET | `/api/v1/models/{id}/download` | Optional | Download `.kmodel` / binary |

**Upload form fields:** `name`, `platform` (`maixcam|k210|esp32|stm32|generic`), `task_type` (`classification|detection|...`), `file`, optional `description`, `version`, `is_public`

**Query params (list):** `platform`, `task_type`, `search`, `skip`, `limit`

---

## App Store — device apps (ZIP packages)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/apps` | Optional | List public apps |
| POST | `/api/v1/apps` | Yes | Upload app ZIP |
| GET | `/api/v1/apps/{id}` | Optional | App metadata |
| PATCH | `/api/v1/apps/{id}` | Yes | Update / publish |
| DELETE | `/api/v1/apps/{id}` | Yes | Delete app |
| GET | `/api/v1/apps/{id}/download` | Optional | Download ZIP |

**Upload form fields:** `name`, `platform`, `file` (ZIP), optional `description`, `version`, `source_url`, `is_public`

---

## Deployment — QR to hardware

Create a time-limited deploy link + QR for a **model** or **app** you own.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/deployments` | Yes | Create deploy token |
| GET | `/api/v1/deployments/{token}/resolve` | No | Device reads metadata + artifact URL |
| GET | `/api/v1/deployments/{token}/artifact` | No | Device downloads file |
| GET | `/api/v1/deployments/{token}/qr` | No | PNG QR code (encodes resolve URL) |

**Create body (JSON):**

```json
{
  "resource_type": "model",
  "resource_id": "uuid-of-model",
  "expires_in_hours": 24
}
```

Use `"resource_type": "app"` for App Store packages.

**Device flow (MaixHub-style):**

1. User creates deployment → receives `qr_url`, `resolve_url`, `artifact_url`
2. Device scans QR → opens `resolve_url` → gets `artifact_url`
3. Device `GET artifact_url` → downloads model/app binary

**Example:**

```http
POST http://localhost:8080/api/v1/deployments
Authorization: Bearer <token>
Content-Type: application/json

{"resource_type": "model", "resource_id": "<model-uuid>", "expires_in_hours": 48}
```

Open QR in browser: `GET http://localhost:8080/api/v1/deployments/<token>/qr`

---

## Service docs (direct ports in Supabase compose)

| Service | Port |
|---------|------|
| user-service | 8000 |
| model-zoo-service | 8001 |
| app-store-service | 8002 |
| deployment-service | 8003 |

Each has `/docs` when exposed.
