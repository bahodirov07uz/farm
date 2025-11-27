from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.schemas import BaseSchema


class RegisterRequest(BaseSchema):
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None
    exp: int | None = None
    type: str | None = None


