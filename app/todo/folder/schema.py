from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

class BaseFolder(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    description: Annotated[str | None, Field(max_length=1000)] = None
    parent_id: UUID | None = None


class CreateFolder(BaseFolder):
    pass


class ShowFolder(BaseFolder):
    id: UUID
    is_active: bool
    user_id: UUID
    children: list[dict] | None = None


class UpdateFolder(BaseFolder):
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    is_active: bool | None = None


# class ShowChildFolder(BaseModel):
#     id: UUID
#     name: str
#     description: str | None = None
#     is_active: bool
#     user_id: UUID