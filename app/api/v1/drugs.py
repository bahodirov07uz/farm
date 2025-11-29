from fastapi import APIRouter, Depends, HTTPException, status

from app.api import deps
from app.models import User
from app.schemas import (
    DrugCreate,
    DrugRead,
    DrugVariantCreate,
    DrugVariantRead,
    DrugVariantUpdate,
    InventoryCreate,
    InventoryRead,
    InventoryUpdate,
)
from app.services.drug_service import DrugService
from app.services.drug_variant_service import DrugVariantService
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/drugs", tags=["drugs"])


@router.post("", response_model=DrugRead, status_code=status.HTTP_201_CREATED)
async def create_drug(
    payload: DrugCreate,
    _: User = Depends(deps.allow_branch_admin_or_cashier),
    service: DrugService = Depends(deps.get_drug_service),
):
    return await service.create_drug(
        name=payload.name,
        code=payload.code,
        description=payload.description,
        price=payload.price,
        images=payload.images,
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
        drug_variant_id=payload.drug_variant_id,
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


@router.get("/all", response_model=list[DrugRead])
async def list_all_drugs(
    service: DrugService = Depends(deps.get_drug_service),
    _: User = Depends(deps.get_current_user),
):
    """Get all drugs (no filters)"""
    return await service.list_drugs()


@router.post("/variants", response_model=DrugVariantRead, status_code=status.HTTP_201_CREATED)
async def create_drug_variant(
    payload: DrugVariantCreate,
    _: User = Depends(deps.allow_branch_admin_or_cashier),
    service: DrugVariantService = Depends(deps.get_drug_variant_service),
):
    return await service.create_variant(
        drug_id=payload.drug_id,
        name=payload.name,
        sku=payload.sku,
        price=payload.price,
        is_active=payload.is_active,
    )


@router.get("/variants/{drug_id}", response_model=list[DrugVariantRead])
async def list_drug_variants(
    drug_id: int,
    service: DrugVariantService = Depends(deps.get_drug_variant_service),
    _: User = Depends(deps.get_current_user),
):
    """Get all variants for a specific drug"""
    return await service.list_variants_by_drug(drug_id)


@router.patch("/variants/{variant_id}", response_model=DrugVariantRead)
async def update_drug_variant(
    variant_id: int,
    payload: DrugVariantUpdate,
    _: User = Depends(deps.allow_operator),
    service: DrugVariantService = Depends(deps.get_drug_variant_service),
):
    return await service.update_variant(
        variant_id,
        name=payload.name,
        sku=payload.sku,
        price=payload.price,
        is_active=payload.is_active,
    )


@router.delete("/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_drug_variant(
    variant_id: int,
    _: User = Depends(deps.allow_operator),
    service: DrugVariantService = Depends(deps.get_drug_variant_service),
):
    await service.delete_variant(variant_id)

