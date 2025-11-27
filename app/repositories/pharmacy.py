from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Branch, Pharmacy, PharmacyRegistrationRequest, PharmacyRequestStatus
from app.repositories.base import BaseRepository


class PharmacyRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(self, *, name: str, address: str | None, phone: str | None) -> Pharmacy:
        pharmacy = Pharmacy(name=name, address=address, phone=phone)
        self.session.add(pharmacy)
        await self.session.flush()
        await self.session.refresh(pharmacy)
        return pharmacy

    async def get_by_id(self, pharmacy_id: int) -> Pharmacy | None:
        stmt = select(Pharmacy).where(Pharmacy.id == pharmacy_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class PharmacyRequestRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(
        self,
        *,
        owner_user_id: int,
        name: str,
        address: str | None,
        phone: str | None,
    ) -> PharmacyRegistrationRequest:
        request = PharmacyRegistrationRequest(
            owner_user_id=owner_user_id,
            name=name,
            address=address,
            phone=phone,
        )
        self.session.add(request)
        await self.session.flush()
        await self.session.refresh(request)
        return request

    async def get_by_id(self, request_id: int) -> PharmacyRegistrationRequest | None:
        stmt = select(PharmacyRegistrationRequest).where(PharmacyRegistrationRequest.id == request_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_pending(self):
        stmt = select(PharmacyRegistrationRequest).where(
            PharmacyRegistrationRequest.status == PharmacyRequestStatus.PENDING
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def set_status(
        self,
        request: PharmacyRegistrationRequest,
        status: PharmacyRequestStatus,
        rejection_reason: str | None = None,
    ) -> PharmacyRegistrationRequest:
        request.status = status
        request.rejection_reason = rejection_reason
        await self.session.flush()
        await self.session.refresh(request)
        return request


