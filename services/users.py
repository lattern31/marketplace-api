from fastapi import HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserRole
from repositories.users import IUserRepository
from services.auth import get_password_hash


async def create_user(
    repository: IUserRepository,
    session: AsyncSession,
    username: str,
    password: str,
    role: UserRole,
) -> User:
    await is_valid_username(repository, session, username)
    user = await repository.create(
        session, username, get_password_hash(password), role
    )
    return user


async def user_exists(
    user_repository: IUserRepository,
    session: AsyncSession,
    user_id: int,
) -> None:
    if not await user_repository.check_exists_by_id(session, user_id):
        error_msg = "user doesn't exist"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )

async def user_has_role(
    user_repository: IUserRepository,
    session: AsyncSession,
    user_id: int,
    user_role: UserRole
) -> bool:
    return (await user_repository.has_role(session, user_id, user_role))

async def is_valid_username(
    repository: IUserRepository,
    session: AsyncSession,
    username: str,
) -> None:
    if await repository.check_exists_by_username(
        session=session, username=username
    ):
        error_msg = 'username already taken'
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
