from fastapi import APIRouter, Depends, HTTPException, status

from app.api import deps
from app.models import User
from app.schemas import (
    PharmacyRead,
    PharmacyRequestCreate,
    PharmacyRequestDecision,
    PharmacyRequestRead,
)
from app.services.pharmacy_service import PharmacyService

router = APIRouter(prefix="/pharmacies", tags=["pharmacies"])


@router.post("/requests", response_model=PharmacyRequestRead, status_code=status.HTTP_201_CREATED)
async def create_pharmacy_request(
    payload: PharmacyRequestCreate,
    current_user: User = Depends(deps.get_current_user),
    service: PharmacyService = Depends(deps.get_pharmacy_service),
):
    return await service.create_request(
        owner_user_id=current_user.id,
        name=payload.name,
        address=payload.address,
        phone=payload.phone,
    )


@router.post(
    "/requests/{request_id}/approve",
    response_model=PharmacyRead,
)
async def approve_request(
    request_id: int,
    service: PharmacyService = Depends(deps.get_pharmacy_service),
    _: User = Depends(deps.allow_operator),
):
    return await service.approve_request(request_id)


@router.post(
    "/requests/{request_id}/reject",
    response_model=PharmacyRequestRead,
)
async def reject_request(
    request_id: int,
    payload: PharmacyRequestDecision,
    service: PharmacyService = Depends(deps.get_pharmacy_service),
    _: User = Depends(deps.allow_operator),
):
    return await service.reject_request(request_id, reason=payload.reason)


