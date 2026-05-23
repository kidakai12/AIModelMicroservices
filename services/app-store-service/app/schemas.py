import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import Platform


class AppUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    platform: Platform | None = None
    version: str | None = Field(default=None, max_length=50)
    source_url: str | None = Field(default=None, max_length=512)
    is_public: bool | None = None


class AppPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_user_id: uuid.UUID
    name: str
    description: str | None
    platform: Platform
    version: str
    source_url: str | None
    file_name: str
    file_size: int
    is_public: bool
    install_count: int
    created_at: datetime
    updated_at: datetime


class AppListResponse(BaseModel):
    items: list[AppPublic]
    total: int
    skip: int
    limit: int
