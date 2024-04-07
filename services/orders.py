from fastapi import HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from models.products import ProductStatus
from models.orders import OrderStatus, Order
from repositories.cart import ICartRepository
from repositories.orders import IOrderRepository
from repositories.users import IUserRepository
from repositories.products import IProductRepository
from services.users import user_exists
from services.products import check_product_exists


async def create_order(
    session: AsyncSession,
    order_repository: IOrderRepository,
    cart_repository: ICartRepository,
    user_id: int,
) -> int:
    content = await cart_repository.get_content(session, user_id)
    if not content:
        error_msg = "empty cart"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    order_id = await order_repository.create(session, user_id, content)
    await cart_repository.clear_all(session, user_id)
    return order_id


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
    if not await order_repository.is_product_in_order(
        session, order_id, product_id):
        error_msg = "product is not in order"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )


def is_valid_quantity(quantity: int) -> None:
    if quantity <= 0:
        error_msg = "quantity can't be less than or equal to 0"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


async def get_seller_sale(
        order_repository: IOrderRepository, session: AsyncSession,
        seller_id: int, order_id: int
    ):
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
):
    sales = await order_repository.get_seller_orders(session, seller_id)
    return sales


async def get_seller_sale_product(
    orders_repository: IOrderRepository,
    session: AsyncSession,
    seller_id: int,
    order_id: int,
    product_id: int,
):
    product = await orders_repository.get_product_in_seller_order(
            session, seller_id, order_id, product_id)
    if product is None:
        error_msg = "product doesn't exist in that order or you don't have enough rights"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    return product


async def update_product_status(
    orders_repository: IOrderRepository,
    session: AsyncSession,
    seller_id: int,
    order_id: int,
    product_id: int,
    status: ProductStatus,
):
    product = await get_seller_sale_product(
        orders_repository, session, seller_id, order_id, product_id)
    await orders_repository.update_product_status(session, order_id,
                                                  product_id, status)
    await auto_status_updater(orders_repository, session, order_id)


async def auto_status_updater(
    orders_repository: IOrderRepository,
    session: AsyncSession,
    order_id: int,
) -> None:
    order = await orders_repository.get_user_order(session, order_id)
    order_status = order.status
    received = [product.status == ProductStatus.RECEIVED for product in order.content]
    if order_status == OrderStatus.OPENED and all(received):
        orders_repository.update_status(session, order_id, OrderStatus.CLOSED)
    if order_status == OrderStatus.CANCELLED:
        order_reposiotry.update_content_status(
            session, order_id, ProductStatus.CANCELLED)


def calc_total_cost(order: Order) -> int:
    return sum([product.cost * product.quantity for product in order.content])
    

async def payment_service(
    orders_repository: IOrderRepository,
    session: AsyncSession,
    order_id: int,
) -> bool:
    order = await orders_repository.get_user_order(session, order_id)
    total_cost = cals_total_cost(order)
    print(order_total_cost)
    #  request to payment service
    return True
    

def delivery_service() -> bool:
    return True
