from datetime import datetime

from app.schemas import BaseSchema


class DrugBase(BaseSchema):
    name: str
    code: str
    description: str | None = None
    is_active: bool = True


class DrugCreate(DrugBase):
    pass


class DrugRead(DrugBase):
    id: int
    created_at: datetime
    updated_at: datetime


