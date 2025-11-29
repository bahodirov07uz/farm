from fastapi import APIRouter, Depends, HTTPException, Query

from app.api import deps
from app.models import User
from app.schemas.inventory import InventoryRead
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/pharmacy/{pharmacy_id}/drug/{drug_id}/total")
async def get_total_quantity_for_pharmacy(
    pharmacy_id: int,
    drug_id: int,
    drug_variant_id: int | None = Query(None, description="Drug variant ID (optional)"),
    current_user: User = Depends(deps.allow_pharmacy_admin),
    service: InventoryService = Depends(deps.get_inventory_service),
):
    """
    Get total quantity of a drug across all branches of a pharmacy.
    Only pharmacy_admin can see aggregated inventory for their pharmacy.
    """
    # Check if user has access to this pharmacy
    if current_user.pharmacy_id != pharmacy_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view inventory for your own pharmacy"
        )
    
    total = await service.get_total_quantity_for_pharmacy(
        pharmacy_id, drug_id, drug_variant_id
    )
    return {
        "pharmacy_id": pharmacy_id,
        "drug_id": drug_id,
        "drug_variant_id": drug_variant_id,
        "total_quantity": total,
    }


@router.get("/branch/{branch_id}", response_model=list[InventoryRead])
async def list_inventory_by_branch(
    branch_id: int,
    current_user: User = Depends(deps.get_current_user),
    service: InventoryService = Depends(deps.get_inventory_service),
):
    """Get all inventory items for a specific branch"""
    return await service.list_by_branch(branch_id)


@router.get("/pharmacy/{pharmacy_id}", response_model=list[InventoryRead])
async def list_inventory_by_pharmacy(
    pharmacy_id: int,
    current_user: User = Depends(deps.allow_pharmacy_admin),
    service: InventoryService = Depends(deps.get_inventory_service),
):
    """Get all inventory items for all branches of a pharmacy"""
    if current_user.pharmacy_id != pharmacy_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view inventory for your own pharmacy"
        )
    return await service.list_by_pharmacy(pharmacy_id)


@router.get("/drug/{drug_id}/branches", response_model=list[InventoryRead])
async def list_branches_with_drug(
    drug_id: int,
    pharmacy_id: int | None = Query(
        None, description="Filter by pharmacy ID (optional, default: current user's pharmacy)"
    ),
    min_quantity: int = Query(
        1, ge=0, description="Minimum quantity in stock (default: 1)"
    ),
    current_user: User = Depends(deps.allow_all_users),
    service: InventoryService = Depends(deps.get_inventory_service),
):
    """
    Berilgan dori mavjud bo'lgan filiallar ro'yxati.
    Agar `pharmacy_id` berilmasa, foydalanuvchining o'z aptekasi bo'yicha filtrlanadi (agar mavjud bo'lsa).
    """
    resolved_pharmacy_id = pharmacy_id or current_user.pharmacy_id
    return await service.list_branches_with_drug(
        drug_id=drug_id,
        pharmacy_id=resolved_pharmacy_id,
        min_quantity=min_quantity,
    )

