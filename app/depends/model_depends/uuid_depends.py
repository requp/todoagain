from typing import Annotated
from uuid import UUID
from fastapi import Query, Path


async def get_uuid_or_str(id_or_username: Annotated[str, Path()]) -> str | UUID:
    try:
        uuid_str = UUID(id_or_username)
    except ValueError:
        if not isinstance(id_or_username, str):
            raise TypeError
        return id_or_username
    return uuid_str
