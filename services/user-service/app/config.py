from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.db_url import normalize_database_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "user-service"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+asyncpg://platform:platform@postgres:5432/user_db"
    )
    # Set true if your provider requires SSL (some external Postgres URLs)
    database_ssl: bool = False

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_db_url(cls, value: str) -> str:
        return normalize_database_url(value)


settings = Settings()
