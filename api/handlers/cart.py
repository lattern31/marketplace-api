from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import (get_async_session, get_cart_repository, 
                      get_product_repository)
from services.auth import get_current_active_user
from services.cart import (get_cart, add_item_to_cart,
                           remove_item_from_cart)
from api.schemas.cart import CartResponseSchema, CartAddRemoveSchema
from models.users import User, UserRole
from repositories.cart import ICartRepository
from repositories.products import IProductRepository


router = APIRouter(prefix='/cart', tags=['cart'])


@router.get('')
async def get_cart_handler(
    session: AsyncSession = Depends(get_async_session),
    cart_repository: ICartRepository = Depends(get_cart_repository),
    product_repository: IProductRepository = Depends(get_product_repository),
    current_user: User = Depends(
        get_current_active_user(required_roles=[UserRole.CUSTOMER])
    ),
) -> CartResponseSchema:
    cart_content = await get_cart(session, cart_repository, current_user.id)
    return {'content': cart_content}


@router.post('')
async def add_item_to_cart_handler(
    cart_schema: CartAddRemoveSchema,
    session: AsyncSession = Depends(get_async_session),
    cart_repository: ICartRepository = Depends(get_cart_repository),
    product_repository: IProductRepository = Depends(get_product_repository),
    current_user: User = Depends(
        get_current_active_user(required_roles=[UserRole.CUSTOMER])
    ),
) -> None:
    await add_item_to_cart(
        session, cart_repository, product_repository,
        current_user.id, cart_schema.product_id
    )


@router.delete('')
async def remove_item_from_cart_handler(
    product_id: int,
    session: AsyncSession = Depends(get_async_session),
    cart_repository: ICartRepository = Depends(get_cart_repository),
    current_user: User = Depends(
        get_current_active_user(required_roles=[UserRole.CUSTOMER])
    ),
) -> None:
    await remove_item_from_cart(
        session, cart_repository,
        current_user.id, product_id
    )
