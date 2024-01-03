from fastapi import Depends, Query, HTTPException
from fastapi.routing import APIRouter
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_async_session, get_user_repository
from api.schemas.users import UserCreateSchema, UserResponseSchema
from repositories.users import IUserRepository


router = APIRouter(prefix='/users', tags=['users'])

@router.post(
    '/',
    response_model=UserResponseSchema,
    operation_id='createUser',
    summary='Create user',
)
async def create_user_handler(
    user_create_schema: UserCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    user_repository: IUserRepository = Depends(get_user_repository),
):
    if await user_repository.check_exists_by_username(
        session=session, 
        username=user_create_schema.username
    ):
        error_msg = 'username already taken'
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    user = await user_repository.create(
        session,
        username=user_create_schema.username,
    )

    return user

@router.get(
    '/',
    response_model=list[UserResponseSchema],
    operation_id='fetch_users',
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

