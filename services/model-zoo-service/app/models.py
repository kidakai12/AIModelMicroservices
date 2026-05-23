import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Platform(str, enum.Enum):
    maixcam = "maixcam"
    k210 = "k210"
    esp32 = "esp32"
    stm32 = "stm32"
    generic = "generic"


class TaskType(str, enum.Enum):
    classification = "classification"
    detection = "detection"
    segmentation = "segmentation"
    other = "other"


class ModelArtifact(Base):
    __tablename__ = "model_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    platform: Mapped[Platform] = mapped_column(Enum(Platform))
    task_type: Mapped[TaskType] = mapped_column(Enum(TaskType))
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(512))
    file_size: Mapped[int] = mapped_column(BigInteger, default=0)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    download_count: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
