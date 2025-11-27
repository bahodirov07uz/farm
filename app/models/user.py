import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class UserRole(str, enum.Enum):
    SUPERADMIN = "superadmin"
    OPERATOR = "operator"
    PHARMACY_ADMIN = "pharmacy_admin"
    BRANCH_ADMIN = "branch_admin"
    CASHIER = "cashier"
    USER = "user"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.USER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    pharmacy_id: Mapped[int | None] = mapped_column(
        ForeignKey("pharmacies.id", ondelete="SET NULL"), nullable=True
    )
    branch_id: Mapped[int | None] = mapped_column(
        ForeignKey("branches.id", ondelete="SET NULL"), nullable=True
    )

    pharmacy = relationship("Pharmacy", back_populates="users")
    branch = relationship("Branch", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    pharmacy_requests = relationship("PharmacyRegistrationRequest", back_populates="owner")

