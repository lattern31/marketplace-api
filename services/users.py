from fastapi import HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from repositories.users import IUserRepository


async def create_user(
    repository: IUserRepository,
    session: AsyncSession,
    username: str,
) -> User:
    await is_valid_username(repository, session, username)
    user = await repository.create(session, username)
    return user


async def user_exists(
    repository: IUserRepository,
    session: AsyncSession,
    id: int,
) -> None:
    if not await repository.check_exists_by_id(
        session=session, user_id=id
    ):
        error_msg = "user doesn't exist"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )


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
