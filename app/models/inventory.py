from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Inventory(TimestampMixin, Base):
    __tablename__ = "inventories"
    __table_args__ = (
        UniqueConstraint("branch_id", "drug_id", name="uq_inventory_branch_drug"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False
    )
    drug_id: Mapped[int] = mapped_column(
        ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reorder_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    branch = relationship("Branch", back_populates="inventories")
    drug = relationship("Drug", back_populates="inventories")


