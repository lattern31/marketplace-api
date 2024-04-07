from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.db import async_engine
from repositories.orders import SQLAOrderRepository
from repositories.products import SQLAProductRepository
from repositories.users import SQLAUserRepository
from repositories.cart import SQLACartRepository


async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()


def get_user_repository():
    return SQLAUserRepository()


def get_product_repository():
    return SQLAProductRepository()


def get_order_repository():
    return SQLAOrderRepository()


def get_cart_repository():
    return SQLACartRepository()
