from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models import Base


engine = create_async_engine(settings.database_url, future=True, echo=settings.debug)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


def get_sync_engine():
    from sqlalchemy import create_engine

    return create_engine(settings.sync_database_url, future=True)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# app/db.py

def init_models() -> None:
    """Used by Alembic for autogenerate to ensure models are imported."""
    # Import all models for Alembic
    from app.models.pharmacy import Pharmacy
    from app.models.user import User
    from app.models.drug import Drug
    from app.models.drug_variant import DrugVariant
    from app.models.inventory import Inventory
    from app.models.orders import Order, OrderItem
    from app.models.branch import Branch
    from app.models.audit_log import AuditLog
    from app.models.pharmacy_request import PharmacyRegistrationRequest

    _ = Base.metadata  # Alembic Base.metadata uchun
