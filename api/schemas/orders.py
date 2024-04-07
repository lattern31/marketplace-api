from datetime import datetime

from pydantic import BaseModel

from api.schemas.products import (ProductInSellerOrderSchema,
                                  ProductInUserOrderSchema)
from models.orders import OrderStatus


class OrderCreateResponseSchema(BaseModel):
    id: int


class UserOrderResponseSchema(OrderCreateResponseSchema):
    status: OrderStatus
    content: list[ProductInUserOrderSchema]
    #total_cost: int
    created_at: datetime


class SellerOrderResponseSchema(OrderCreateResponseSchema):
    status: OrderStatus
    content: list[ProductInSellerOrderSchema]
    #total_cost: int
    created_at: datetime
