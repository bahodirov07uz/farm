from datetime import datetime

from pydantic import EmailStr

from app.models.user import UserRole
from app.schemas import BaseSchema


class UserBase(BaseSchema):
    email: EmailStr
    full_name: str | None = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    pharmacy_id: int | None = None
    branch_id: int | None = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime














