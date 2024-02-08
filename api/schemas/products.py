from datetime import datetime

from pydantic import BaseModel


class ProductCreateSchema(BaseModel):
    name: str
    cost: int


class ProductResponseSchema(ProductCreateSchema):
    created_at: datetime


class ProductCreateResponseSchema(BaseModel):
    name: str


class ProductInOrderSchema(BaseModel):
    product_name: str
    cost: int
    quantity: int
