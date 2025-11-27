from fastapi import APIRouter, Depends, HTTPException, status

from app.api import deps
from app.models import User
from app.schemas import (
    DrugCreate,
    DrugRead,
    InventoryCreate,
    InventoryRead,
    InventoryUpdate,
)
from app.services.drug_service import DrugService
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/drugs", tags=["drugs"])


@router.post("", response_model=DrugRead, status_code=status.HTTP_201_CREATED)
async def create_drug(
    payload: DrugCreate,
    _: User = Depends(deps.allow_operator),
    service: DrugService = Depends(deps.get_drug_service),
):
    return await service.create_drug(
        name=payload.name,
        code=payload.code,
        description=payload.description,
        is_active=payload.is_active,
    )


@router.get("", response_model=list[DrugRead])
async def list_drugs(
    search: str | None = None,
    is_active: bool | None = None,
    service: DrugService = Depends(deps.get_drug_service),
    _: User = Depends(deps.get_current_user),
):
    return await service.list_drugs(is_active=is_active, search=search)


@router.get("/search", response_model=list[DrugRead])
async def search_drugs(
    query: str,
    service: DrugService = Depends(deps.get_drug_service),
    _: User = Depends(deps.get_current_user),
):
    return await service.list_drugs(search=query)


@router.post(
    "/inventory",
    response_model=InventoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_inventory(
    payload: InventoryCreate,
    _: User = Depends(deps.allow_pharmacy_admin),
    service: InventoryService = Depends(deps.get_inventory_service),
):
    return await service.add_inventory(
        branch_id=payload.branch_id,
        drug_id=payload.drug_id,
        quantity=payload.quantity,
        reorder_level=payload.reorder_level,
    )


@router.patch(
    "/inventory/{inventory_id}",
    response_model=InventoryRead,
)
async def update_inventory(
    inventory_id: int,
    payload: InventoryUpdate,
    _: User = Depends(deps.allow_branch_admin_or_cashier),
    service: InventoryService = Depends(deps.get_inventory_service),
):
    if payload.quantity is None and payload.reorder_level is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nothing to update")
    return await service.update_stock(
        inventory_id,
        quantity=payload.quantity,
        reorder_level=payload.reorder_level,
    )

