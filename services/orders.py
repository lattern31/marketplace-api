from fastapi import HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

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
    await order_exists(order_repository, session, order_id)
    await product_exists(product_repository, session, product_name)
    is_valid_quantity(quantity)

    await order_repository.add_product(session, order_id,
                                       product_name, quantity)


async def delete_item_from_order(
    order_repository: IOrderRepository,
    product_repository: IProductRepository,
    session: AsyncSession,
    order_id: int,
    product_name: str,
) -> None:
    await order_exists(order_repository, session, order_id)
    await product_exists(product_repository, session, product_name)
    await is_product_in_order(order_repository, session,
                              order_id, product_name)
    await order_repository.delete_product(session, order_id, product_name)


async def order_exists(
    order_repository: IOrderRepository,
    session: AsyncSession,
    order_id: int,
) -> None:
    if not await order_repository.check_exists_by_id(session, order_id):
        error_msg = "order doesn't exist"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )


async def is_product_in_order(
    order_repository: IOrderRepository,
    session: AsyncSession,
    order_id: int,
    product_name: str,
) -> None:
    if not await order_repository.is_product_in_order(session,
                                                      order_id,
                                                      product_name):
        error_msg = "product is not in order"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )


def is_valid_quantity(quantity) -> None:
    if quantity <= 0:
        error_msg = "quantity can't be less than or equal to 0"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
