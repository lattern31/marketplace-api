from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserRole


class IUserRepository(Protocol):
    async def create(self, session: AsyncSession,
                     username: str, hashed_password: str,
                     role: UserRole) -> int:
        ...

    async def get_by_email(self, session: AsyncSession,
                           email: str) -> User:
        ...

    async def fetch(self, session: AsyncSession,
                    username: str) -> list[User]:
        ...

    async def check_exists_by_username(self, session: AsyncSession,
                                       username: str) -> bool:
        ...

    async def check_exists_by_id(self, session: AsyncSession,
                                 user_id: int) -> bool:
        ...

    async def has_role(self, session: AsyncSession,
                       user_id: int, user_role: UserRole) -> bool:
        ...


class SQLAUserRepository:
    async def create(self, session: AsyncSession,
                     username: str, hashed_password: str, role: UserRole) -> int:
        user = User(
            username=username,
            hashed_password=hashed_password,
            role=role
        )
        session.add(user)
        await session.commit()
        return user.id

    async def get_by_email(self, session: AsyncSession,
                           email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        response = await session.execute(stmt)
        return response.one_or_none()

    async def get_by_username(self, session: AsyncSession,
                              username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        response = await session.execute(stmt)
        return response.scalar_one_or_none()

    async def fetch(self, session: AsyncSession,
                    username: str | None = None) -> list[User]:
        stmt = select(User)
        if username is not None:
            stmt = stmt.where(User.username.like(f"%{username}%"))

        results = (await session.execute(stmt)).scalars().all()
        return results

    async def check_exists_by_username(self, session: AsyncSession,
                                       username: str) -> bool:
        stmt = select(User).where(User.username == username)

        response = await session.execute(stmt)
        return response.one_or_none() is not None

    async def check_exists_by_id(self, session: AsyncSession,
                                 user_id: int) -> bool:
        stmt = select(User).where(User.id == user_id)

        response = await session.execute(stmt)
        return response.one_or_none() is not None

    async def has_role(self, session: AsyncSession,
                       user_id: int, user_role: UserRole) -> bool:
        stmt = select(User).where(User.id == user_id, User.role == user_role)
        response = await session.execute(stmt)
        return response.one_or_none() is not None
