from fastapi import APIRouter, FastAPI

SERVICE_NAME = "model-zoo-service"
PLANNED_FEATURES = [
    "Browse and search public models",
    "Upload and version models",
    "Platform tags (MCU, edge board, etc.)",
    "Favorites and download stats",
]

app = FastAPI(title=SERVICE_NAME, version="0.0.0-stub")
router = APIRouter(prefix="/api/v1/models", tags=["model-zoo"])


@router.get("/")
async def model_zoo_root() -> dict:
    return {
        "service": SERVICE_NAME,
        "status": "planned",
        "message": "Model Zoo is not implemented yet.",
        "planned_features": PLANNED_FEATURES,
    }


app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}
