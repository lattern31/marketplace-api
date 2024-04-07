from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base


class Cart(Base):
    __tablename__ = 'cart'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id', ondelete='CASCADE'),
        primary_key=True,
    )
    quantity: Mapped[int]
    product: Mapped["Product"] = relationship()
    cost: AssociationProxy[int] = association_proxy(
        'product', 'cost')
    title: AssociationProxy[int] = association_proxy(
        'product', 'title')
    seller_id: AssociationProxy[int] = association_proxy(
        'product', 'seller_id')
