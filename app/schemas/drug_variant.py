from datetime import datetime

from app.schemas import BaseSchema


class DrugVariantBase(BaseSchema):
    drug_id: int
    name: str
    sku: str
    price: float = 0.0
    is_active: bool = True


class DrugVariantCreate(DrugVariantBase):
    pass


class DrugVariantRead(DrugVariantBase):
    id: int
    created_at: datetime
    updated_at: datetime


class DrugVariantUpdate(BaseSchema):
    name: str | None = None
    sku: str | None = None
    price: float | None = None
    is_active: bool | None = None

