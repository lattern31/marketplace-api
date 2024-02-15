from typing import Protocol

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.products import Product


class IProductRepository(Protocol):
    async def create(self, session: AsyncSession,
                     title: str, cost: int) -> int:
        ...

    async def fetch(self, session: AsyncSession,
                    title: str) -> list[Product]:
        ...

    async def check_exists_by_id(self, session: AsyncSession,
                                 id: int) -> bool:
        ...


class SQLAProductRepository:
    async def create(self, session: AsyncSession,
                     title: str, cost: int) -> int:
        stmt = insert(Product).returning(Product.id)
        product_id = await session.execute(stmt, {'title': title,
                                                  'cost': cost})
        await session.commit()
        return product_id.scalar()

    async def fetch(self, session: AsyncSession,
                    title: str | None = None) -> list[Product]:
        stmt = select(Product)
        if title is not None:
            stmt = stmt.where(Product.title.like(f"%{title}%"))

        results = (await session.execute(stmt)).scalars().all()
        return results

    async def check_exists_by_id(self, session: AsyncSession,
                                 id: int) -> bool:
        stmt = select(Product).where(Product.id == id)

        response = await session.execute(stmt)
        return response.one_or_none() is not None
