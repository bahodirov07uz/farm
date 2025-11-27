from datetime import datetime

from app.schemas import BaseSchema


class InventoryBase(BaseSchema):
    branch_id: int
    drug_id: int
    quantity: int = 0
    reorder_level: int = 0


class InventoryCreate(InventoryBase):
    pass


class InventoryRead(InventoryBase):
    id: int
    created_at: datetime
    updated_at: datetime


class InventoryUpdate(BaseSchema):
    quantity: int | None = None
    reorder_level: int | None = None

