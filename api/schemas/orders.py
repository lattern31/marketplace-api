from datetime import datetime

from pydantic import BaseModel

from api.schemas.products import ProductInOrderSchema
from models.orders import OrderStatus


class OrderCreateSchema(BaseModel):
    user_id: int


class OrderCreateResponseSchema(BaseModel):
    id: int


class OrderResponseSchema(OrderCreateSchema, OrderCreateResponseSchema):
    status: OrderStatus
    content: list[ProductInOrderSchema]
    created_at: datetime


class OrderAddItemSchema(BaseModel):
    product_name: str
    quantity: int
