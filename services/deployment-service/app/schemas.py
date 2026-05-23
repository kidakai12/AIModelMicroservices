import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import ResourceType


class DeploymentCreate(BaseModel):
    resource_type: ResourceType
    resource_id: uuid.UUID
    expires_in_hours: int = Field(default=24, ge=1, le=168)


class DeploymentCreated(BaseModel):
    token: str
    resolve_url: str
    artifact_url: str
    qr_url: str
    expires_at: datetime
    resource_type: ResourceType
    resource_id: uuid.UUID
    resource_name: str
    platform: str


class DeploymentResolve(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    token: str
    resource_type: ResourceType
    resource_id: uuid.UUID
    resource_name: str
    platform: str
    artifact_url: str
    expires_at: datetime
