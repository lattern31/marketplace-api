from pydantic import BaseModel

from api.schemas.products import ProductInCartSchema


class CartResponseSchema(BaseModel):
    content: list[ProductInCartSchema]

class CartAddRemoveSchema(BaseModel):
    product_id: int
