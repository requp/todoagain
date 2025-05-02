from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr

class BaseUser(BaseModel):
    fullname: Annotated[str | None, Field(min_length=1, max_length=300)] = None
    username: Annotated[str, Field(min_length=4, max_length=32)]
    email: Annotated[EmailStr, Field(max_length=300)]

class UpdateUserPassword(BaseModel):
    raw_password: Annotated[str, Field(min_length=8, max_length=32)]

class UpdateUserEmail(BaseModel):
    email: Annotated[EmailStr, Field(max_length=300)]

class CreateUser(BaseUser):
    raw_password: Annotated[str, Field(min_length=8, max_length=32)]

class ShowUser(BaseUser):
    id: Annotated[UUID, Field()]
    role: str
    is_active: bool

class UpdateUser(BaseModel):
    fullname: Annotated[str | None, Field(min_length=1, max_length=300)] = None
    username: Annotated[str | None, Field(min_length=4, max_length=50)] = None
