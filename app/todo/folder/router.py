from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.auth_router import get_current_user
from app.backend.config import ROOT_API
from app.backend.db_depends import get_db
from app.todo.folder.schema import CreateFolder, UpdateFolder
from app.todo.folder.service import FolderManager

router = APIRouter(prefix=ROOT_API + "/folders", tags=["folders"])

@router.post(path="/", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_folder(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        new_folder: CreateFolder
)-> dict:
    """
    Create a folder and return a response with the folder data

    :param db: AsyncSession
    :param new_folder: CreateUser - (name, Optional[description, parent_id])
    :param get_user: dict - a user who requires to create the folder
    :return: dict - (id, name, description, parent_id, user_id)
    """
    folder_data: dict = await FolderManager.create_folder(db=db, get_user=get_user, folder_data=new_folder)
    return {
        "data": folder_data,
        "status_code": status.HTTP_201_CREATED,
        "detail": "Successful"
    }


@router.get(path="/{folder_id}", response_model=dict)
async def show_folder(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        folder_id: Annotated[UUID, Path()]
)-> dict:
    """
    Return a response with the folder data

    :param db: AsyncSession
    :param folder_id: UUID
    :param get_user: dict - a user who requires to show the folder
    :return: dict - (id, name, description, parent_id, user_id)
    """
    folder_data: dict = await FolderManager.show_folder(db=db, get_user=get_user, folder_id=folder_id)
    return {
        "data": folder_data,
        "status_code": status.HTTP_200_OK,
        "detail": "Successful"
    }


@router.get(path="/", response_model=dict)
async def list_folders(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
)-> dict:
    """
    Return a response with the all user's folder

    :param db: AsyncSession
    :param get_user: dict - a user who requires to list all their folders
    :return: dict - (id, name, description, parent_id, user_id)
    """
    folders_data: list[dict] = await FolderManager.list_folders(db=db, get_user=get_user)
    return {
        "data": folders_data,
        "status_code": status.HTTP_200_OK,
        "detail": "Successful"
    }


@router.put(path="/{folder_id}", response_model=dict)
async def update_folder(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        folder_id: Annotated[UUID, Path()],
        updated_data: UpdateFolder
) -> dict:
    """
    Update a user data by user's id and return a response with user's data

    :param db: AsyncSession
    :param get_user: dict - the user who requires an update
    :param folder_id: UUID - folder's id which data needs to be updated
    :param updated_data: dict - Optional[name, description, is_active, parent_id]
    :return: dict - (data: user_data, status_code, detail)
    """
    folder_data: dict =  await FolderManager.update_folder(
        db=db, get_user=get_user, folder_id=folder_id, updated_data=updated_data
    )
    return {
        "data": folder_data,
        "status_code": status.HTTP_200_OK,
        "detail": "Folder has been successfully updated"
    }


@router.delete(path="/{folder_id}", response_model=dict)
async def delete_folder(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        folder_id: Annotated[UUID, Path()],
) -> dict:
    """
    Update a user data by user's id and return a response with user's data

    :param db: AsyncSession
    :param get_user: dict - the user who requires to delete a folder
    :param folder_id: UUID - folder's id which needs to be deleted
    :return: dict
    """
    await FolderManager.delete_folder(
        db=db, get_user=get_user, folder_id=folder_id
    )
    return {
        "status_code": status.HTTP_200_OK,
        "detail": "Folder has been successfully deleted"
    }