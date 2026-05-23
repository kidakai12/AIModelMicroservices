from fastapi import APIRouter, FastAPI

SERVICE_NAME = "training-service"
PLANNED_FEATURES = [
    "Training projects (classification / detection)",
    "Dataset upload and annotation",
    "Training job queue and progress (WebSocket)",
    "Deploy model to IoT device via QR",
]

app = FastAPI(
    title=SERVICE_NAME,
    version="0.0.0-stub",
    description="Cloud AI training — coming soon",
)
router = APIRouter(prefix="/api/v1/training", tags=["training"])


@router.get("/")
async def training_root() -> dict:
    return {
        "service": SERVICE_NAME,
        "status": "planned",
        "message": "Cloud training is not implemented yet. Start with user-service.",
        "planned_features": PLANNED_FEATURES,
    }


app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}
