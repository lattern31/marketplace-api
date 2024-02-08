from sqlalchemy.orm import Mapped

from db.db import Base
from utils.models_annotations import created_at, strpk


class Product(Base):
    __tablename__ = "products"

    name: Mapped[strpk]
    cost: Mapped[int]
    created_at: Mapped[created_at]
