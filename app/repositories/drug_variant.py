from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DrugVariant
from app.repositories.base import BaseRepository


class DrugVariantRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(
        self,
        *,
        drug_id: int,
        name: str,
        sku: str,
        price: float,
        is_active: bool,
    ) -> DrugVariant:
        variant = DrugVariant(
            drug_id=drug_id, name=name, sku=sku, price=price, is_active=is_active
        )
        self.session.add(variant)
        await self.session.flush()
        await self.session.refresh(variant)
        return variant

    async def get_by_id(self, variant_id: int) -> DrugVariant | None:
        stmt = select(DrugVariant).where(DrugVariant.id == variant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_drug(self, drug_id: int) -> Sequence[DrugVariant]:
        stmt = select(DrugVariant).where(DrugVariant.drug_id == drug_id).order_by(DrugVariant.name)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(
        self,
        variant: DrugVariant,
        *,
        name: str | None = None,
        sku: str | None = None,
        price: float | None = None,
        is_active: bool | None = None,
    ) -> DrugVariant:
        if name is not None:
            variant.name = name
        if sku is not None:
            variant.sku = sku
        if price is not None:
            variant.price = price
        if is_active is not None:
            variant.is_active = is_active
        await self.session.flush()
        await self.session.refresh(variant)
        return variant

    async def delete(self, variant: DrugVariant) -> None:
        await self.session.delete(variant)

