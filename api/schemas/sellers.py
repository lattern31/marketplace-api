from pydantic import BaseModel, field_validator

from models.products import ProductStatus


class SellerUpdateProductStatusSchema(BaseModel):
    status: ProductStatus

    @field_validator('status')
    def validate_status(cls, v):
        if v not in (ProductStatus.READY_TO_SEND, ProductStatus.SHIPPING):
            raise ValueError('forbidden status value')
        return v
