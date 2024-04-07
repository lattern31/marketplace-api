from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import (get_async_session, get_product_repository,
                      get_order_repository)
from api.schemas.products import (ProductResponseSchema,
                                  ProductInSellerOrderSchema)
from api.schemas.orders import SellerOrderResponseSchema
from api.schemas.sellers import SellerUpdateProductStatusSchema
from models.users import User, UserRole
from models.products import ProductStatus
from repositories.products import IProductRepository
from repositories.orders import IOrderRepository
from services.orders import (get_seller_sale, get_seller_sales,
                             get_seller_sale_product, update_product_status)
from services.auth import get_current_active_user


router = APIRouter(prefix='/sellers', tags=['sellers'])


@router.get('/{seller_id}/products')
async def get_seller_products_handler(
    seller_id: int,
    session: AsyncSession = Depends(get_async_session),
    product_repository: IProductRepository = Depends(get_product_repository),
) -> list[ProductResponseSchema]:
    products = await product_repository.get_seller_products(session, seller_id)
    return products


@router.get('/sales')
async def get_seller_sales_handler(
    session: AsyncSession = Depends(get_async_session),
    order_repository: IOrderRepository = Depends(get_order_repository),
    current_user: User = Depends(
        get_current_active_user(required_roles=[UserRole.SELLER])
    ),
) -> list[SellerOrderResponseSchema]:
    orders = await get_seller_sales(
        order_repository, session, current_user.id)
    return orders


@router.get('/sales/{order_id}')
async def get_seller_sale_handler(
    order_id: int,
    session: AsyncSession = Depends(get_async_session),
    order_repository: IOrderRepository = Depends(get_order_repository),
    current_user: User = Depends(
        get_current_active_user(required_roles=[UserRole.SELLER])
    ),
) -> SellerOrderResponseSchema:
    order = await get_seller_sale(
            order_repository, session, current_user.id, order_id)
    return order


@router.get('/sales/{order_id}/{product_id}')
async def get_seller_sale_product_handler(
    order_id: int,
    product_id: int,
    session: AsyncSession = Depends(get_async_session),
    orders_repository: IOrderRepository = Depends(get_order_repository),
    current_user: User = Depends(get_current_active_user(
        required_roles=[UserRole.SELLER])
    ),
) -> ProductInSellerOrderSchema:
    product = await get_seller_sale_product(orders_repository, session, 
                                            current_user.id, order_id,
                                            product_id)
    return product

@router.patch('/sales/{order_id}/{product_id}')
async def update_product_status_handler(
    order_id: int,
    product_id: int,
    status_schema: SellerUpdateProductStatusSchema,
    session: AsyncSession = Depends(get_async_session),
    orders_repository: IOrderRepository = Depends(get_order_repository),
    current_user: User = Depends(get_current_active_user(
        required_roles=[UserRole.SELLER])
    ),
):
    print(status_schema)
    await update_product_status(orders_repository, session, current_user.id,
                                order_id, product_id, status_schema.status)
