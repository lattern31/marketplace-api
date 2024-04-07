from typing import Protocol

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.cart import Cart
from models.products import ProductInOrder


class ICartRepository(Protocol):
    async def get_content(self, session: AsyncSession,
                          user_id: int) -> list[ProductInOrder]:
        ...

    async def add_item(self, session: AsyncSession,
                       user_id: int, product_id: int) -> None:
        ...

    async def remove_item(self, session: AsyncSession,
                          user_id: int, product_id: int) -> None:
        ...

    async def clear_all(self, session: AsyncSession,
                        user_id: int) -> None:
        ...

    async def is_product_in_cart(self, session, AsyncSession,
                                 user_id: int, product_id: int) -> bool:
        ...

class SQLACartRepository:
    async def get_content(self, session: AsyncSession,
                          user_id: int) -> list[ProductInOrder]:
        stmt = select(Cart).where(Cart.user_id == user_id).options(
                selectinload(Cart.product))
        response = await session.execute(stmt)
        return response.scalars().all()

    async def add_item(self, session: AsyncSession,
                       user_id: int, product_id: int) -> None:
        stmt = select(Cart).where(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        )
        cart = (await session.execute(stmt)).scalar_one_or_none()
        if cart:
            cart.quantity += 1
            session.add(cart)
        else:
            session.add(Cart(user_id=user_id, product_id=product_id,
                             quantity=1))
        await session.commit()

    async def remove_item(self, session: AsyncSession,
                          user_id: int, product_id: int) -> None:
        stmt = delete(Cart).where(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        )
        await session.execute(stmt)
        await session.commit()

    async def clear_all(self, session: AsyncSession,
                        user_id: int) -> None:
        stmt = delete(Cart).where(Cart.user_id == user_id)
        await session.execute(stmt)
        await session.commit()

    async def is_product_in_cart(self, session: AsyncSession,
                                 user_id: int, product_id: int) -> bool:
        stmt = select(Cart).where(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        )
        if (await session.execute(stmt)).scalar_one_or_none() is None:
            return False
        return True
