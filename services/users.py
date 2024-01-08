from fastapi import HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from repositories.users import IUserRepository


async def user_exists(
    repository: IUserRepository,
    session: AsyncSession,
    id: int,
) -> None:
    if not await repository.check_exists_by_id(
        session=session, id=id
    ):
        error_msg = "user doesn't exist"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

async def create_user(
    repository: IUserRepository,
    session: AsyncSession,
    username: str,
) -> User:
    if await repository.check_exists_by_username(
        session=session, username=username
    ):
        error_msg = 'username already taken'
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    user = await repository.create(session, username)
    return user

