from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Drug
from app.repositories.drug import DrugRepository


class DrugService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.drug_repo = DrugRepository(session)

    async def create_drug(
        self,
        *,
        name: str,
        code: str,
        description: str | None,
        price: float,
        images: list[str] | None = None,
        is_active: bool,
    ) -> Drug:
        drug = await self.drug_repo.create(
            name=name, code=code, description=description, price=price, images=images, is_active=is_active
        )
        await self.session.commit()
        await self.session.refresh(drug)
        return drug

    async def list_drugs(self, *, is_active: bool | None = None, search: str | None = None) -> list[Drug]:
        drugs = await self.drug_repo.list(is_active=is_active, search=search)
        return list(drugs)

    async def get_drug(self, drug_id: int) -> Drug | None:
        return await self.drug_repo.get_by_id(drug_id)





