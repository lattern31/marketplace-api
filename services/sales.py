from fastapi import HTTPException, status
from sqlaclhemy.ext.asyncio import AsyncSession
from repositories.orders import IOrderRepository


async def get_seller_sale(
        order_repository: IOrderRepository,
        session: AsyncSession,
        seller_id: int,
        order_id: int
    ) -> Order | None:
    order = await order_repository.get_seller_order(
        session, seller_id, order_id)
    if order is None or order.content == []:
        error_msg = "order doesn't exist or you don't have enough rights"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    return order


async def get_seller_sales(
        order_repository: IOrderRepository,
        session: AsyncSession,
        seller_id: int
    ) -> list[Order]:
    orders = await order_repository.get_seller_orders(session, seller_id)
    return orders
