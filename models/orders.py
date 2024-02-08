from enum import auto, StrEnum

from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base
from utils.models_annotations import created_at, intpk


class OrderStatus(StrEnum):
    PENDING = auto()
    CHECKOUT = auto()
    SHIPPING = auto()
    COMPLETED = auto()
    CANCELLED = auto()


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
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
    product_name: Mapped[str] = mapped_column(
        ForeignKey("products.name", ondelete="CASCADE"),
        primary_key=True,
    )
    quantity: Mapped[int]
    product: Mapped["Product"] = relationship()
    cost: AssociationProxy[int] = association_proxy(
        'product', 'cost')
