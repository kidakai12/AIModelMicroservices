from fastapi import APIRouter, FastAPI

SERVICE_NAME = "toolbox-service"
PLANNED_FEATURES = [
    "Model format conversion (ONNX → device format)",
    "Async convert jobs with status polling",
    "Future: quantization, pruning helpers",
]

app = FastAPI(title=SERVICE_NAME, version="0.0.0-stub")
router = APIRouter(prefix="/api/v1/toolbox", tags=["toolbox"])


@router.get("/")
async def toolbox_root() -> dict:
    return {
        "service": SERVICE_NAME,
        "status": "planned",
        "message": "Toolbox is not implemented yet.",
        "planned_features": PLANNED_FEATURES,
    }


app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}
