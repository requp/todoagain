from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, Path
# from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select, update

from app.auth.service import UserManager
from app.depends.model_depends.uuid_depends import get_uuid_or_str
from app.auth.model import User
from app.auth.auth_router import get_current_user
from app.backend.config import ROOT_API
from app.auth.schema import CreateUserRaw, ShowUser, UpdateUser
from app.backend.db_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix=ROOT_API + "/users", tags=["users"])

@router.post(path="/", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        new_user_raw: CreateUserRaw
) -> dict:
    """
    Create user and return a response with user data

    :param db: AsyncSession
    :param new_user_raw: CreateUser - (username, email, raw_password, Optional[fullname])
    :return: dict - (data: user_data, status_code, detail)
    """
    user_data: dict = await UserManager.create_user(db=db, new_user_raw=new_user_raw)
    return {
        "data": user_data,
        "status_code": status.HTTP_201_CREATED,
        "detail": "Successful"
    }


@router.get("/{id_or_username}", response_model=dict)
async def show_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        id_or_username: Annotated[UUID | str, Depends(get_uuid_or_str)]
) -> dict:
    """
    Return response with a user data by user's id or username

    :param db: AsyncSession
    :param id_or_username: str | UUID
    :param get_user: dict - the user who requires to show a user by id
    :return: dict - (data: user_data, status_code, detail)
    """
    user_data: dict  = await UserManager.show_user(db=db, id_or_username=id_or_username)
    return {
        "data": user_data,
        "status_code": status.HTTP_200_OK,
        "detail": "Successful"
    }


@router.put("/{user_id}", response_model=dict)
async def update_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        user_id: Annotated[UUID, Path()],
        updated_data: UpdateUser
) -> dict:
    """
    Update a user data by user's id and return a response with user's data

    :param db: AsyncSession
    :param get_user: dict - the user who requires an update
    :param user_id: UUID - user's id which data needs to be updated
    :param updated_data: dict - Optional[username, fullname]
    :return: dict - (data: user_data, status_code, detail)
    """
    user_data: dict =  await UserManager.update_user(
        db=db, get_user=get_user, user_id=user_id, updated_data=updated_data
    )
    return {
        "data": user_data,
        "status_code": status.HTTP_200_OK,
        "detail": "User has been successfully updated"
    }


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        user_id: Annotated[UUID, Path()],
) -> dict:
    """
    Make a user inactive by user's id

    :param db: AsyncSession
    :param get_user: dict - the user who requires an update
    :param user_id: UUID - user's id which data needs to be updated
    :return: dict - (data: user_data, status_code, detail)
    """
    await UserManager.delete_user(db=db, get_user=get_user, user_id=user_id)
    return {
        "status_code": status.HTTP_200_OK,
        "detail": "User has been successfully deleted"
    }

