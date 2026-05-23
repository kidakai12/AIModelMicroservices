import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.database import SessionLocal
from app.models import ModelArtifact
from app.storage import artifact_path

router = APIRouter(prefix="/internal/models", tags=["internal"])


@router.get("/{model_id}/artifact")
async def internal_download_artifact(model_id: uuid.UUID) -> FileResponse:
    """Docker-network only — used by deployment-service to proxy device downloads."""
    async with SessionLocal() as db:
        model = await db.get(ModelArtifact, model_id)
        if model is None:
            raise HTTPException(status_code=404, detail="Model not found")
        try:
            path = artifact_path(model.file_path)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Model file missing") from None
        return FileResponse(path, filename=model.file_name, media_type="application/octet-stream")
