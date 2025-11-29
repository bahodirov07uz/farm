from datetime import datetime

from app.schemas import BaseSchema


class BranchBase(BaseSchema):
    name: str
    address: str | None = None
    phone: str | None = None
    latitude: str | None = None
    longitude: str | None = None

class BranchCreate(BranchBase):
    pharmacy_id: int | None = None


class BranchRead(BranchBase):
    id: int
    pharmacy_id: int
    created_at: datetime
    updated_at: datetime


class BranchNearby(BaseSchema):
    branch: BranchRead
    distance_km: float


class BranchUpdate(BaseSchema):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    longitude: str |None = None
    latitude:str | None= None

class BranchAssignAdmin(BaseSchema):
    user_id: int

