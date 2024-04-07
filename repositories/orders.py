from typing import Protocol

from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.orders import Order, OrdersProducts, OrderStatus
from models.products import Product, ProductInOrder, ProductStatus


class IOrderRepository(Protocol):
    async def create(
        self, session: AsyncSession, owner_id: int,
        content: list[ProductInOrder]
    ) -> int:
        ...

    async def get_user_order(
        self, session: AsyncSession, order_id: int
    ) -> Order | None:
        ...

    async def get_user_orders(
        self, session: AsyncSession, user_id: int
    ) -> list[Order]:
        ...

    async def get_product_in_seller_order(
        self, session: AsyncSession, seller_id: int,
        order_id: int, product_id: int
    ) -> OrdersProducts | None:
        ...

    async def get_seller_order(
        self, session: AsyncSession, seller_id: int, order_id: int
    ) -> Order | None:
        ...

    async def get_seller_orders(
        self, session: AsyncSession, seller_id: int
    ) -> list[Order]:
        ...

    async def update_status(
        self, session: AsyncSession, order_id: int, status: OrderStatus
    ) -> None:
        ...

    async def update_product_status(
        self, session: AsyncSession, seller_id: int,
        order_id: int, product_id: int, status: ProductStatus
    ) -> None:
        ...

    async def is_status_actual(
        self, session: AsyncSession, order_id: int
    ) -> bool:
        ...

    async def is_seller_product_owner(
        self, session: AsyncSession, seller_id: int,
        order_id: int, product_id: int
    ) -> bool:
        ...

    async def is_product_in_order(
        self, session: AsyncSession, order_id: int, product_id: int
    ) -> bool:
        ...

    async def check_exists_by_id(
        self, session: AsyncSession, order_id: int
    ) -> bool:
        ...


class SQLAOrderRepository:
    async def create(
        self, session: AsyncSession, owner_id: int,
        content: list[ProductInOrder]
    ) -> int:
        order = Order(owner_id=owner_id, status=OrderStatus.OPENED)
        session.add(order)
        await session.commit()
        for item in content:
            item_obj = OrdersProducts(
                product_id=item.product_id,
                order_id=order.id,
                quantity=item.quantity,
                status=ProductStatus.PENDING
            )
            session.add(item_obj)
        await session.commit()
        return order.id

    async def get_user_order(
        self, session: AsyncSession, order_id: int
    ) -> Order | None:
        stmt = select(Order).where(Order.id == order_id).options(
            selectinload(Order.content).selectinload(OrdersProducts.product)
        )
        response = await session.execute(stmt)
        return response.scalars().one_or_none()

    async def get_user_orders(
        self, session: AsyncSession, customer_id: int
    ) -> list[Order]:
        stmt = select(Order).where(Order.owner_id == customer_id).options(
            selectinload(Order.content).selectinload(OrdersProducts.product)
        )
        response = await session.execute(stmt)
        return response.scalars().all()

    async def get_product_in_seller_order(
        self, session: AsyncSession, seller_id: int,
        order_id: int, product_id: int
    ) -> OrdersProducts | None:
        stmt = select(OrdersProducts).where(
            OrdersProducts.order_id == order_id,
            OrdersProducts.product_id == product_id
            ).options(selectinload(OrdersProducts.product))
        response = await session.execute(stmt)
        product = response.scalars().one_or_none()
        if product is not None and product.seller_id == seller_id:
            return product


    async def get_seller_order(
        self, session: AsyncSession, seller_id: int, order_id: int
    ) -> Order | None:
        stmt = select(Order).where(Order.id == order_id).options(
            selectinload(Order.content).
            selectinload(OrdersProducts.product)
        )
        response = await session.execute(stmt)
        order = response.scalars().one_or_none()
        if order is not None:
            for item in order.content:
                if item.seller_id != seller_id:
                    order.content.remove(item)
        return order

    async def get_seller_orders(
        self, session: AsyncSession, seller_id: int
    ) -> list[Order]:
        order_ids = select(OrdersProducts.order_id).options(
                selectinload(OrdersProducts.product)
                ).where(OrdersProducts.seller_id == seller_id)
        stmt = select(Order).where(Order.id.in_(order_ids)).options(
            selectinload(Order.content).
            selectinload(OrdersProducts.product)
        )
        response = await session.execute(stmt)
        orders = response.scalars().all()
        for order in orders:
            for item in order.content:
                if item.seller_id != seller_id:
                    order.content.remove(item)
        return orders

    async def update_status(
        self, session: AsyncSession, order_id: int,
        status: OrderStatus
    ) -> None:
        stmt = update(Order).where(Order.id == order_id).values(status=status)
        await session.execute(stmt)
        await session.commit()

    async def update_product_status(
        self, session: AsyncSession,
        order_id: int, product_id: int, status: ProductStatus
    ) -> None:
        stmt = update(OrdersProducts).where(
            OrdersProducts.order_id == order_id,
            OrdersProducts.product_id == product_id
        ).values(status=status)
        await session.execute(stmt)
        await session.commit()

    async def update_content_status(
        self, session: AsyncSession,
        order_id: int, status: ProductStatus
    ) -> None:
        stmt = update(OrdersProducts).where(
            OrdersProducts.order_id == order_id
        ).values(status=status)
        await session.execute(stmt)
        await session.commit()

    async def is_seller_product_owner(
        self, session: AsyncSession, seller_id: int,
        order_id: int, product_id: int
    ) -> bool:
        stmt = select(OrdersProducts).where(
            OrdersProducts.order_id == order_id,
            OrdersProducts.product_id == product_id
        ).options(selectinload(OrdersProducts.product))
        response = await session.execute(stmt)
        return response.product.seller_id == seller_id

    async def is_product_in_order(
        self, session: AsyncSession, order_id: int, product_id: int
    ) -> bool:
        stmt = select(OrdersProducts).where(
            OrdersProducts.order_id == order_id,
            OrdersProducts.product_id == product_id
        )
        response = await session.execute(stmt)
        return response.scalars().one_or_none() is not None

    async def check_exists_by_id(
        self, session: AsyncSession, id: int
    ) -> bool:
        stmt = select(Order).where(Order.id == id)
        response = await session.execute(stmt)
        return response.one_or_none() is not None
