import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import Platform, TaskType


class ModelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    platform: Platform
    task_type: TaskType
    version: str = Field(default="1.0.0", max_length=50)
    is_public: bool = False


class ModelUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    platform: Platform | None = None
    task_type: TaskType | None = None
    version: str | None = Field(default=None, max_length=50)
    is_public: bool | None = None


class ModelPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_user_id: uuid.UUID
    name: str
    description: str | None
    platform: Platform
    task_type: TaskType
    version: str
    file_name: str
    file_size: int
    is_public: bool
    download_count: int
    created_at: datetime
    updated_at: datetime


class ModelListResponse(BaseModel):
    items: list[ModelPublic]
    total: int
    skip: int
    limit: int
