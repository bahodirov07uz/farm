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

    @staticmethod
    def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Hisoblash: Yer sharida ikkita nuqta orasidagi masofa (km) – Haversine formulasi.
        """
        from math import radians, sin, cos, sqrt, atan2

        R = 6371.0  # Yer radiusi (km)

        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = (
            sin(dlat / 2) ** 2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

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
        latitude: str | None = None,
        longitude: str | None = None,
    ) -> Branch:
        branch = await self.branch_repo.get_by_id(branch_id)
        if branch is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")

        branch = await self.branch_repo.update_branch(branch, name=name, address=address, phone=phone,latitude=latitude,longitude=longitude)
        await self.session.commit()
        await self.session.refresh(branch)
        return branch

    async def delete_branch(self, branch_id: int) -> None:
        branch = await self.branch_repo.get_by_id(branch_id)
        if branch is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
        await self.branch_repo.delete(branch)
        await self.session.commit()

    async def list_all_branches(self) -> list[Branch]:
        branches = await self.branch_repo.list_all()
        return list(branches)

    async def list_nearby_branches(
        self, *, latitude: float, longitude: float, radius_km: float = 10.0
    ) -> list[tuple[Branch, float]]:
        """
        Foydalanuvchi joylashuviga yaqin filiallar ro'yxati (masofa km bilan).
        """
        branches = await self.branch_repo.list_all()
        results: list[tuple[Branch, float]] = []

        for branch in branches:
            if not branch.latitude or not branch.longitude:
                continue
            try:
                br_lat = float(branch.latitude)
                br_lon = float(branch.longitude)
            except (TypeError, ValueError):
                continue

            distance = self._haversine_km(latitude, longitude, br_lat, br_lon)
            if radius_km <= 0 or distance <= radius_km:
                results.append((branch, distance))

        # Masofa bo'yicha sortlash
        results.sort(key=lambda x: x[1])
        return results









