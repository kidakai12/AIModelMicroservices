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
    generic = "generic"


class AppPackage(Base):
    __tablename__ = "app_packages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    platform: Mapped[Platform] = mapped_column(Enum(Platform))
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(512))
    file_size: Mapped[int] = mapped_column(BigInteger, default=0)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    install_count: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
