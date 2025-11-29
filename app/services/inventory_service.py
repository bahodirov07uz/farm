from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Branch, Drug, Inventory
from app.repositories.branch import BranchRepository
from app.repositories.drug import DrugRepository
from app.repositories.inventory import InventoryRepository
from app.repositories.pharmacy import PharmacyRepository


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
        drug_variant_id: int | None = None,
        quantity: int,
        reorder_level: int,
    ) -> Inventory:
        branch = await self._ensure_branch(branch_id)
        drug = await self._ensure_drug(drug_id)

        existing = await self.inventory_repo.get_by_branch_and_drug(
            branch.id, drug.id, drug_variant_id
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inventory already exists")

        inventory = await self.inventory_repo.create(
            branch_id=branch.id,
            drug_id=drug.id,
            drug_variant_id=drug_variant_id,
            quantity=quantity,
            reorder_level=reorder_level,
        )
        await self.session.commit()
        await self.session.refresh(inventory)
        return inventory

    async def get_total_quantity_for_pharmacy(
        self, pharmacy_id: int, drug_id: int, drug_variant_id: int | None = None
    ) -> int:
        """Get total quantity of a drug across all branches of a pharmacy"""
        return await self.inventory_repo.get_total_quantity_by_drug_for_pharmacy(
            pharmacy_id, drug_id, drug_variant_id
        )

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

    async def list_by_branch(self, branch_id: int) -> list[Inventory]:
        """Get all inventory items for a branch"""
        inventories = await self.inventory_repo.list_by_branch(branch_id)
        return list(inventories)

    async def list_by_pharmacy(self, pharmacy_id: int) -> list[Inventory]:
        """Get all inventory items for all branches of a pharmacy"""
        inventories = await self.inventory_repo.list_by_pharmacy(pharmacy_id)
        return list(inventories)

    async def list_branches_with_drug(
        self,
        drug_id: int,
        pharmacy_id: int | None = None,
        min_quantity: int = 1,
    ) -> list[Inventory]:
        """
        Get all inventory rows (branches) that have this drug.
        Optionally filtered by pharmacy and minimum quantity.
        """
        await self._ensure_drug(drug_id)
        inventories = await self.inventory_repo.list_by_drug(
            drug_id=drug_id,
            pharmacy_id=pharmacy_id,
            min_quantity=min_quantity,
        )
        return list(inventories)
