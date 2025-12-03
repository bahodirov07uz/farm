from datetime import datetime, timezone
from typing import List
import secrets
import string

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.orders import OrderRepository
from app.models.orders import Order, OrderItem, OrderStatus
from app.models import User, UserRole
from app.schemas.orders import (
    OrderCreate, 
    OrderResponse, 
    OrderCreateResponse,
    OrderScanResponse,
    OrderListResponse,
    OrderItemResponse
)


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = OrderRepository(session)

    @staticmethod
    def generate_barcode(length: int = 12) -> str:
        """
        Generate cryptographically secure barcode
        Format: 3 letters + 9 digits (e.g., ABC123456789)
        """
        letters = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(3))
        digits = ''.join(secrets.choice(string.digits) for _ in range(9))
        return f"{letters}{digits}"

    async def generate_unique_barcode(self) -> str:
        """Generate unique barcode with collision handling"""
        max_attempts = 20
        for attempt in range(max_attempts):
            barcode = self.generate_barcode()
            if not await self.repository.check_barcode_exists(barcode):
                return barcode
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate unique barcode after multiple attempts"
        )

    async def create_order(
        self, 
        order_data: OrderCreate, 
        user_id: int
    ) -> OrderCreateResponse:
        """Create a new order"""
        
        # 1. Validate branch exists
        branch = await self.repository.get_branch_by_id(order_data.branch_id)
        if not branch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Branch with id {order_data.branch_id} not found"
            )

        # 2. Validate items are not empty
        if not order_data.items or len(order_data.items) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order must contain at least one item"
            )

        # 3. Validate all drugs exist, check inventory, and calculate totals
        total_amount = 0.0
        validated_items = []

        for item in order_data.items:
            # Validate quantity
            if item.qty <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Quantity must be greater than 0 for drug_id {item.drug_id}"
                )

            drug = await self.repository.get_drug_by_id(item.drug_id)
            if not drug:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Drug with id {item.drug_id} not found"
                )
            
            # Check inventory availability
            inventory = await self.repository.get_inventory_by_branch_and_drug(
                order_data.branch_id,
                item.drug_id,
                item.drug_variant_id
            )
            
            if not inventory:
                drug_name = drug.name
                variant_msg = f" (variant_id: {item.drug_variant_id})" if item.drug_variant_id else ""
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"'{drug_name}'{variant_msg} uchun omborda mahsulot mavjud emas"
                )
            
            if inventory.quantity < item.qty:
                drug_name = drug.name
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"'{drug_name}' uchun yetarli miqdor yo'q. Omborda: {inventory.quantity}, Talab: {item.qty}"
                )
            
            # Get price (variant price takes precedence)
            price = float(drug.price)
            if item.drug_variant_id:
                from app.repositories.drug import DrugRepository
                drug_repo = DrugRepository(self.session)
                variant = await drug_repo.get_variant_by_id(item.drug_variant_id)
                if variant:
                    price = float(variant.price)
            
            # Calculate item subtotal
            subtotal = price * item.qty
            total_amount += subtotal
            
            validated_items.append({
                "drug_id": item.drug_id,
                "drug_variant_id": item.drug_variant_id,
                "quantity": item.qty,
                "price": price,
                "subtotal": subtotal
            })

        # 4. Generate unique barcode and order number
        barcode = await self.generate_unique_barcode()
        order_number = barcode  # Use same value for simplicity

        # 5. Create order
        new_order = Order(
            order_number=order_number,
            barcode=barcode,
            branch_id=order_data.branch_id,
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=total_amount
        )

        order = await self.repository.create_order(new_order)

        # 6. Create order items
        order_items = [
            OrderItem(
                order_id=order.id,
                drug_id=item["drug_id"],
                drug_variant_id=item.get("drug_variant_id"),
                quantity=item["quantity"],
                price=item["price"],
                subtotal=item["subtotal"]
            )
            for item in validated_items
        ]

        await self.repository.create_order_items(order_items)

        # 7. Commit transaction
        await self.session.commit()
        await self.session.refresh(order)

        # 8. Return response
        return OrderCreateResponse(
            id=order.id,
            order_number=order.order_number,
            barcode=order.barcode,
            status=order.status,
            total_amount=order.total_amount,
            created_at=order.created_at
        )

    async def scan_order(self, barcode: str) -> OrderScanResponse:
        """Scan and confirm order (cashier only)"""
        
        # 1. Validate barcode format
        if not barcode or len(barcode) != 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid barcode format"
            )

        # 2. Find order by barcode
        order = await self.repository.get_order_by_barcode(barcode)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Barcode '{barcode}' bo'yicha buyurtma topilmadi"
            )

        # 3. Check order status
        if order.status == OrderStatus.CONFIRMED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Buyurtma allaqachon tasdiqlangan"
            )

        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Buyurtma bekor qilingan"
            )

        # 4. Process each order item and reduce inventory
        for item in order.items:
            inventory = await self.repository.get_inventory_by_branch_and_drug(
                order.branch_id, 
                item.drug_id,
                getattr(item, 'drug_variant_id', None)
            )

            if not inventory:
                drug_name = item.drug.name if item.drug else f"ID:{item.drug_id}"
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"'{drug_name}' uchun omborda inventar topilmadi"
                )

            # Check quantity availability (re-check before confirming)
            if inventory.quantity < item.quantity:
                drug_name = item.drug.name if item.drug else f"ID:{item.drug_id}"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"'{drug_name}' uchun yetarli miqdor yo'q. Mavjud: {inventory.quantity}, Kerak: {item.quantity}"
                )

            # Reduce inventory
            new_quantity = inventory.quantity - item.quantity
            await self.repository.update_inventory_quantity(inventory, new_quantity)

        # 5. Update order status to confirmed
        order.status = OrderStatus.CONFIRMED
        order.confirmed_at = datetime.now(timezone.utc)
        await self.repository.update_order_status(order, OrderStatus.CONFIRMED)

        # 6. Commit transaction
        await self.session.commit()
        await self.session.refresh(order)

        # 7. Return response
        return OrderScanResponse(
            id=order.id,
            order_number=order.order_number,
            barcode=order.barcode,
            status=order.status,
            total_amount=order.total_amount,
            confirmed_at=order.confirmed_at,
            message="Buyurtma muvaffaqiyatli tasdiqlandi"
        )

    async def get_order_by_id(self, order_id: int) -> OrderResponse:
        """Get order details by ID"""
        order = await self.repository.get_order_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {order_id} not found"
            )

        # Build response with items
        items_response = [
            OrderItemResponse(
                id=item.id,
                drug_id=item.drug_id,
                drug_variant_id=item.drug_variant_id,
                quantity=item.quantity,
                price=item.price,
                subtotal=item.subtotal,
                drug_name=item.drug.name if item.drug else None,
                variant_name=item.drug_variant.name if item.drug_variant else None
            )
            for item in order.items
        ]

        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            barcode=order.barcode,
            branch_id=order.branch_id,
            user_id=order.user_id,
            status=order.status,
            total_amount=order.total_amount,
            created_at=order.created_at,
            confirmed_at=order.confirmed_at,
            items=items_response
        )

    async def get_all_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        status: OrderStatus = None,
        branch_id: int = None,
        user_id: int = None
    ) -> List[OrderListResponse]:
        """Get list of orders with filters"""
        orders = await self.repository.get_all_orders(
            skip=skip,
            limit=limit,
            status=status,
            branch_id=branch_id,
            user_id=user_id
        )

        return [
            OrderListResponse(
                id=order.id,
                order_number=order.order_number,
                barcode=order.barcode,
                branch_id=order.branch_id,
                user_id=order.user_id,
                status=order.status,
                total_amount=order.total_amount,
                created_at=order.created_at,
                items_count=len(order.items)
            )
            for order in orders
        ]

    async def get_orders_by_pharmacy(
        self,
        pharmacy_id: int,
        skip: int = 0,
        limit: int = 100,
        status: OrderStatus = None
    ) -> List[OrderListResponse]:
        """Get orders for all branches under a pharmacy"""
        orders = await self.repository.get_orders_by_pharmacy(
            pharmacy_id=pharmacy_id,
            skip=skip,
            limit=limit,
            status=status
        )

        return [
            OrderListResponse(
                id=order.id,
                order_number=order.order_number,
                barcode=order.barcode,
                branch_id=order.branch_id,
                user_id=order.user_id,
                status=order.status,
                total_amount=order.total_amount,
                created_at=order.created_at,
                items_count=len(order.items)
            )
            for order in orders
        ]

    async def verify_branch_belongs_to_pharmacy(
        self,
        branch_id: int,
        pharmacy_id: int
    ) -> bool:
        """Verify if a branch belongs to a pharmacy"""
        branch = await self.repository.get_branch_by_id(branch_id)
        return branch and branch.pharmacy_id == pharmacy_id

    async def cancel_order(self, order_id: int, current_user: User) -> None:
        """Cancel a pending order"""
        order = await self.repository.get_order_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {order_id} not found"
            )

        # Check if order can be cancelled
        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending orders can be cancelled"
            )

        # Permission check
        if current_user.role == UserRole.USER:
            if order.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only cancel your own orders"
                )
        elif current_user.role in [UserRole.BRANCH_ADMIN, UserRole.CASHIER]:
            if order.branch_id != current_user.branch_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only cancel orders for your branch"
                )
        elif current_user.role == UserRole.PHARMACY_ADMIN:
            is_valid = await self.verify_branch_belongs_to_pharmacy(
                order.branch_id,
                current_user.pharmacy_id
            )
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only cancel orders for your pharmacy's branches"
                )

        # Cancel order
        order.status = OrderStatus.CANCELLED
        await self.repository.update_order_status(order, OrderStatus.CANCELLED)
        await self.session.commit()