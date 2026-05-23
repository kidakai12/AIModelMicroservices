"""Normalize DATABASE_URL for SQLAlchemy asyncpg (Render, Heroku, etc.)."""


def normalize_database_url(url: str) -> str:
    """
    Render and others often provide postgres:// or postgresql:// URLs.
    SQLAlchemy async requires the asyncpg driver prefix.
    """
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+asyncpg" not in url.split("://", 1)[0]:
        return "postgresql+asyncpg://" + url[len("postgresql://") :]
    return url
