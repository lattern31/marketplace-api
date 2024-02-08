from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base
from utils.models_annotations import created_at, intpk


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    username: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[created_at]
    orders: Mapped[list["Order"]] = relationship()

    def __repr__(self):
        obj = f'id={self.id}, username={self.username}, \
                created_at={self.created_at.ctime()}'
        return obj
