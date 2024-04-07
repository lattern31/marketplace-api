from enum import auto, StrEnum

from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base
from utils.models_annotations import created_at, intpk


class UserRole(StrEnum):
    CUSTOMER = auto()
    SELLER = auto()
    ADMIN = auto()


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    disabled: Mapped[bool] = mapped_column(default=False)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    role: Mapped[UserRole]
    created_at: Mapped[created_at]
    orders: Mapped[list["Order"]] = relationship()
    cart: Mapped[list["Cart"]] = relationship()

    def __repr__(self):
        obj = f'id={self.id}, username={self.username}, \
pswd_hash={self.hashed_password}, \
created_at={self.created_at.ctime()}'
        return obj
