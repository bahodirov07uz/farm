from datetime import datetime, timezone
from typing import List
import random
import string

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.orders import OrderRepository
from app.models.orders import Order, OrderItem, OrderStatus
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
    def generate_random_code(length: int = None) -> str:
        """Generate random alphanumeric code (6-10 characters)"""
        if length is None:
            length = random.randint(6, 10)
        
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    async def generate_unique_barcode(self) -> str:
        """Generate unique barcode"""
        max_attempts = 10
        for _ in range(max_attempts):
            barcode = self.generate_random_code()
            if not await self.repository.check_barcode_exists(barcode):
                return barcode
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate unique barcode"
        )

    async def generate_unique_order_number(self) -> str:
        """Generate unique order number"""
        max_attempts = 10
        for _ in range(max_attempts):
            order_number = self.generate_random_code()
            if not await self.repository.check_order_number_exists(order_number):
                return order_number
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate unique order number"
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

        # 2. Validate all drugs exist, check inventory, and calculate totals
        total_amount = 0.0
        validated_items = []

        for item in order_data.items:
            drug = await self.repository.get_drug_by_id(item.drug_id)
            if not drug:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Drug with id {item.drug_id} not found"
                )
            
            # Check inventory availability BEFORE creating order
            inventory = await self.repository.get_inventory_by_branch_and_drug(
                order_data.branch_id,
                item.drug_id,
                item.drug_variant_id
            )
            
            if not inventory:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Inventory not found for drug_id {item.drug_id} in branch {order_data.branch_id}"
                )
            
            if inventory.quantity < item.qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Yetarli emas! Drug_id {item.drug_id} uchun omborda {inventory.quantity} ta bor, talab qilingan: {item.qty} ta"
                )
            
            # Use variant price if available, otherwise use drug base price
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

        # 3. Generate unique order number and barcode
        order_number = await self.generate_unique_order_number()
        barcode = order_number  # barcode same as order_number

        # 4. Create order
        new_order = Order(
            order_number=order_number,
            barcode=barcode,
            branch_id=order_data.branch_id,
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=total_amount
        )

        order = await self.repository.create_order(new_order)

        # 5. Create order items
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

        # 6. Commit transaction
        await self.session.commit()
        await self.session.refresh(order)

        # 7. Return response
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
        
        # 1. Find order by barcode
        order = await self.repository.get_order_by_barcode(barcode)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with barcode '{barcode}' not found"
            )

        # 2. Check if already confirmed
        if order.status == OrderStatus.CONFIRMED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order has already been confirmed"
            )

        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order has been cancelled"
            )

        # 3. Process each order item
        for item in order.items:
            # Get inventory (with variant support)
            inventory = await self.repository.get_inventory_by_branch_and_drug(
                order.branch_id, 
                item.drug_id,
                getattr(item, 'drug_variant_id', None)
            )

            if not inventory:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Inventory not found for drug_id {item.drug_id} in branch {order.branch_id}"
                )

            # Check quantity availability
            if inventory.quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient quantity for drug_id {item.drug_id}. Available: {inventory.quantity}, Required: {item.quantity}"
                )

            # Reduce inventory quantity
            new_quantity = inventory.quantity - item.quantity
            await self.repository.update_inventory_quantity(inventory, new_quantity)

        # 4. Update order status to confirmed
        order.status = OrderStatus.CONFIRMED
        order.confirmed_at = datetime.now(timezone.utc)
        await self.repository.update_order_status(order, OrderStatus.CONFIRMED)

        # 5. Commit transaction
        await self.session.commit()
        await self.session.refresh(order)

        # 6. Return response
        return OrderScanResponse(
            id=order.id,
            order_number=order.order_number,
            barcode=order.barcode,
            status=order.status,
            total_amount=order.total_amount,
            confirmed_at=order.confirmed_at,
            message="Order confirmed successfully"
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