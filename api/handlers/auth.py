from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.users import (Token, UserCreateSchema,
                               UserCreateResponseSchema)
from api.deps import get_async_session, get_user_repository
from repositories.users import IUserRepository
from services.auth import create_access_token, authenticate_user
from common.settings import settings
from services.users import create_user


router = APIRouter(tags=['auth'])


@router.post('/login')
async def login_for_auth_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
    user_repository: IUserRepository = Depends(get_user_repository),
) -> Token:
    user = await authenticate_user(user_repository, session,
                             form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post('/register')
async def register_user(
    user_create_schema: UserCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    user_repository: IUserRepository = Depends(get_user_repository),
) -> UserCreateResponseSchema:
    user_id = await create_user(
        user_repository,
        session,
        username=user_create_schema.username,
        password=user_create_schema.password,
        role=user_create_schema.role,
    )
    return UserCreateResponseSchema(id=user_id)
