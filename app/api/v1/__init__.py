from fastapi import APIRouter

from app.api.v1 import auth, branches, drugs, inventory, pharmacies, orders

router = APIRouter()
router.include_router(auth.router)
router.include_router(pharmacies.router)
router.include_router(branches.router)
router.include_router(drugs.router)
router.include_router(orders.router)
router.include_router(inventory.router)


__all__ = ["router"]

