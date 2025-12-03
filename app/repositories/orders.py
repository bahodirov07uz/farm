from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List

from app.models.orders import Order, OrderItem, OrderStatus
from app.models import Drug, Inventory, Branch


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, order: Order) -> Order:
        """Create a new order"""
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def create_order_items(self, order_items: List[OrderItem]) -> List[OrderItem]:
        """Create order items in bulk"""
        self.db.add_all(order_items)
        await self.db.flush()
        return order_items

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID with items and drug details"""
        query = (
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.drug),
                selectinload(Order.items).selectinload(OrderItem.drug_variant)
            )
            .where(Order.id == order_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_order_by_barcode(self, barcode: str) -> Optional[Order]:
        """Get order by barcode with items"""
        query = (
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.drug),
                selectinload(Order.items).selectinload(OrderItem.drug_variant)
            )
            .where(Order.barcode == barcode)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """Get order by order number"""
        query = select(Order).where(Order.order_number == order_number)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_order_status(self, order: Order, status: OrderStatus) -> Order:
        """Update order status"""
        order.status = status
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def get_all_orders(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[OrderStatus] = None,
        branch_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> List[Order]:
        """Get all orders with filters"""
        query = select(Order).options(selectinload(Order.items))
        
        if status:
            query = query.where(Order.status == status)
        if branch_id:
            query = query.where(Order.branch_id == branch_id)
        if user_id:
            query = query.where(Order.user_id == user_id)
        
        query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_orders_by_pharmacy(
        self,
        pharmacy_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """Get orders for all branches under a pharmacy"""
        query = (
            select(Order)
            .join(Branch, Order.branch_id == Branch.id)
            .options(selectinload(Order.items))
            .where(Branch.pharmacy_id == pharmacy_id)
        )
        
        if status:
            query = query.where(Order.status == status)
        
        query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_drug_by_id(self, drug_id: int) -> Optional[Drug]:
        """Get drug by ID"""
        query = select(Drug).where(Drug.id == drug_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_branch_by_id(self, branch_id: int) -> Optional[Branch]:
        """Get branch by ID"""
        query = select(Branch).where(Branch.id == branch_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_inventory_by_branch_and_drug(
        self, 
        branch_id: int, 
        drug_id: int,
        drug_variant_id: Optional[int] = None
    ) -> Optional[Inventory]:
        """Get inventory for specific branch and drug (with optional variant)"""
        query = select(Inventory).where(
            Inventory.branch_id == branch_id,
            Inventory.drug_id == drug_id
        )
        if drug_variant_id is not None:
            query = query.where(Inventory.drug_variant_id == drug_variant_id)
        else:
            query = query.where(Inventory.drug_variant_id.is_(None))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_inventory_quantity(
        self, 
        inventory: Inventory, 
        quantity: int
    ) -> Inventory:
        """Update inventory quantity"""
        inventory.quantity = quantity
        await self.db.flush()
        await self.db.refresh(inventory)
        return inventory

    async def check_barcode_exists(self, barcode: str) -> bool:
        """Check if barcode already exists"""
        query = select(func.count(Order.id)).where(Order.barcode == barcode)
        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0

    async def check_order_number_exists(self, order_number: str) -> bool:
        """Check if order number already exists"""
        query = select(func.count(Order.id)).where(Order.order_number == order_number)
        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0