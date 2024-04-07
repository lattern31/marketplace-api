from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.cart import ICartRepository
from repositories.products import IProductRepository
from models.users import User
from models.cart import Cart
from services.products import check_product_exists


async def get_cart(
    session: AsyncSession,
    cart_repository: ICartRepository,
    user_id: int,
) -> Cart:
    return (await cart_repository.get_content(session, user_id))


async def add_item_to_cart(
    session: AsyncSession,
    cart_repository: ICartRepository,
    product_repository: IProductRepository,
    user_id: int,
    product_id: int,
) -> None:
    await check_product_exists(session, product_repository, product_id)
    await cart_repository.add_item(session, user_id, product_id)


async def remove_item_from_cart(
    session: AsyncSession,
    cart_repository: ICartRepository,
    user_id: int,
    product_id: int,
) -> None:
    if not await cart_repository.is_product_in_cart(
        session=session, user_id=user_id, product_id=product_id):
        error_msg = "product is not in cart"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    await cart_repository.remove_item(session, user_id, product_id)
