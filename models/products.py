from dataclasses import dataclass
from enum import auto, StrEnum

from sqlalchemy.orm import Mapped

from db.db import Base
from utils.models_annotations import created_at, intpk


class ProductStatus(StrEnum):
    PENDING = auto()
    READY_TO_SEND = auto()
    SHIPPING = auto()
    DELIVERED = auto()
    RECEIVED = auto()
    CANCELLED = auto()


class Product(Base):
    __tablename__ = "products"

    id: Mapped[intpk]
    title: Mapped[str]
    seller_id: Mapped[int]
    cost: Mapped[int]
    created_at: Mapped[created_at]


@dataclass
class ProductInOrder:
    id: int
    title: str
    seller_id: int
    cost: int
    quantity: int
    status: ProductStatus
