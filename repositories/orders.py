from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.orders import Order, OrdersProducts, OrderStatus


class IOrderRepository(Protocol):
    async def create(
        self, session: AsyncSession, owner_id: int, 
        status: OrderStatus = OrderStatus.PENDING
    ) -> Order:
        ...

    async def get_one(self, session: AsyncSession, order_id: int) -> Order:
        ...

    async def status_update(self, session: AsyncSession, status: OrderStatus):
        ...

    async def add_product(
        self, session: AsyncSession, order_id: int,
        product_id: int, quantity: int
    ):
        ...
    #TODO check_if_exists_by_id


class SQLAOrderRepository:
    async def create(
        self, session: AsyncSession, user_id: int, 
        status: OrderStatus = OrderStatus.PENDING
    ) -> int:
        order = Order(user_id=user_id, status=status)
        session.add(order)
        await session.commit()
        return order.id
        
    async def get_one(self, session: AsyncSession, order_id: int) -> Order | None:
        stmt = select(Order).where(Order.id == order_id
            ).options(selectinload(Order.content).selectinload(OrdersProducts.product))
        order = (await session.execute(stmt)).scalars().one_or_none()

        return order

    async def status_update(
        self, session: AsyncSession, id: int, status: OrderStatus) -> Order:
        ...

    async def add_product(
        self, session: AsyncSession, order_id: int, 
        product_name: str, quantity: int
    ):
        row = OrdersProducts(
            order_id=order_id, 
            product_name=product_name, 
            quantity=quantity
        )
        session.add(row)
        await session.commit()

