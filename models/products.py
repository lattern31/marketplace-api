from sqlalchemy.orm import Mapped

from db.db import Base
from utils.models_annotations import created_at, intpk


class Product(Base):
    __tablename__ = "products"

    id: Mapped[intpk]
    title: Mapped[str]
    cost: Mapped[int]
    created_at: Mapped[created_at]
