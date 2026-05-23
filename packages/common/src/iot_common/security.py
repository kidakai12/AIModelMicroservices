from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt


def create_access_token(
    subject: str,
    *,
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: int = 60,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(
    token: str,
    *,
    secret_key: str,
    algorithm: str = "HS256",
) -> dict[str, Any]:
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
