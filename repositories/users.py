from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User


class IUserRepository(Protocol):
    async def create(self, session: AsyncSession, username: str) -> User:
        ...

    async def fetch(self, session: AsyncSession, username: str) -> list[User]:
        ...

    async def check_exists_by_username(self, session: AsyncSession, username: str) -> bool:
        ...

    async def check_exists_by_id(self, session: AsyncSession, id: int) -> bool:
        ...


class SQLAUserRepository:
    async def create(self, session: AsyncSession, username: str) -> User:
        user = User(username=username)
        session.add(user)
        await session.commit()
        return user

    async def fetch(self, session: AsyncSession, username: str | None = None) -> list[User]:
        stmt = select(User)
        if username is not None:
            stmt = stmt.where(User.username.like(f"%{username}%"))

        results = (await session.execute(stmt)).scalars().all()
        return results

    async def check_exists_by_username(self, session: AsyncSession, username: str) -> bool:
        stmt = select(User).where(User.username == username)

        response = await session.execute(stmt)
        return response.one_or_none() is not None

    async def check_exists_by_id(self, session: AsyncSession, id: int) -> bool:
        stmt = select(User).where(User.id == id)

        response = await session.execute(stmt)
        return response.one_or_none() is not None
