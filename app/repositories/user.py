from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Branch, User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, *, email: str, hashed_password: str, full_name: str | None = None) -> User:
        user = User(email=email, hashed_password=hashed_password, full_name=full_name)
        self.session.add(user)
        await self.session.flush()
        return user

    async def set_role(self, user: User, role: UserRole) -> User:
        user.role = role
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def assign_pharmacy(self, user: User, pharmacy_id: int | None) -> User:
        user.pharmacy_id = pharmacy_id
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def assign_branch(self, user: User, branch_id: int | None) -> User:
        user.branch_id = branch_id
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def list_by_role(self, role: UserRole) -> Sequence[User]:
        stmt = select(User).where(User.role == role)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_branch_admin(self, branch_id: int) -> User | None:
        stmt = select(User).where(User.branch_id == branch_id, User.role == UserRole.BRANCH_ADMIN)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


