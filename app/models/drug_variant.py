from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class DrugVariant(TimestampMixin, Base):
    __tablename__ = "drug_variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    drug_id: Mapped[int] = mapped_column(
        ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., "5 tablets", "10 tablets"
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # Stock Keeping Unit
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    drug = relationship("Drug", back_populates="variants")
    inventories = relationship(
        "Inventory", back_populates="drug_variant", cascade="all, delete-orphan"
    )

