from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Inventory
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_branch_and_drug(self, branch_id: int, drug_id: int) -> Inventory | None:
        stmt = select(Inventory).where(
            Inventory.branch_id == branch_id,
            Inventory.drug_id == drug_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        branch_id: int,
        drug_id: int,
        quantity: int,
        reorder_level: int,
    ) -> Inventory:
        inventory = Inventory(
            branch_id=branch_id,
            drug_id=drug_id,
            quantity=quantity,
            reorder_level=reorder_level,
        )
        self.session.add(inventory)
        await self.session.flush()
        await self.session.refresh(inventory)
        return inventory

    async def update_stock(
        self,
        inventory: Inventory,
        *,
        quantity: int | None = None,
        reorder_level: int | None = None,
    ) -> Inventory:
        if quantity is not None:
            inventory.quantity = quantity
        if reorder_level is not None:
            inventory.reorder_level = reorder_level
        await self.session.flush()
        await self.session.refresh(inventory)
        return inventory

    async def get_by_id(self, inventory_id: int) -> Inventory | None:
        stmt = select(Inventory).where(Inventory.id == inventory_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


