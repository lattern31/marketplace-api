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
    owner_id: int,
) -> int:
    await user_exists(user_repository, session, owner_id)
    order_id = await order_repository.create(session, owner_id)
    return order_id


async def add_item_to_order(
    order_repository: IOrderRepository,
    product_repository: IProductRepository,
    session: AsyncSession,
    order_id: int,
    product_id: int,
    quantity: int,
) -> None:
    await order_exists(order_repository, session, order_id)
    await product_exists(product_repository, session, product_id)
    is_valid_quantity(quantity)

    await order_repository.add_product(session, order_id,
                                       product_id, quantity)


async def delete_item_from_order(
    order_repository: IOrderRepository,
    product_repository: IProductRepository,
    session: AsyncSession,
    order_id: int,
    product_id: int,
) -> None:
    await order_exists(order_repository, session, order_id)
    await product_exists(product_repository, session, product_id)
    await is_product_in_order(order_repository, session,
                              order_id, product_id)
    await order_repository.delete_product(session, order_id, product_id)


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
    product_id: int,
) -> None:
    if not await order_repository.is_product_in_order(session,
                                                      order_id,
                                                      product_id):
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
