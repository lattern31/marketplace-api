from fastapi import Depends, HTTPException, Query
from fastapi.routing import APIRouter
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_async_session, get_order_repository, get_user_repository
from api.schemas.orders import OrderAddItemSchema, OrderCreateSchema, OrderCreateResponseSchema, OrderResponseSchema
from repositories.orders import IOrderRepository
from repositories.users import IUserRepository


router = APIRouter(prefix='/orders', tags=['orders'])

@router.post(
    '/',
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
    if not await user_repository.check_exists_by_id(
        session=session, 
        id=order_create_schema.user_id
    ):
        error_msg = "user doesn't exist"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    order_id = await order_repository.create(
        session,
        user_id=order_create_schema.user_id,
    )

    return OrderCreateResponseSchema(id=order_id)

@router.get(
    '/',
    response_model=OrderResponseSchema,
    operation_id='get order',
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)

    return response

@router.post(
    '/add_item',
    response_model=OrderResponseSchema,
    operation_id='add item to order',
    summary='Add item to order',
)
async def add_item_handler(
    order_add_item_schema: OrderAddItemSchema,
    session: AsyncSession = Depends(get_async_session),
    order_repository: IOrderRepository = Depends(get_order_repository),
):
    await order_repository.add_product(
        session=session,
        **order_add_item_schema.dict(),
    )
    resp = await order_repository.get_one(
        session=session, order_id=order_add_item_schema.order_id)

    return resp

