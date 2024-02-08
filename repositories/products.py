from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.products import Product


class IProductRepository(Protocol):
    async def create(self, session: AsyncSession,
                     name: str, cost: int) -> Product:
        ...

    async def fetch(self, session: AsyncSession,
                    name: str) -> list[Product]:
        ...

    async def check_exists_by_name(self, session: AsyncSession,
                                   name: str) -> bool:
        ...


class SQLAProductRepository:
    async def create(self, session: AsyncSession,
                     name: str, cost: int) -> Product:
        product = Product(name=name, cost=cost)
        session.add(product)
        await session.commit()
        return product

    async def fetch(self, session: AsyncSession,
                    name: str | None = None) -> list[Product]:
        stmt = select(Product)
        if name is not None:
            stmt = stmt.where(Product.name.like(f"%{name}%"))

        results = (await session.execute(stmt)).scalars().all()
        return results

    async def check_exists_by_name(self, session: AsyncSession,
                                   name: str) -> bool:
        stmt = select(Product).where(Product.name == name)

        response = await session.execute(stmt)
        return response.one_or_none() is not None
