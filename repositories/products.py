from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.products import Product


class IProductRepository(Protocol):
    async def create(self, session: AsyncSession,
                     title: str, seller_id: int, cost: int) -> int:
        ...

    async def get_one(self, session: AsyncSession,
                      product_id: int) -> Product:
        ...

    async def get_all(self, session: AsyncSession) -> list[Product]:
        ...

    async def get_seller_products(self, session: AsyncSession,
                                  seller_id: int) -> list[Product]:
        ...


class SQLAProductRepository:
    async def create(self, session: AsyncSession,
                     title: str, seller_id: int, cost: int) -> int:
        product = Product(title=title, seller_id=seller_id, cost=cost)
        session.add(product)
        await session.commit()
        return product.id

    async def get_all(self, session: AsyncSession) -> Product | None:
        return (await session.execute(select(Product))).scalars().all()

    async def get_one(self, session: AsyncSession,
                      product_id: int) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        response = await session.execute(stmt)
        return response.scalars().one_or_none()

    async def get_seller_products(self, session: AsyncSession,
                                  seller_id: int) -> list[Product]:
        stmt = select(Product).where(Product.seller_id == seller_id)
        return (await session.execute(stmt)).scalars().all()

    async def check_exists_by_id(self, session: AsyncSession,
                                 id: int) -> bool:
        stmt = select(Product).where(Product.id == id)
        response = await session.execute(stmt)
        return response.one_or_none() is not None
