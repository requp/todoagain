from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.todo.folder.exceptions import FolderExceptionManager
from app.todo.folder.model import Folder
from app.todo.folder.schema import CreateFolder, ShowFolder, UpdateFolder


# async def _get_children_dict(db: AsyncSession, parent_id: UUID) -> list[dict]:
#     children: list[Folder] = list(await db.scalars(select(Folder).filter_by(parent_id=parent_id)))
#     return [ShowChildFolder(**child.__dict__).model_dump() for child in children]


class FolderManager:
    """
    Class which contains main static methods
    for working with Folder objects data
    between an Api router and a user DB table
    """

    @staticmethod
    async def create_folder(
            db: AsyncSession, get_user: dict, folder_data: CreateFolder
    )-> dict:
        """
        Create a new folder to give back a dict with folder data
        or get an Exception

        :param db: AsyncSession
        :param get_user: dict
        :param folder_data: CreateFolder - (name, Optional[description, parent_id])
        :return: dict - (id, name, description, parent_id, user_id)
        """
        await FolderExceptionManager.create_folder_exceptions(
            db=db, get_user=get_user, folder_data=folder_data
        )
        new_folder: Folder = Folder(
            **folder_data.model_dump(),
            user_id=get_user['id']
        )
        db.add(new_folder)
        await db.commit()
        if not new_folder.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="something got wrong with creation")
        return ShowFolder(**new_folder.__dict__).model_dump()


    @staticmethod
    async def show_folder(
            db: AsyncSession, get_user: dict, folder_id: UUID
    )-> dict:
        folder: Folder | None = await db.scalar(select(Folder).filter_by(id=folder_id))
        FolderExceptionManager.show_folder_exceptions(folder, get_user)
        #children: list[dict] = await FolderManager.get_children_dict(db=db, parent_id=folder.id)
        return ShowFolder(
            **folder.__dict__,
            #children=children
        ).model_dump()


    @staticmethod
    async def list_folders(
            db: AsyncSession, get_user: dict
    )-> list[dict]:
        folders: list[Folder] | None = list(
            await db.scalars(
                select(Folder)
                .filter_by(user_id=get_user['id'])
            )
        )
        folders_list: list[dict] = []
        for folder in folders:
            #children: list[dict] = await FolderManager.get_children_dict(db=db, parent_id=folder.id)
            folders_list.append(
                ShowFolder(
                    **folder.__dict__,
                    #children=children
                ).model_dump()
            )
        return folders_list


    @staticmethod
    async def update_folder(
            db: AsyncSession, folder_id: UUID, get_user: dict, updated_data: UpdateFolder
    ) -> dict:
        """
        Update a folder data with updated fields by a user's id
        and return back and updated info
        or get an Exception

        :param db: AsyncSession
        :param folder_id: UUID
        :param get_user: dict
        :param updated_data: UpdateUser - Optional[username, fullname]
        :return: dict - (id, email, username, fullname)
        """

        target_folder: Folder | None = await db.scalar(
            select(Folder).filter_by(id=folder_id)
        )
        await FolderExceptionManager.update_folder_exceptions(
            folder=target_folder, get_user=get_user, updated_data=updated_data, db=db
        )

        for key, value in updated_data.model_dump().items():
            if value:
                if getattr(target_folder, key) != value:
                    setattr(target_folder, key, value)
        if db.dirty:
            await db.commit()
            await db.refresh(target_folder)
        return ShowFolder(**target_folder.__dict__).model_dump()


    @staticmethod
    async def delete_folder(
            db: AsyncSession, get_user: dict, folder_id: UUID
    ) -> None:
        """
        Delete a folder object by a folder's id
        or get an Exception

        :param db: AsyncSession
        :param folder_id: UUID
        :param get_user: dict
        :return: None
        """
        folder: Folder | None = await db.scalar(
            select(Folder).filter_by(id=folder_id)
        )
        FolderExceptionManager.delete_folder_exceptions(folder, get_user)
        await db.delete(folder)
