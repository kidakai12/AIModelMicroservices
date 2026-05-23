import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_id, get_optional_user_id
from app.database import get_db
from app.models import ModelArtifact, Platform, TaskType
from app.schemas import ModelCreate, ModelListResponse, ModelPublic, ModelUpdate
from app.storage import artifact_path, save_upload

router = APIRouter(prefix="/models", tags=["model-zoo"])


def _can_access(model: ModelArtifact, user_id: uuid.UUID | None) -> bool:
    if model.is_public:
        return True
    return user_id is not None and model.owner_user_id == user_id


@router.get("", response_model=ModelListResponse)
async def list_models(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID | None = Depends(get_optional_user_id),
    platform: Platform | None = None,
    task_type: TaskType | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> ModelListResponse:
    query = select(ModelArtifact)
    if user_id is None:
        query = query.where(ModelArtifact.is_public.is_(True))
    else:
        query = query.where(
            or_(ModelArtifact.is_public.is_(True), ModelArtifact.owner_user_id == user_id)
        )
    if platform:
        query = query.where(ModelArtifact.platform == platform)
    if task_type:
        query = query.where(ModelArtifact.task_type == task_type)
    if search:
        like = f"%{search}%"
        query = query.where(
            or_(ModelArtifact.name.ilike(like), ModelArtifact.description.ilike(like))
        )

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    rows = await db.execute(
        query.order_by(ModelArtifact.created_at.desc()).offset(skip).limit(limit)
    )
    items = list(rows.scalars().all())
    return ModelListResponse(items=items, total=total or 0, skip=skip, limit=limit)


@router.post("", response_model=ModelPublic, status_code=status.HTTP_201_CREATED)
async def upload_model(
    name: str = Form(...),
    platform: Platform = Form(...),
    task_type: TaskType = Form(...),
    file: UploadFile = File(...),
    description: str | None = Form(None),
    version: str = Form("1.0.0"),
    is_public: bool = Form(False),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ModelArtifact:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File is required")

    model = ModelArtifact(
        owner_user_id=user_id,
        name=name,
        description=description,
        platform=platform,
        task_type=task_type,
        version=version,
        is_public=is_public,
        file_name="",
        file_path="",
    )
    db.add(model)
    await db.flush()

    file_name, file_path, file_size = await save_upload(model.id, file)
    model.file_name = file_name
    model.file_path = file_path
    model.file_size = file_size
    await db.commit()
    await db.refresh(model)
    return model


@router.get("/{model_id}", response_model=ModelPublic)
async def get_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID | None = Depends(get_optional_user_id),
) -> ModelArtifact:
    model = await db.get(ModelArtifact, model_id)
    if model is None or not _can_access(model, user_id):
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.patch("/{model_id}", response_model=ModelPublic)
async def update_model(
    model_id: uuid.UUID,
    body: ModelUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ModelArtifact:
    model = await db.get(ModelArtifact, model_id)
    if model is None or model.owner_user_id != user_id:
        raise HTTPException(status_code=404, detail="Model not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(model, field, value)
    await db.commit()
    await db.refresh(model)
    return model


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    model = await db.get(ModelArtifact, model_id)
    if model is None or model.owner_user_id != user_id:
        raise HTTPException(status_code=404, detail="Model not found")
    await db.delete(model)
    await db.commit()


@router.get("/{model_id}/download")
async def download_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID | None = Depends(get_optional_user_id),
) -> FileResponse:
    model = await db.get(ModelArtifact, model_id)
    if model is None or not _can_access(model, user_id):
        raise HTTPException(status_code=404, detail="Model not found")
    try:
        path = artifact_path(model.file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model file missing") from None
    model.download_count += 1
    await db.commit()
    return FileResponse(path, filename=model.file_name, media_type="application/octet-stream")
