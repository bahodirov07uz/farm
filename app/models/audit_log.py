from typing import Any

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="audit_logs")

