from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


from .audit_log import AuditLogBase, AuditLogCreate, AuditLogRead
from .branch import BranchAssignAdmin, BranchBase, BranchCreate, BranchRead, BranchUpdate
from .drug import DrugBase, DrugCreate, DrugRead
from .inventory import InventoryBase, InventoryCreate, InventoryRead, InventoryUpdate
from .pharmacy import PharmacyBase, PharmacyCreate, PharmacyRead
from .pharmacy_request import (
    PharmacyRequestCreate,
    PharmacyRequestDecision,
    PharmacyRequestRead,
)
from .user import UserBase, UserCreate, UserRead

__all__ = [
    "AuditLogBase",
    "AuditLogCreate",
    "AuditLogRead",
    "BaseSchema",
    "BranchAssignAdmin",
    "BranchBase",
    "BranchCreate",
    "BranchRead",
    "BranchUpdate",
    "DrugBase",
    "DrugCreate",
    "DrugRead",
    "InventoryBase",
    "InventoryCreate",
    "InventoryRead",
    "InventoryUpdate",
    "PharmacyBase",
    "PharmacyCreate",
    "PharmacyRead",
    "PharmacyRequestCreate",
    "PharmacyRequestDecision",
    "PharmacyRequestRead",
    "UserBase",
    "UserCreate",
    "UserRead",
]

