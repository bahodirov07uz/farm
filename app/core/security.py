from datetime import datetime, timedelta, timezone
from typing import Any
import base64
import hashlib

import jwt
import bcrypt

from app.core.config import settings

def _prepare_password_bytes(password: str) -> bytes:
    """
    bcrypt has a 72 byte limit. If password exceeds this, we hash it with SHA-256 first,
    then base64 encode it (as recommended in bcrypt documentation).
    This ensures the password is always <= 72 bytes when encoded.
    """
    password_bytes = password.encode("utf-8")
    
    if len(password_bytes) > 72:
        hashed_bytes = hashlib.sha256(password_bytes).digest()
        password_bytes = base64.b64encode(hashed_bytes)

    if len(password_bytes) > 72:
        raise ValueError("Password preprocessing failed to reduce length below 72 bytes.")
    return password_bytes


def get_password_hash(password: str) -> str:
    """
    Hash password using bcrypt, applying preprocessing for long passwords.
    """
    prepared = _prepare_password_bytes(password)
    hashed = bcrypt.hashpw(prepared, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password with the same preprocessing as get_password_hash.
    If password > 72 bytes, it was hashed with SHA-256 and base64 encoded first.
    """
    prepared = _prepare_password_bytes(plain_password)
    return bcrypt.checkpw(prepared, hashed_password.encode("utf-8"))


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

