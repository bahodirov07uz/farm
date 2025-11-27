from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Pharmacy, PharmacyRegistrationRequest, PharmacyRequestStatus, UserRole
from app.repositories.pharmacy import PharmacyRepository, PharmacyRequestRepository
from app.repositories.user import UserRepository


class PharmacyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.pharmacy_repo = PharmacyRepository(session)
        self.request_repo = PharmacyRequestRepository(session)
        self.user_repo = UserRepository(session)

    async def create_request(
        self,
        *,
        owner_user_id: int,
        name: str,
        address: str | None,
        phone: str | None,
    ) -> PharmacyRegistrationRequest:
        request = await self.request_repo.create(
            owner_user_id=owner_user_id,
            name=name,
            address=address,
            phone=phone,
        )
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def approve_request(self, request_id: int) -> Pharmacy:
        request = await self.request_repo.get_by_id(request_id)
        if request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        if request.status != PharmacyRequestStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already handled")

        pharmacy = await self.pharmacy_repo.create(
            name=request.name,
            address=request.address,
            phone=request.phone,
        )
        owner = await self.user_repo.get_by_id(request.owner_user_id)
        if owner is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")

        await self.user_repo.assign_pharmacy(owner, pharmacy.id)
        await self.user_repo.set_role(owner, UserRole.PHARMACY_ADMIN)
        await self.request_repo.set_status(request, PharmacyRequestStatus.APPROVED)

        await self.session.commit()
        await self.session.refresh(pharmacy)
        return pharmacy

    async def reject_request(self, request_id: int, reason: str | None = None) -> PharmacyRegistrationRequest:
        request = await self.request_repo.get_by_id(request_id)
        if request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        if request.status != PharmacyRequestStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already handled")

        await self.request_repo.set_status(request, PharmacyRequestStatus.REJECTED, rejection_reason=reason)
        await self.session.commit()
        await self.session.refresh(request)
        return request


