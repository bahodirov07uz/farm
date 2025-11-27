from datetime import datetime
from typing import Any

from app.schemas import BaseSchema


class AuditLogBase(BaseSchema):
    action: str
    entity_type: str
    entity_id: str
    payload: dict[str, Any] | None = None
    user_id: int | None = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    id: int
    created_at: datetime
    updated_at: datetime

