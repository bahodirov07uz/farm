from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional

from app.api.deps import (
    get_current_user,
    get_order_service,
    allow_cashier,
    allow_branch_admin_or_cashier,
    allow_all_users,
    require_roles,
)
from app.models import User, UserRole
from app.schemas.orders import (
    OrderCreate,
    OrderResponse,
    OrderCreateResponse,
    OrderScanResponse,
    OrderListResponse,
    OrderStatus,
)
from app.services.orders import OrderService


router = APIRouter(prefix="/order", tags=["Orders"])


@router.post(
    "/",
    response_model=OrderCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description="Create a new order with items. All authenticated users can create orders."
)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(allow_all_users),
    service: OrderService = Depends(get_order_service),
):
    """
    Create a new order:
    - **branch_id**: ID of the branch where order is placed
    - **items**: List of items with drug_id, drug_variant_id (optional), and qty
    
    Returns generated order_number and barcode
    """
    return await service.create_order(order_data, current_user.id)


@router.post(
    "/scan",
    response_model=OrderScanResponse,
    summary="Scan and confirm order by barcode",
    description="Scan order by barcode and confirm it. Reduces inventory. Cashier role required."
)
async def scan_order(
    barcode: str = Query(..., description="Order barcode to scan"),
    current_user: User = Depends(allow_cashier),
    service: OrderService = Depends(get_order_service),
):
    """
    Scan and confirm order by barcode:
    - Validates order exists and is pending
    - Checks inventory availability
    - Reduces inventory quantities
    - Marks order as confirmed
    
    Only cashiers, branch admins, operators, and superadmins can scan orders.
    """
    return await service.scan_order(barcode)


@router.get(
    "/my-orders",
    response_model=List[OrderListResponse],
    summary="Get current user's orders",
    description="Get all orders created by the current user"
)
async def get_my_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    current_user: User = Depends(allow_all_users),
    service: OrderService = Depends(get_order_service),
):
    """
    Get orders created by current user with optional status filter
    """
    return await service.get_all_orders(
        skip=skip,
        limit=limit,
        status=status,
        user_id=current_user.id
    )


@router.get(
    "/branch/{branch_id}",
    response_model=List[OrderListResponse],
    summary="Get orders by branch",
    description="Get all orders for a specific branch. Branch admin and cashier access."
)
async def get_branch_orders(
    branch_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    current_user: User = Depends(allow_branch_admin_or_cashier),
    service: OrderService = Depends(get_order_service),
):
    """
    Get all orders for a specific branch:
    - Branch admins and cashiers can view orders for their branches
    - Operators and superadmins can view orders for any branch
    """
    # If user is branch admin or cashier, verify they belong to this branch
    if current_user.role in [UserRole.BRANCH_ADMIN, UserRole.CASHIER]:
        if current_user.branch_id != branch_id:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view orders for your own branch"
            )
    
    return await service.get_all_orders(
        skip=skip,
        limit=limit,
        status=status,
        branch_id=branch_id
    )


@router.get(
    "/pharmacy/{pharmacy_id}",
    response_model=List[OrderListResponse],
    summary="Get orders by pharmacy",
    description="Get all orders for branches under a specific pharmacy. Pharmacy admin access required."
)
async def get_pharmacy_orders(
    pharmacy_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    current_user: User = Depends(
        require_roles(UserRole.PHARMACY_ADMIN, UserRole.OPERATOR, UserRole.SUPERADMIN)
    ),
    service: OrderService = Depends(get_order_service),
):
    """
    Get all orders for branches under a specific pharmacy:
    - Pharmacy admins can view orders for their pharmacy's branches
    - Operators and superadmins can view orders for any pharmacy
    """
    # If user is pharmacy admin, verify they own this pharmacy
    if current_user.role == UserRole.PHARMACY_ADMIN:
        if current_user.pharmacy_id != pharmacy_id:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view orders for your own pharmacy"
            )
    
    return await service.get_orders_by_pharmacy(
        pharmacy_id=pharmacy_id,
        skip=skip,
        limit=limit,
        status=status
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order details",
    description="Get detailed information about a specific order"
)
async def get_order(
    order_id: int,
    current_user: User = Depends(allow_all_users),
    service: OrderService = Depends(get_order_service),
):
    """
    Get order by ID with all items and details.
    Users can only view their own orders unless they are admin/cashier.
    """
    order = await service.get_order_by_id(order_id)
    
    # Permission check
    if current_user.role == UserRole.USER:
        if order.user_id != current_user.id:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own orders"
            )
    elif current_user.role in [UserRole.BRANCH_ADMIN, UserRole.CASHIER]:
        if order.branch_id != current_user.branch_id:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view orders for your branch"
            )
    elif current_user.role == UserRole.PHARMACY_ADMIN:
        # Check if order's branch belongs to user's pharmacy
        is_valid = await service.verify_branch_belongs_to_pharmacy(
            order.branch_id, 
            current_user.pharmacy_id
        )
        if not is_valid:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view orders for your pharmacy's branches"
            )
    
    return order


@router.get(
    "/",
    response_model=List[OrderListResponse],
    summary="Get all orders (Admin only)",
    description="Get list of all orders with optional filters. Operator and Superadmin access only."
)
async def get_all_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    current_user: User = Depends(require_roles(UserRole.OPERATOR, UserRole.SUPERADMIN)),
    service: OrderService = Depends(get_order_service),
):
    """
    Get all orders across the system with filters.
    Only operators and superadmins can access this endpoint.
    """
    return await service.get_all_orders(
        skip=skip,
        limit=limit,
        status=status,
        branch_id=branch_id,
        user_id=user_id
    )


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel order",
    description="Cancel a pending order"
)
async def cancel_order(
    order_id: int,
    current_user: User = Depends(allow_all_users),
    service: OrderService = Depends(get_order_service),
):
    """
    Cancel a pending order:
    - Users can cancel their own pending orders
    - Admins can cancel any pending order
    """
    await service.cancel_order(order_id, current_user)
    return None