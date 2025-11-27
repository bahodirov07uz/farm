from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Branch(TimestampMixin, Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    pharmacy_id: Mapped[int] = mapped_column(
        ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False
    )

    pharmacy = relationship("Pharmacy", back_populates="branches")
    inventories = relationship(
        "Inventory", back_populates="branch", cascade="all, delete-orphan"
    )
    users = relationship("User", back_populates="branch")


