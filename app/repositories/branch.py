from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Branch
from app.repositories.base import BaseRepository


class BranchRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(
        self,
        *,
        pharmacy_id: int,
        name: str,
        address: str | None,
        phone: str | None,
    ) -> Branch:
        branch = Branch(pharmacy_id=pharmacy_id, name=name, address=address, phone=phone)
        self.session.add(branch)
        await self.session.flush()
        await self.session.refresh(branch)
        return branch

    async def get_by_id(self, branch_id: int) -> Branch | None:
        stmt = select(Branch).where(Branch.id == branch_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_pharmacy(self, pharmacy_id: int) -> Sequence[Branch]:
        stmt = select(Branch).where(Branch.pharmacy_id == pharmacy_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_branch(
        self,
        branch: Branch,
        *,
        name: str | None = None,
        address: str | None = None,
        phone: str | None = None,
        longitude: str | None = None,
        latitude: str | None = None,
    ) -> Branch:
        if name is not None:
            branch.name = name
        if address is not None:
            branch.address = address
        if phone is not None:
            branch.phone = phone
        if longitude is not None:
            branch.longitude = longitude

        if latitude is not None:
            branch.latitude = latitude
        await self.session.commit()
        await self.session.refresh(branch)
        return branch

    async def delete(self, branch: Branch) -> None:
        await self.session.delete(branch)

    async def list_all(self) -> list[Branch]:
        stmt = select(Branch).order_by(Branch.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())









