from datetime import datetime
from enum import auto, StrEnum

from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base
from utils.models_annotations import created_at, intpk
from models.products import ProductStatus


class OrderStatus(StrEnum):
    OPENED = auto()
    COMPLETED = auto()
    CANCELLED = auto()


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[intpk]
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    status: Mapped[OrderStatus]
    content: Mapped[list["OrdersProducts"]] = relationship()
    created_at: Mapped[created_at]


class OrdersProducts(Base):
    __tablename__ = "orders_products"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        primary_key=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    )
    quantity: Mapped[int]
    status: Mapped[ProductStatus]
    product: Mapped["Product"] = relationship()
    cost: AssociationProxy[int] = association_proxy(
        'product', 'cost')
    title: AssociationProxy[int] = association_proxy(
        'product', 'title')
    seller_id: AssociationProxy[int] = association_proxy(
        'product', 'seller_id')
