from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import (get_async_session, get_order_repository,
                      get_cart_repository, get_product_repository)
from api.schemas.orders import (OrderCreateResponseSchema,
                                UserOrderResponseSchema)
from repositories.orders import IOrderRepository
from repositories.products import IProductRepository
from repositories.cart import ICartRepository
from models.users import User, UserRole
from models.orders import OrderStatus
from services.orders import create_order
from services.auth import get_current_active_user


router = APIRouter(prefix='/orders', tags=['orders'])


@router.get('')
async def get_my_orders_handler(
    session: AsyncSession = Depends(get_async_session),
    order_repository: IOrderRepository = Depends(get_order_repository),
    current_user: User = Depends(get_current_active_user(
        required_roles=[UserRole.CUSTOMER])
    ),
) -> list[UserOrderResponseSchema]:
    orders = await order_repository.get_user_orders(session, current_user.id)
    return orders


@router.post('')
async def create_order_handler(
    session: AsyncSession = Depends(get_async_session),
    order_repository: IOrderRepository = Depends(get_order_repository),
    cart_repository: ICartRepository = Depends(get_cart_repository),
    current_user: User = Depends(
        get_current_active_user(required_roles=[UserRole.CUSTOMER])
    ),
) -> OrderCreateResponseSchema:
    order_id = await create_order(
        session, order_repository, cart_repository, current_user.id)
    return OrderCreateResponseSchema(id=order_id)


@router.get('/{order_id}')
async def get_order_handler(
    order_id: int,
    session: AsyncSession = Depends(get_async_session),
    order_repository: IOrderRepository = Depends(get_order_repository),
    current_user: User = Depends(
        get_current_active_user(required_roles=[UserRole.CUSTOMER])
    ),
) -> UserOrderResponseSchema:
    order = await order_repository.get_user_order(
        session=session, order_id=order_id
    )

    if order.owner_id != current_user.id:
        error_msg = "forbidden"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=error_msg)
    if order is None:
        error_msg = "order doesn't exist"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=error_msg)
    return order
