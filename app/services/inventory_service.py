from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Branch, Drug, Inventory
from app.repositories.branch import BranchRepository
from app.repositories.drug import DrugRepository
from app.repositories.inventory import InventoryRepository


class InventoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.inventory_repo = InventoryRepository(session)
        self.branch_repo = BranchRepository(session)
        self.drug_repo = DrugRepository(session)

    async def add_inventory(
        self,
        *,
        branch_id: int,
        drug_id: int,
        quantity: int,
        reorder_level: int,
    ) -> Inventory:
        branch = await self._ensure_branch(branch_id)
        drug = await self._ensure_drug(drug_id)

        existing = await self.inventory_repo.get_by_branch_and_drug(branch.id, drug.id)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inventory already exists")

        inventory = await self.inventory_repo.create(
            branch_id=branch.id,
            drug_id=drug.id,
            quantity=quantity,
            reorder_level=reorder_level,
        )
        await self.session.commit()
        await self.session.refresh(inventory)
        return inventory

    async def update_stock(
        self,
        inventory_id: int,
        *,
        quantity: int | None = None,
        reorder_level: int | None = None,
    ) -> Inventory:
        inventory = await self.inventory_repo.get_by_id(inventory_id)
        if inventory is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
        inventory = await self.inventory_repo.update_stock(
            inventory, quantity=quantity, reorder_level=reorder_level
        )
        await self.session.commit()
        await self.session.refresh(inventory)
        return inventory

    async def _ensure_branch(self, branch_id: int) -> Branch:
        branch = await self.branch_repo.get_by_id(branch_id)
        if branch is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
        return branch

    async def _ensure_drug(self, drug_id: int) -> Drug:
        drug = await self.drug_repo.get_by_id(drug_id)
        if drug is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drug not found")
        return drug


