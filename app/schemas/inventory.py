from datetime import datetime

from app.schemas import BaseSchema


class InventoryBase(BaseSchema):
    branch_id: int
    drug_id: int
    drug_variant_id: int | None = None
    quantity: int = 0
    reorder_level: int = 0


class InventoryCreate(InventoryBase):
    pass


class InventoryRead(InventoryBase):
    model_config = {"from_attributes": True}
    
    id: int
    created_at: datetime
    updated_at: datetime
    drug: dict | None = None  # Will be populated from relationship
    drug_variant: dict | None = None  # Will be populated from relationship
    branch: dict | None = None  # Will be populated from relationship


class InventoryUpdate(BaseSchema):
    quantity: int | None = None
    reorder_level: int | None = None

