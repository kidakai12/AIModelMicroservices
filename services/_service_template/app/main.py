"""Copy this pattern when implementing a new microservice."""

from fastapi import APIRouter, FastAPI

SERVICE_NAME = "service-name"
PLANNED_FEATURES: list[str] = []

app = FastAPI(title=SERVICE_NAME, version="0.0.0-stub")
router = APIRouter(prefix="/api/v1", tags=[SERVICE_NAME])


@router.get("/")
async def not_implemented() -> dict:
    return {
        "service": SERVICE_NAME,
        "status": "planned",
        "message": "This service is not implemented yet.",
        "planned_features": PLANNED_FEATURES,
    }


app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}
