import enum
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import BigInteger, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ResourceType(str, enum.Enum):
    model = "model"
    app = "app"


class DeploymentToken(Base):
    __tablename__ = "deployment_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    resource_type: Mapped[ResourceType] = mapped_column(Enum(ResourceType))
    resource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    resource_name: Mapped[str] = mapped_column(String(200))
    platform: Mapped[str] = mapped_column(String(50))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    access_count: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def new_token() -> str:
        return secrets.token_urlsafe(24)

    @classmethod
    def default_expiry(cls, hours: int) -> datetime:
        return datetime.now(timezone.utc) + timedelta(hours=hours)
