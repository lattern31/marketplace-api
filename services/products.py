from fastapi import HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from models.products import Product
from repositories.products import IProductRepository


async def product_exists(
    repository: IProductRepository,
    session: AsyncSession,
    product_name: str,
) -> None:
    if not await repository.check_exists_by_name(
            session=session, name=product_name):
        error_msg = "product doesn't exist"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )


async def create_product(
    repository: IProductRepository,
    session: AsyncSession,
    name: str,
    cost: int,
) -> Product:
    if await repository.check_exists_by_name(
        session=session, name=name
    ):
        error_msg = 'name already taken'
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    product = await repository.create(
        session, name=name, cost=cost)
    return product
