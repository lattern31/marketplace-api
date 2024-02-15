from fastapi import Depends, Query
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_async_session, get_product_repository
from api.schemas.products import (ProductCreateSchema,
                                  ProductCreateResponseSchema,
                                  ProductResponseSchema)
from repositories.products import IProductRepository
from services.products import create_product


router = APIRouter()


@router.post(
    '',
    response_model=ProductCreateResponseSchema,
    operation_id='createProduct',
    summary='Create Product',
)
async def create_product_handler(
    product_create_schema: ProductCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    product_repository: IProductRepository = Depends(get_product_repository),
):
    product_id = await create_product(product_repository, session,
                                      **product_create_schema.model_dump())

    return {'id': product_id}


@router.get(
    '',
    response_model=list[ProductResponseSchema],
    operation_id='fetchProducts',
    summary='Fetch products',
)
async def fetch_products_handler(
    session: AsyncSession = Depends(get_async_session),
    product_repository: IProductRepository = Depends(get_product_repository),
    title: str = Query(
        default=None,
        description="Search by product title",
    )
):
    response = await product_repository.fetch(session, title)
    return response
