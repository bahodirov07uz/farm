from datetime import datetime

from app.schemas import BaseSchema


class PharmacyBase(BaseSchema):
    name: str
    address: str | None = None
    phone: str | None = None


class PharmacyCreate(PharmacyBase):
    pass


class PharmacyRead(PharmacyBase):
    id: int
    created_at: datetime
    updated_at: datetime














