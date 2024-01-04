from typing import Protocol

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.orders import Order, OrdersProducts, OrderStatus


class IOrderRepository(Protocol):
    async def create(
        self, session: AsyncSession, owner_id: int, 
        status: OrderStatus = OrderStatus.PENDING
    ) -> Order:
        ...

    async def get_one(
        self, session: AsyncSession, order_id: int
    ) -> Order:
        ...

    async def status_update(
        self, session: AsyncSession, status: OrderStatus
    ):
        ...

    async def add_product(
        self, session: AsyncSession, order_id: int,
        product_id: int, quantity: int
    ):
        ...

    async def check_exists_by_id(self, session: AsyncSession, id: int) -> bool:
        ...


class SQLAOrderRepository:
    async def create(
        self, session: AsyncSession, user_id: int, 
        status: OrderStatus = OrderStatus.PENDING
    ) -> int:
        order = Order(user_id=user_id, status=status)
        session.add(order)
        await session.commit()
        return order.id
        
    async def get_one(
        self, session: AsyncSession, order_id: int
    ) -> Order | None:
        stmt = select(Order).where(Order.id == order_id).options(
            selectinload(Order.content).selectinload(OrdersProducts.product)
        )
        order = (await session.execute(stmt)).scalars().one_or_none()

        return order

    async def status_update(
        self, session: AsyncSession, id: int, status: OrderStatus
    ) -> Order:
        ...

    async def add_product(
        self, session: AsyncSession, order_id: int, 
        product_name: str, quantity: int
    ):
        sel_stmt = select(OrdersProducts).where(
            OrdersProducts.order_id == order_id,
            OrdersProducts.product_name == product_name
        )
        row_in_db = (await session.execute(sel_stmt)).scalars().one_or_none()
        if row_in_db is not None:  # update row
            await session.execute(update(OrdersProducts), [
                {"order_id": row_in_db.order_id,
                 "product_name": row_in_db.product_name,
                 "quantity": row_in_db.quantity + quantity}
            ])
        else:  # new row
            row = OrdersProducts(
                order_id=order_id, 
                product_name=product_name, 
                quantity=quantity
            )
            session.add(row)
        await session.commit()

    async def check_exists_by_id(self, session: AsyncSession, id: int) -> bool:
        stmt = select(Order).where(Order.id == id)

        response = await session.execute(stmt)
        return response.one_or_none() is not None
        
