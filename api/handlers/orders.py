from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import (get_async_session, get_order_repository,
                      get_user_repository, get_product_repository)
from api.schemas.orders import (OrderAddItemSchema, OrderCreateSchema,
                                OrderCreateResponseSchema, OrderResponseSchema)
from repositories.orders import IOrderRepository
from repositories.users import IUserRepository
from repositories.products import IProductRepository
from services.orders import create_order, add_item_to_order


router = APIRouter()


@router.post(
    '',
    response_model=OrderCreateResponseSchema,
    operation_id='createOrder',
    summary='Create order',
)
async def create_order_handler(
    order_create_schema: OrderCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    order_repository: IOrderRepository = Depends(get_order_repository),
    user_repository: IUserRepository = Depends(get_user_repository),
):
    order_id = await create_order(
        order_repository, user_repository,
        session, order_create_schema.user_id)
    return OrderCreateResponseSchema(id=order_id)


@router.get(
    '/{order_id}',
    response_model=OrderResponseSchema,
    operation_id='getOrder',
    summary='Get Order',
)
async def get_order_handler(
    order_id: int,
    session: AsyncSession = Depends(get_async_session),
    order_repository: IOrderRepository = Depends(get_order_repository),
):
    response = await order_repository.get_one(
        session=session,
        order_id=order_id,
    )

    if response is None:
        error_msg = "order doesn't exist"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=error_msg)
    return response


@router.post(
    '/{order_id}/add_item',
    operation_id='addItemToOrder',
    summary='Add item to order',
)
async def add_item_handler(
    order_id: int,
    order_add_item_schema: OrderAddItemSchema,
    session: AsyncSession = Depends(get_async_session),
    order_repository: IOrderRepository = Depends(get_order_repository),
    product_repository: IProductRepository = Depends(get_product_repository),
):
    await add_item_to_order(
        order_repository, product_repository, session,
        order_id=order_id, **order_add_item_schema.model_dump())
