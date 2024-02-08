from datetime import datetime

from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    username: str


class UserResponseSchema(UserCreateSchema):
    id: int
    created_at: datetime


class UserCreateResponseSchema(BaseModel):
    id: int
