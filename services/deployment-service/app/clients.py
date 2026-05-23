import uuid

import httpx
from fastapi import HTTPException

from app.config import settings
from app.models import ResourceType


async def fetch_resource_metadata(
    resource_type: ResourceType,
    resource_id: uuid.UUID,
    authorization: str,
) -> dict:
    if resource_type == ResourceType.model:
        url = f"{settings.model_zoo_url}/api/v1/models/{resource_id}"
    else:
        url = f"{settings.app_store_url}/api/v1/apps/{resource_id}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers={"Authorization": authorization})
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Resource not found or not accessible")
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="Failed to verify resource ownership")
        return response.json()


def public_urls(token: str) -> tuple[str, str, str]:
    base = settings.gateway_public_url.rstrip("/")
    resolve_url = f"{base}/api/v1/deployments/{token}/resolve"
    artifact_url = f"{base}/api/v1/deployments/{token}/artifact"
    qr_url = f"{base}/api/v1/deployments/{token}/qr"
    return resolve_url, artifact_url, qr_url


async def stream_artifact(resource_type: ResourceType, resource_id: uuid.UUID):
    if resource_type == ResourceType.model:
        url = f"{settings.model_zoo_url}/internal/models/{resource_id}/artifact"
    else:
        url = f"{settings.app_store_url}/internal/apps/{resource_id}/artifact"

    client = httpx.AsyncClient(timeout=120.0)
    request = client.build_request("GET", url)
    response = await client.send(request, stream=True)
    if response.status_code >= 400:
        await response.aclose()
        await client.aclose()
        raise HTTPException(status_code=404, detail="Artifact not found")
    return client, response
