from datetime import datetime

from pydantic import BaseModel, Field


class ProductCreateSchema(BaseModel):
    title: str
    cost: int


class ProductResponseSchema(ProductCreateSchema):
    id: int
    created_at: datetime


class ProductCreateResponseSchema(BaseModel):
    id: int


class ProductInOrderSchema(BaseModel):
    id: int = Field(validation_alias='product_id')
    title: str
    cost: int
    quantity: int
