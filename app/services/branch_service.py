from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Branch, User, UserRole
from app.repositories.branch import BranchRepository
from app.repositories.user import UserRepository


class BranchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.branch_repo = BranchRepository(session)
        self.user_repo = UserRepository(session)

    async def create_branch(
        self,
        *,
        pharmacy_id: int,
        name: str,
        address: str | None,
        phone: str | None,
    ) -> Branch:
        branch = await self.branch_repo.create(
            pharmacy_id=pharmacy_id,
            name=name,
            address=address,
            phone=phone,
        )
        await self.session.commit()
        await self.session.refresh(branch)
        return branch

    async def assign_admin(self, branch_id: int, user_id: int) -> Branch:
        branch = await self.branch_repo.get_by_id(branch_id)
        if branch is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await self.user_repo.set_role(user, UserRole.BRANCH_ADMIN)
        await self.user_repo.assign_branch(user, branch.id)
        await self.session.commit()
        await self.session.refresh(branch)
        return branch

    async def list_branches(self, pharmacy_id: int) -> list[Branch]:
        branches = await self.branch_repo.list_by_pharmacy(pharmacy_id)
        return list(branches)

    async def update_branch(
        self,
        branch_id: int,
        *,
        name: str | None = None,
        address: str | None = None,
        phone: str | None = None,
    ) -> Branch:
        branch = await self.branch_repo.get_by_id(branch_id)
        if branch is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")

        branch = await self.branch_repo.update_branch(branch, name=name, address=address, phone=phone)
        await self.session.commit()
        await self.session.refresh(branch)
        return branch

    async def delete_branch(self, branch_id: int) -> None:
        branch = await self.branch_repo.get_by_id(branch_id)
        if branch is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
        await self.branch_repo.delete(branch)
        await self.session.commit()


