from fastapi import HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.products import IProductRepository


async def product_exists(repository: IProductRepository,
                         session: AsyncSession,
                         product_id: int) -> None:
    if not await repository.check_exists_by_id(
            session=session, id=product_id):
        error_msg = "product doesn't exist"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )


async def create_product(repository: IProductRepository,
                         session: AsyncSession,
                         title: str,
                         cost: int) -> int:
    product_id = await repository.create(session, title, cost)
    return product_id
