from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Drug, DrugVariant
from app.repositories.drug import DrugRepository
from app.repositories.drug_variant import DrugVariantRepository


class DrugVariantService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.variant_repo = DrugVariantRepository(session)
        self.drug_repo = DrugRepository(session)

    async def create_variant(
        self,
        *,
        drug_id: int,
        name: str,
        sku: str,
        price: float,
        is_active: bool,
    ) -> DrugVariant:
        drug = await self.drug_repo.get_by_id(drug_id)
        if drug is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drug not found")

        variant = await self.variant_repo.create(
            drug_id=drug_id, name=name, sku=sku, price=price, is_active=is_active
        )
        await self.session.commit()
        await self.session.refresh(variant)
        return variant

    async def list_variants_by_drug(self, drug_id: int) -> list[DrugVariant]:
        variants = await self.variant_repo.list_by_drug(drug_id)
        return list(variants)

    async def get_variant(self, variant_id: int) -> DrugVariant | None:
        return await self.variant_repo.get_by_id(variant_id)

    async def update_variant(
        self,
        variant_id: int,
        *,
        name: str | None = None,
        sku: str | None = None,
        price: float | None = None,
        is_active: bool | None = None,
    ) -> DrugVariant:
        variant = await self.variant_repo.get_by_id(variant_id)
        if variant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")

        variant = await self.variant_repo.update(
            variant, name=name, sku=sku, price=price, is_active=is_active
        )
        await self.session.commit()
        await self.session.refresh(variant)
        return variant

    async def delete_variant(self, variant_id: int) -> None:
        variant = await self.variant_repo.get_by_id(variant_id)
        if variant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        await self.variant_repo.delete(variant)
        await self.session.commit()

