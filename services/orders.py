from fastapi import HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from models.orders import Order
from repositories.orders import IOrderRepository
from repositories.users import IUserRepository
from repositories.products import IProductRepository
from services.users import user_exists
from services.products import product_exists


async def create_order(
    order_repository: IOrderRepository,
    user_repository: IUserRepository,
    session: AsyncSession,
    user_id: int,
) -> int:
    await user_exists(user_repository, session, user_id)
    order_id = await order_repository.create(session, user_id)
    return order_id

async def add_item_to_order(
    order_repository: IOrderRepository,
    product_repository: IProductRepository,
    session: AsyncSession,
    order_id: int,
    product_name: str,
    quantity: int,
) -> None:
    if not await order_repository.check_exists_by_id(
        session, order_id
    ):
        error_msg = "order doesn't exist"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )
    if not await product_repository.check_exists_by_name(
        session, product_name
    ):
        error_msg = "product doesn't exist"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=error_msg
        )
    if quantity <= 0:
        error_msg = "quantity can't be less than or equal to 0"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=error_msg
        )

    await order_repository.add_product(
        session, order_id, product_name, quantity)

