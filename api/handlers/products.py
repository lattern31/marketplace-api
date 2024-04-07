from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_async_session, get_product_repository
from api.schemas.products import (ProductCreateSchema,
                                  ProductCreateResponseSchema,
                                  ProductResponseSchema)
from models.users import User, UserRole
from repositories.products import IProductRepository
from services.auth import get_current_active_user
from services.products import create_product, check_product_exists


router = APIRouter(prefix='/products', tags=['products'])


@router.get('')
async def get_products(
    session: AsyncSession = Depends(get_async_session),
    product_repository: IProductRepository = Depends(get_product_repository),
) -> list[ProductResponseSchema]:
    products = await product_repository.get_all(session)
    return products


@router.post('')
async def create_product(
    product_create_schema: ProductCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    product_repository: IProductRepository = Depends(get_product_repository),
    current_user: User = Depends(
        get_current_active_user(required_roles=[UserRole.SELLER])
    ),
) -> ProductCreateResponseSchema:
    product_id = await product_repository.create(
        session, **product_create_schema.model_dump(),
        seller_id=current_user.id
    )
    return ProductCreateResponseSchema(id=product_id)


@router.get('/{product_id}')
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_async_session),
    product_repository: IProductRepository = Depends(get_product_repository),
):
    await check_product_exists(session, product_repository, product_id)
    product = await product_repository.get_one(session, product_id)
    return product 
