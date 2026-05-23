import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.database import SessionLocal
from app.storage import artifact_path
from app.models import AppPackage

router = APIRouter(prefix="/internal/apps", tags=["internal"])


@router.get("/{app_id}/artifact")
async def internal_download_artifact(app_id: uuid.UUID) -> FileResponse:
    async with SessionLocal() as db:
        app_pkg = await db.get(AppPackage, app_id)
        if app_pkg is None:
            raise HTTPException(status_code=404, detail="App not found")
        try:
            path = artifact_path(app_pkg.file_path)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="App package missing") from None
        return FileResponse(path, filename=app_pkg.file_name, media_type="application/zip")
