import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.config import settings


def ensure_storage_root() -> Path:
    root = Path(settings.storage_path)
    root.mkdir(parents=True, exist_ok=True)
    return root


async def save_upload(model_id: uuid.UUID, upload: UploadFile) -> tuple[str, str, int]:
    root = ensure_storage_root()
    model_dir = root / str(model_id)
    model_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(upload.filename or "model.bin").name
    dest = model_dir / safe_name
    size = 0
    async with aiofiles.open(dest, "wb") as out:
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            await out.write(chunk)
    return safe_name, str(dest), size


def artifact_path(file_path: str) -> Path:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(file_path)
    return path
