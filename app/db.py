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


def init_models() -> None:
    """Used by Alembic for autogenerate to ensure models are imported."""
    _ = Base.metadata

