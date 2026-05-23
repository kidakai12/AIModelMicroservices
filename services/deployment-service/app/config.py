from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+asyncpg" not in url.split("://", 1)[0]:
        return "postgresql+asyncpg://" + url[len("postgresql://") :]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "deployment-service"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://platform:platform@postgres:5432/deployment_db"
    database_ssl: bool = False
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    model_zoo_url: str = "http://model-zoo-service:8000"
    app_store_url: str = "http://app-store-service:8000"
    gateway_public_url: str = "http://localhost:8080"
    deploy_token_expire_hours: int = 24

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_db(cls, value: str) -> str:
        return normalize_database_url(value)


settings = Settings()
