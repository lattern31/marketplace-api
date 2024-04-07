from datetime import datetime

from pydantic import BaseModel, Field, PositiveInt

from models.products import ProductStatus


class ProductCreateSchema(BaseModel):
    title: str
    cost: PositiveInt


class ProductResponseSchema(ProductCreateSchema):
    id: int
    seller_id: int
    created_at: datetime


class ProductCreateResponseSchema(BaseModel):
    id: int


class ProductInCartSchema(ProductCreateSchema):
    id: int = Field(validation_alias='product_id')
    seller_id: int
    quantity: int


class ProductInUserOrderSchema(ProductInCartSchema):
    status: ProductStatus


class ProductInSellerOrderSchema(ProductInCartSchema):
    #address: str
    status: ProductStatus
