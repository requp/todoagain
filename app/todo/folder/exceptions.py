from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.exceptions import user_have_no_admin_permissions
from app.todo.folder.model import Folder
from app.todo.folder.schema import CreateFolder, UpdateFolder


async def _is_name_taken_by_user_id(user_id: UUID, folder_name: str, db: AsyncSession) -> bool:
    """
    Bool value of existing a folder's name with some folder's user id in it

    :param user_id: UUID
    :param folder_name: str
    :param db: AsyncSession
    :return: bool
    """

    return bool(
        await db.scalar(select(Folder).filter(
            and_(Folder.name == folder_name, Folder.user_id == user_id)
            ))
    )


async def _is_users_parent_folder(
        user_id: UUID | str, parent_id: UUID, db: AsyncSession
) -> bool:
    parent_folder: Folder | None = await db.scalar(select(Folder).filter_by(id=parent_id))
    if not parent_folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given parent_id folder doesn't exist"
        )
    return parent_folder.user_id == user_id or str(parent_folder.user_id) == user_id


def folder_not_exist(folder: Folder | None) -> None:
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A folder with given id doesn't exist"
        )


async def name_is_taken_by_user(
        db: AsyncSession,
        folder_data: CreateFolder | UpdateFolder,
        get_user: dict,
        action_name: str = "create"
):
    is_name_taken_by_user: bool = await _is_name_taken_by_user_id(
        db=db, folder_name=folder_data.name, user_id=get_user["id"]
    )
    if is_name_taken_by_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You can't {action_name} a folder "
                   "with the same name which you already have"
        )


async def other_user_parent_folder(
        db: AsyncSession,
        get_user: dict,
        folder_data: CreateFolder | UpdateFolder,
        action_name: str = "create"
) -> None:
    if folder_data.parent_id:
        is_users_parent_folder: bool = await _is_users_parent_folder(
            db=db, user_id=get_user["id"], parent_id=folder_data.parent_id
        )
        if not is_users_parent_folder:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You can't {action_name} a nested folder "
                       "with the other user's folder"
            )


def private_folder(folder: Folder, get_user: dict) -> None:
    if (
            not get_user["is_superuser"]
            and folder.is_private
            and str(folder.user_id) != get_user["id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't see a private folder of other user"
        )


class FolderExceptionManager:
    """

    """

    @staticmethod
    async def create_folder_exceptions(
            db: AsyncSession,
            get_user: dict,
            folder_data: CreateFolder | UpdateFolder
    ) -> None:
        await name_is_taken_by_user(
            db=db, folder_data=folder_data, get_user=get_user
        )
        await other_user_parent_folder(
            db=db, folder_data=folder_data, get_user=get_user
        )


    @staticmethod
    def show_folder_exceptions(
            folder: Folder | None, get_user: dict
    ) -> None:
        folder_not_exist(folder=folder)
        private_folder(folder=folder, get_user=get_user)


    @staticmethod
    async def update_folder_exceptions(
            folder: Folder | None,
            get_user: dict,
            updated_data: UpdateFolder,
            db: AsyncSession
    ) -> None:
        folder_not_exist(folder=folder)
        user_have_no_admin_permissions(
            get_user=get_user, user_id=str(folder.user_id)
        )
        if updated_data.name and updated_data.name != folder.name:
            await name_is_taken_by_user(
                folder_data=updated_data, db=db, get_user=get_user, action_name="update"
            )
        await other_user_parent_folder(
            db=db, folder_data=updated_data, get_user=get_user, action_name="update"
        )


    @staticmethod
    def delete_folder_exceptions(
            folder: Folder | None, get_user: dict
    ) -> None:
        folder_not_exist(folder=folder)
        user_have_no_admin_permissions(
            get_user=get_user, user_id=str(folder.user_id)
        )