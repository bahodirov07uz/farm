from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Drug
from app.repositories.base import BaseRepository


class DrugRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(
        self,
        *,
        name: str,
        code: str,
        description: str | None,
        price: float,
        images: list[str] | None = None,
        is_active: bool,
    ) -> Drug:
        drug = Drug(name=name, code=code, description=description, price=price, images=images, is_active=is_active)
        self.session.add(drug)
        await self.session.flush()
        await self.session.refresh(drug)
        return drug

    async def get_by_id(self, drug_id: int) -> Drug | None:
        stmt = select(Drug).where(Drug.id == drug_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, *, is_active: bool | None = None, search: str | None = None) -> Sequence[Drug]:
        stmt = select(Drug)
        if is_active is not None:
            stmt = stmt.where(Drug.is_active == is_active)
        if search:
            ilike_term = f"%{search.lower()}%"
            stmt = stmt.where(
                (Drug.name.ilike(ilike_term)) | (Drug.code.ilike(ilike_term))
            )
        result = await self.session.execute(stmt.order_by(Drug.name))
        return result.scalars().all()

    async def get_variant_by_id(self, variant_id: int):
        from app.models import DrugVariant
        stmt = select(DrugVariant).where(DrugVariant.id == variant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()





