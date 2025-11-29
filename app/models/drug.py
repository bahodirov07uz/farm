from sqlalchemy import Boolean, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Drug(TimestampMixin, Base):
    __tablename__ = "drugs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)  # Base price
    images: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)  # List of image URLs
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    variants = relationship(
        "DrugVariant", back_populates="drug", cascade="all, delete-orphan"
    )
    inventories = relationship(
        "Inventory", back_populates="drug", cascade="all, delete-orphan"
    )





