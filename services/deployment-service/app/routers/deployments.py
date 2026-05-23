import io
from datetime import datetime, timezone

import qrcode
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_id
from app.clients import fetch_resource_metadata, public_urls, stream_artifact
from app.config import settings
from app.database import get_db
from app.models import DeploymentToken, ResourceType
from app.schemas import DeploymentCreate, DeploymentCreated, DeploymentResolve

router = APIRouter(prefix="/deployments", tags=["deployment"])


async def _get_valid_token(token: str, db: AsyncSession) -> DeploymentToken:
    from sqlalchemy import select

    row = await db.execute(select(DeploymentToken).where(DeploymentToken.token == token))
    deploy = row.scalar_one_or_none()
    if deploy is None:
        raise HTTPException(status_code=404, detail="Deployment token not found")
    expires = deploy.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Deployment token expired")
    return deploy


@router.post("", response_model=DeploymentCreated, status_code=201)
async def create_deployment(
    body: DeploymentCreate,
    request: Request,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> DeploymentCreated:
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Not authenticated")

    meta = await fetch_resource_metadata(body.resource_type, body.resource_id, auth)
    if str(meta.get("owner_user_id")) != str(user_id):
        raise HTTPException(status_code=403, detail="You do not own this resource")

    token = DeploymentToken.new_token()
    expires_at = DeploymentToken.default_expiry(body.expires_in_hours)
    deploy = DeploymentToken(
        token=token,
        resource_type=body.resource_type,
        resource_id=body.resource_id,
        owner_user_id=user_id,
        resource_name=meta["name"],
        platform=meta["platform"],
        expires_at=expires_at,
    )
    db.add(deploy)
    await db.commit()
    await db.refresh(deploy)

    resolve_url, artifact_url, qr_url = public_urls(token)
    return DeploymentCreated(
        token=token,
        resolve_url=resolve_url,
        artifact_url=artifact_url,
        qr_url=qr_url,
        expires_at=deploy.expires_at,
        resource_type=deploy.resource_type,
        resource_id=deploy.resource_id,
        resource_name=deploy.resource_name,
        platform=deploy.platform,
    )


@router.get("/{token}/resolve", response_model=DeploymentResolve)
async def resolve_deployment(token: str, db: AsyncSession = Depends(get_db)) -> DeploymentResolve:
    deploy = await _get_valid_token(token, db)
    _, artifact_url, _ = public_urls(token)
    deploy.access_count += 1
    await db.commit()
    return DeploymentResolve(
        token=deploy.token,
        resource_type=deploy.resource_type,
        resource_id=deploy.resource_id,
        resource_name=deploy.resource_name,
        platform=deploy.platform,
        artifact_url=artifact_url,
        expires_at=deploy.expires_at,
    )


@router.get("/{token}/artifact")
async def download_artifact(token: str, db: AsyncSession = Depends(get_db)) -> StreamingResponse:
    deploy = await _get_valid_token(token, db)
    client, response = await stream_artifact(deploy.resource_type, deploy.resource_id)
    deploy.access_count += 1
    await db.commit()

    media_type = (
        "application/octet-stream"
        if deploy.resource_type == ResourceType.model
        else "application/zip"
    )

    async def iterator():
        try:
            async for chunk in response.aiter_bytes():
                yield chunk
        finally:
            await response.aclose()
            await client.aclose()

    filename = deploy.resource_name.replace(" ", "_")
    if deploy.resource_type == ResourceType.app:
        filename = f"{filename}.zip"

    return StreamingResponse(
        iterator(),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{token}/qr")
async def deployment_qr(token: str, db: AsyncSession = Depends(get_db)) -> Response:
    deploy = await _get_valid_token(token, db)
    resolve_url, _, _ = public_urls(token)
    img = qrcode.make(resolve_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return Response(content=buffer.getvalue(), media_type="image/png")
