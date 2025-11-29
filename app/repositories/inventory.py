from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Branch, Inventory
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_branch_and_drug(
        self, branch_id: int, drug_id: int, drug_variant_id: int | None = None
    ) -> Inventory | None:
        stmt = select(Inventory).where(
            Inventory.branch_id == branch_id,
            Inventory.drug_id == drug_id,
        )
        if drug_variant_id is not None:
            stmt = stmt.where(Inventory.drug_variant_id == drug_variant_id)
        else:
            stmt = stmt.where(Inventory.drug_variant_id.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_total_quantity_by_drug_for_pharmacy(
        self, pharmacy_id: int, drug_id: int, drug_variant_id: int | None = None
    ) -> int:
        """Get total quantity of a drug across all branches of a pharmacy"""
        stmt = (
            select(func.sum(Inventory.quantity))
            .join(Branch, Inventory.branch_id == Branch.id)
            .where(Branch.pharmacy_id == pharmacy_id, Inventory.drug_id == drug_id)
        )
        if drug_variant_id is not None:
            stmt = stmt.where(Inventory.drug_variant_id == drug_variant_id)
        else:
            stmt = stmt.where(Inventory.drug_variant_id.is_(None))
        result = await self.session.execute(stmt)
        total = result.scalar()
        return total or 0

    async def create(
        self,
        *,
        branch_id: int,
        drug_id: int,
        drug_variant_id: int | None = None,
        quantity: int,
        reorder_level: int,
    ) -> Inventory:
        inventory = Inventory(
            branch_id=branch_id,
            drug_id=drug_id,
            drug_variant_id=drug_variant_id,
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

    async def list_by_branch(self, branch_id: int) -> Sequence[Inventory]:
        """Get all inventory items for a branch"""
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Inventory)
            .options(
                selectinload(Inventory.drug),
                selectinload(Inventory.drug_variant),
                selectinload(Inventory.branch)
            )
            .where(Inventory.branch_id == branch_id)
            .order_by(Inventory.drug_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_pharmacy(self, pharmacy_id: int) -> Sequence[Inventory]:
        """Get all inventory items for all branches of a pharmacy"""
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Inventory)
            .options(
                selectinload(Inventory.drug),
                selectinload(Inventory.drug_variant),
                selectinload(Inventory.branch),
            )
            .join(Branch, Inventory.branch_id == Branch.id)
            .where(Branch.pharmacy_id == pharmacy_id)
            .order_by(Inventory.branch_id, Inventory.drug_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_drug(
        self,
        drug_id: int,
        pharmacy_id: int | None = None,
        min_quantity: int = 1,
    ) -> Sequence[Inventory]:
        """
        Get all inventory rows for a specific drug (optionally filtered by pharmacy).
        """
        from sqlalchemy.orm import selectinload

        stmt = (
            select(Inventory)
            .options(
                selectinload(Inventory.drug),
                selectinload(Inventory.drug_variant),
                selectinload(Inventory.branch),
            )
            .join(Branch, Inventory.branch_id == Branch.id)
            .where(Inventory.drug_id == drug_id)
        )
        if pharmacy_id is not None:
            stmt = stmt.where(Branch.pharmacy_id == pharmacy_id)
        if min_quantity is not None and min_quantity > 0:
            stmt = stmt.where(Inventory.quantity >= min_quantity)
        result = await self.session.execute(stmt)
        return result.scalars().all()
