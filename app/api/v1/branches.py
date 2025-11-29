from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api import deps
from app.models import User, UserRole
from app.schemas import (
    BranchAssignAdmin,
    BranchCreate,
    BranchNearby,
    BranchRead,
    BranchUpdate,
)
from app.services.branch_service import BranchService

router = APIRouter(prefix="/branches", tags=["branches"])


@router.post("", response_model=BranchRead, status_code=status.HTTP_201_CREATED)
async def create_branch(
    payload: BranchCreate,
    current_user: User = Depends(deps.allow_pharmacy_admin),
    service: BranchService = Depends(deps.get_branch_service),
):
    pharmacy_id = payload.pharmacy_id or current_user.pharmacy_id
    if pharmacy_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pharmacy context missing")
    if current_user.pharmacy_id and current_user.pharmacy_id != pharmacy_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create for another pharmacy")
    return await service.create_branch(
        pharmacy_id=pharmacy_id,
        name=payload.name,
        address=payload.address,
        phone=payload.phone,
    )


@router.post("/{branch_id}/assign-admin", response_model=BranchRead)
async def assign_branch_admin(
    branch_id: int,
    payload: BranchAssignAdmin,
    _: User = Depends(deps.allow_pharmacy_admin),
    service: BranchService = Depends(deps.get_branch_service),
):
    return await service.assign_admin(branch_id, payload.user_id)


@router.get("", response_model=list[BranchRead])
async def list_branches(
    pharmacy_id: int | None = None,
    current_user: User = Depends(deps.get_current_user),
    service: BranchService = Depends(deps.get_branch_service),
):
    resolved_pharmacy_id = pharmacy_id or current_user.pharmacy_id
    if resolved_pharmacy_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pharmacy context required")
    return await service.list_branches(resolved_pharmacy_id)


@router.patch("/{branch_id}", response_model=BranchRead)
async def update_branch(
    branch_id: int,
    payload: BranchUpdate,
    _: User = Depends(deps.allow_pharmacy_admin),
    service: BranchService = Depends(deps.get_branch_service),
):
    return await service.update_branch(
        branch_id,
        name=payload.name,
        address=payload.address,
        phone=payload.phone,
        longitude=payload.longitude,
        latitude=payload.latitude,
    )


@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branch(
    branch_id: int,
    _: User = Depends(deps.allow_pharmacy_admin),
    service: BranchService = Depends(deps.get_branch_service),
):
    await service.delete_branch(branch_id)


@router.get("/all", response_model=list[BranchRead])
async def list_all_branches(
    service: BranchService = Depends(deps.get_branch_service),
    _: User = Depends(deps.allow_operator),
):
    """Get all branches across all pharmacies (only for operators/superadmins)"""
    return await service.list_all_branches()


@router.get("/nearby", response_model=list[BranchNearby])
async def get_nearby_branches(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    radius_km: float = Query(
        10.0, ge=0, description="Radius in kilometers (0 = no limit)"
    ),
    _: User = Depends(deps.allow_all_users),
    service: BranchService = Depends(deps.get_branch_service),
):
    """
    Har qanday foydalanuvchi uchun yaqin filiallar ro'yxati.
    Foydalanuvchi joylashuvi (latitude/longitude) bo'yicha hisoblanadi.
    """
    items = await service.list_nearby_branches(
        latitude=latitude, longitude=longitude, radius_km=radius_km
    )
    # (Branch, distance_km) -> BranchNearby
    return [
        BranchNearby(branch=BranchRead.model_validate(branch), distance_km=distance)
        for branch, distance in items
    ]

