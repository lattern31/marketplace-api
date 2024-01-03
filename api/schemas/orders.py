from datetime import datetime
from typing import Any

from pydantic import BaseModel

from api.schemas.products import ProductCreateSchema, ProductInOrderSchema


class OrderCreateSchema(BaseModel):
    user_id: int


class OrderCreateResponseSchema(BaseModel):
    id: int


class OrderResponseSchema(OrderCreateSchema, OrderCreateResponseSchema):
    status: str
    content: list[ProductInOrderSchema]
    created_at: datetime


class OrderAddItemSchema(BaseModel):
    order_id: int
    product_name: str
    quantity: int

