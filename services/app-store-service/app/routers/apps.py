import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_id, get_optional_user_id
from app.database import get_db
from app.models import AppPackage, Platform
from app.schemas import AppListResponse, AppPublic, AppUpdate
from app.storage import artifact_path, save_upload

router = APIRouter(prefix="/apps", tags=["app-store"])


def _can_access(app: AppPackage, user_id: uuid.UUID | None) -> bool:
    if app.is_public:
        return True
    return user_id is not None and app.owner_user_id == user_id


@router.get("", response_model=AppListResponse)
async def list_apps(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID | None = Depends(get_optional_user_id),
    platform: Platform | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> AppListResponse:
    query = select(AppPackage)
    if user_id is None:
        query = query.where(AppPackage.is_public.is_(True))
    else:
        query = query.where(or_(AppPackage.is_public.is_(True), AppPackage.owner_user_id == user_id))
    if platform:
        query = query.where(AppPackage.platform == platform)
    if search:
        like = f"%{search}%"
        query = query.where(or_(AppPackage.name.ilike(like), AppPackage.description.ilike(like)))
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    rows = await db.execute(query.order_by(AppPackage.created_at.desc()).offset(skip).limit(limit))
    return AppListResponse(items=list(rows.scalars().all()), total=total or 0, skip=skip, limit=limit)


@router.post("", response_model=AppPublic, status_code=status.HTTP_201_CREATED)
async def upload_app(
    name: str = Form(...),
    platform: Platform = Form(...),
    file: UploadFile = File(...),
    description: str | None = Form(None),
    version: str = Form("1.0.0"),
    source_url: str | None = Form(None),
    is_public: bool = Form(False),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> AppPackage:
    if not file.filename:
        raise HTTPException(status_code=400, detail="ZIP package is required")

    app_pkg = AppPackage(
        owner_user_id=user_id,
        name=name,
        description=description,
        platform=platform,
        version=version,
        source_url=source_url,
        is_public=is_public,
        file_name="",
        file_path="",
    )
    db.add(app_pkg)
    await db.flush()
    file_name, file_path, file_size = await save_upload(app_pkg.id, file)
    app_pkg.file_name = file_name
    app_pkg.file_path = file_path
    app_pkg.file_size = file_size
    await db.commit()
    await db.refresh(app_pkg)
    return app_pkg


@router.get("/{app_id}", response_model=AppPublic)
async def get_app(
    app_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID | None = Depends(get_optional_user_id),
) -> AppPackage:
    app_pkg = await db.get(AppPackage, app_id)
    if app_pkg is None or not _can_access(app_pkg, user_id):
        raise HTTPException(status_code=404, detail="App not found")
    return app_pkg


@router.patch("/{app_id}", response_model=AppPublic)
async def update_app(
    app_id: uuid.UUID,
    body: AppUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> AppPackage:
    app_pkg = await db.get(AppPackage, app_id)
    if app_pkg is None or app_pkg.owner_user_id != user_id:
        raise HTTPException(status_code=404, detail="App not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(app_pkg, field, value)
    await db.commit()
    await db.refresh(app_pkg)
    return app_pkg


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(
    app_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    app_pkg = await db.get(AppPackage, app_id)
    if app_pkg is None or app_pkg.owner_user_id != user_id:
        raise HTTPException(status_code=404, detail="App not found")
    await db.delete(app_pkg)
    await db.commit()


@router.get("/{app_id}/download")
async def download_app(
    app_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID | None = Depends(get_optional_user_id),
) -> FileResponse:
    app_pkg = await db.get(AppPackage, app_id)
    if app_pkg is None or not _can_access(app_pkg, user_id):
        raise HTTPException(status_code=404, detail="App not found")
    try:
        path = artifact_path(app_pkg.file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="App package missing") from None
    app_pkg.install_count += 1
    await db.commit()
    return FileResponse(path, filename=app_pkg.file_name, media_type="application/zip")
