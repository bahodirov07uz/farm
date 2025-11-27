from datetime import datetime

from app.models import PharmacyRequestStatus
from app.schemas import BaseSchema


class PharmacyRequestCreate(BaseSchema):
    name: str
    address: str | None = None
    phone: str | None = None


class PharmacyRequestDecision(BaseSchema):
    reason: str | None = None


class PharmacyRequestRead(BaseSchema):
    id: int
    owner_user_id: int
    name: str
    address: str | None
    phone: str | None
    status: PharmacyRequestStatus
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime


