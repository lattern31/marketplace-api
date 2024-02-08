from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from common.settings import settings


class Base(DeclarativeBase):
    ...


async_engine: AsyncEngine = create_async_engine(
    settings.db_string,
    echo=settings.debug,
)
