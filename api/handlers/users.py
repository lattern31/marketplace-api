from fastapi import Depends, Query
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_async_session, get_user_repository
from api.schemas.users import UserResponseSchema
from repositories.users import IUserRepository
from services.auth import get_current_active_user
from models.users import User


router = APIRouter(prefix='', tags=['users'])


@router.get('')
async def get_my_profile(
    session: AsyncSession = Depends(get_async_session),
    user_repository: IUserRepository = Depends(get_user_repository),
    current_user: User = Depends(get_current_active_user())
) -> UserResponseSchema:
    return current_user
