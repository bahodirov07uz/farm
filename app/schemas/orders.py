from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


# Order Item Schemas
class OrderItemCreate(BaseModel):
    drug_id: int = Field(..., gt=0, description="Drug ID must be positive")
    drug_variant_id: Optional[int] = Field(None, gt=0, description="Drug variant ID (optional)")
    qty: int = Field(..., gt=0, description="Quantity must be greater than 0")


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    drug_id: int
    drug_variant_id: Optional[int] = None
    quantity: int
    price: float
    subtotal: float
    drug_name: Optional[str] = None
    variant_name: Optional[str] = None


# Order Schemas
class OrderCreate(BaseModel):
    branch_id: int = Field(..., gt=0, description="Branch ID must be positive")
    items: List[OrderItemCreate] = Field(..., min_length=1, description="At least one item required")

    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError("Order must contain at least one item")
        
        # Check for duplicate drug_id + drug_variant_id combinations
        item_keys = [(item.drug_id, item.drug_variant_id) for item in v]
        if len(item_keys) != len(set(item_keys)):
            raise ValueError("Duplicate drug_id + drug_variant_id combinations are not allowed in a single order")
        
        return v


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    barcode: str
    branch_id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []


class OrderCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    barcode: str
    status: OrderStatus
    total_amount: float
    created_at: datetime


class OrderScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    barcode: str
    status: OrderStatus
    total_amount: float
    confirmed_at: datetime
    message: str


class OrderListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    barcode: str
    branch_id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    created_at: datetime
    items_count: int