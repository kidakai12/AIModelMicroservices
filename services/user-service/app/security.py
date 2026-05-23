from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
import bcrypt

from app.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(subject: str) -> tuple[str, int]:
    expires_minutes = settings.jwt_access_token_expire_minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire}
    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return token, expires_minutes * 60


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        subject: str | None = payload.get("sub")
        if subject is None:
            raise ValueError("Missing subject")
        return subject
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
