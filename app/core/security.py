from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: str | Any, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(tz=timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str | Any) -> str:
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    return _create_token(subject, expires_delta, token_type="access")


def create_refresh_token(subject: str | Any) -> str:
    expires_delta = timedelta(minutes=settings.refresh_token_expire_minutes)
    return _create_token(subject, expires_delta, token_type="refresh")


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

