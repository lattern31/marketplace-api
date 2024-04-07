from datetime import datetime

from pydantic import BaseModel, Field
from models.users import UserRole


class UserSchema(BaseModel):
    username: str# = Field(min_length=4)
    role: UserRole


class UserCreateSchema(UserSchema):
    password: str# = Field(min_length=4)


class UserResponseSchema(UserSchema):
    id: int
    created_at: datetime


class UserCreateResponseSchema(BaseModel):
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str
