from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Numeric, Enum as SQLEnum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
import enum

from app.models.base import Base
from app.models.mixins import TimestampMixin


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_number: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    barcode: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey("branches.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    branch: Mapped["Branch"] = relationship("Branch", back_populates="orders")
    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", 
        back_populates="order",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False)
    drug_id: Mapped[int] = mapped_column(Integer, ForeignKey("drugs.id"), nullable=False)
    drug_variant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("drug_variants.id"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    drug: Mapped["Drug"] = relationship("Drug")
    drug_variant: Mapped["DrugVariant | None"] = relationship("DrugVariant")

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, drug_id={self.drug_id}, drug_variant_id={self.drug_variant_id}, quantity={self.quantity})>"