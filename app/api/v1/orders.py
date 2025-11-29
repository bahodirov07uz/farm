from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional

from app.api.deps import (
    get_current_user,
    get_current_cashier,
    get_current_admin,
    get_order_service,
)
from app.models import User
from app.schemas.orders import (
    OrderCreate,
    OrderResponse,
    OrderCreateResponse,
    OrderScanResponse,
    OrderListResponse,
    OrderStatus,
)
from app.services.orders import OrderService


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/",
    response_model=OrderCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description="Create a new order with items. User role required."
)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    """
    Create a new order:
    - **branch_id**: ID of the branch where order is placed
    - **items**: List of items with drug_id and qty
    
    Returns generated order_number and barcode (same value)
    """
    return await service.create_order(order_data, current_user.id)


@router.post(
    "/scan/{barcode}",
    response_model=OrderScanResponse,
    summary="Scan and confirm order",
    description="Scan order by barcode and confirm it. Reduces inventory. Cashier role required."
)
async def scan_order(
    barcode: str,
    current_user: User = Depends(get_current_cashier),
    service: OrderService = Depends(get_order_service),
):
    """
    Scan and confirm order by barcode:
    - Validates order exists and is pending
    - Checks inventory availability
    - Reduces inventory quantities
    - Marks order as confirmed
    
    Only cashiers can scan orders.
    """
    return await service.scan_order(barcode)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order details",
    description="Get detailed information about a specific order"
)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    """
    Get order by ID with all items and details
    """
    return await service.get_order_by_id(order_id)


@router.get(
    "/",
    response_model=List[OrderListResponse],
    summary="Get all orders",
    description="Get list of orders with optional filters. Admin role required."
)
async def get_all_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    current_user: User = Depends(get_current_admin),
    service: OrderService = Depends(get_order_service),
):
    """
    Get all orders with filters:
    - **skip**: Pagination offset
    - **limit**: Maximum records to return
    - **status**: Filter by order status (pending, confirmed, cancelled)
    - **branch_id**: Filter by branch
    - **user_id**: Filter by user who created the order
    
    Only admins can access this endpoint.
    """
    return await service.get_all_orders(
        skip=skip,
        limit=limit,
        status=status,
        branch_id=branch_id,
        user_id=user_id
    )