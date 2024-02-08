from fastapi import Depends, Query
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_async_session, get_user_repository
from api.schemas.users import (UserCreateSchema,
                               UserCreateResponseSchema,
                               UserResponseSchema)
from repositories.users import IUserRepository
from services.users import create_user


router = APIRouter()


@router.post(
    '',
    response_model=UserCreateResponseSchema,
    operation_id='createUser',
    summary='Create user',
)
async def create_user_handler(
    user_create_schema: UserCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    user_repository: IUserRepository = Depends(get_user_repository),
):
    user_id = await create_user(
        user_repository,
        session,
        username=user_create_schema.username,
    )
    return {'id': user_id}


@router.get(
    '',
    response_model=list[UserResponseSchema],
    operation_id='fetchUsers',
    summary='Fetch users',
)
async def fetch_users_handler(
    session: AsyncSession = Depends(get_async_session),
    user_repository: IUserRepository = Depends(get_user_repository),
    username: str = Query(
        default=None,
        description="Search by username",
    )
):
    response = await user_repository.fetch(
        session=session,
        username=username,
    )
    return response
