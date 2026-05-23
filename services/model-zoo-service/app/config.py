from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+asyncpg" not in url.split("://", 1)[0]:
        return "postgresql+asyncpg://" + url[len("postgresql://") :]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "model-zoo-service"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+asyncpg://platform:platform@postgres:5432/model_zoo_db"
    )
    database_ssl: bool = False

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"

    storage_path: str = "/data/models"
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_db(cls, value: str) -> str:
        return normalize_database_url(value)


settings = Settings()
