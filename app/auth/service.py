from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Bundle
from starlette import status

from app.auth.auth_router import bcrypt_context
from app.auth.model import User
from app.auth.schema import CreateUser, UpdateUser, ShowUser
from app.backend.db_depends import get_db
from app.depends.model_depends.uuid_depends import get_uuid_or_str

async def _get_user_data_or_none(
        db: Annotated[AsyncSession, Depends(get_db)],
        id_or_username: Annotated[UUID | str, Field()],
        fields: Annotated[tuple | list, Field()]
) -> dict | None:
    """
    Return json data of a user
    from a given user's id or username

    :param db: AsyncSession
    :param id_or_username: UUID | str
    :param fields: tuple | list - Contains a collection of User model's fields
                                  which required to return
    :return: fields
    """

    user_values: tuple
    user_data: dict = {}
    if isinstance(id_or_username, UUID):
        # user = await db.scalar(select(User).where(User.id == id_or_username))
        user_values = (
            tuple(
                await db
                .scalar(
                    select(Bundle('user', *User.__table__.c[*fields])
                           )
                    .where(User.id == id_or_username)
                )))
    elif isinstance(id_or_username, str):
        user_values = (
            tuple(
                await db
                .scalar(
                    select(Bundle('user', *User.__table__.c[*fields])
                           )
                    .where(User.username == id_or_username)
                )))
        user_data.update(dict(zip(fields, user_values)))
    else:
        return None
    return user_data


async def _get_user_or_none(
        db: Annotated[AsyncSession, Depends(get_db)],
        id_or_username: Annotated[UUID | str, Field()]
) -> User | None:
    """
    Return a User object from a given user's id or username
    or None if the user doesn't exist

    :param db: AsyncSession
    :param id_or_username: UUID | str
    :return: User | None
    """

    user: User | None = None
    if isinstance(id_or_username, UUID):
        user = await db.scalar(select(User).where(User.id == id_or_username))
    elif isinstance(id_or_username, str):
        user = await db.scalar(select(User).where(User.username == id_or_username))
    return user



class UserManager:
    """
    Class which contains main static methods
    for working with User objects data
    between an Api router and a user DB table
    """

    @staticmethod
    async def create_user(db: AsyncSession, new_user_raw: CreateUser) -> dict:
        """
        Create a user account to give back a dict with user data
        or get an Exception

        :param db: AsyncSession
        :param new_user_raw: CreateUser - (username, email, raw_password, Optional[fullname])
        :return: dict - (id, email, username, fullname)
        """

        new_user_data: dict = new_user_raw.model_dump()
        new_user_data.pop('raw_password')
        new_user_data['password'] = bcrypt_context.hash(new_user_raw.raw_password)
        new_user: User = User(**new_user_data)
        db.add(new_user)
        await db.commit()
        if not new_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="something got wrong with creation")
        return ShowUser(**new_user.__dict__).model_dump()


    @staticmethod
    async def show_user(db: AsyncSession, id_or_username: UUID | str) -> dict:
        """
        Return back a dict with user data by a user's id or username
        or get an Exception

        :param db: AsyncSession
        :param id_or_username: UUID | str
        :return: dict  - (id, email, username, fullname)
        """
        user: User | None = await _get_user_or_none(db, id_or_username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This user doesn't exist"
            )
        return ShowUser(**user.__dict__).model_dump()


    @staticmethod
    async def update_user(
            db: AsyncSession, user_id: UUID, get_user: dict, updated_data: UpdateUser
    ) -> dict:
        """
        Update a user data with new updated fields by a user's id
        and return back and updated info
        or get an Exception

        :param db: AsyncSession
        :param user_id: UUID
        :param get_user: dict
        :param updated_data: UpdateUser - Optional[username, fullname]
        :return: dict - (id, email, username, fullname)
        """

        target_user: User | None = await db.scalar(select(User).filter_by(id=user_id))
        if target_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This user doesn't exist"
            )
        if target_user.id != get_user['id']:
            if target_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can't change other admins' data"
                )
            elif not get_user['is_superuser']:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have admin permission"
                )

        for key, value in updated_data.model_dump().items():
            if value:
                if getattr(target_user, key) != value:
                    if key == 'username':
                        is_taken_username: User | None = await db.scalar(
                            select(User).filter_by(username=value))
                        if is_taken_username:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail="This username is already taken"
                            )
                    setattr(target_user, key, value)
        if db.dirty:
            await db.commit()
            await db.refresh(target_user)
        return ShowUser(**target_user.__dict__).model_dump()


    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID, get_user: dict) -> None:
        """
        Make a user inactive by the user's id or get an Exception

        :param db: AsyncSession
        :param user_id: UUID
        :param get_user: dict
        :return: None
        """
        if not get_user.get('is_superuser'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have admin permission"
            )
        target_user: User | None = await db.scalar(select(User).filter_by(id=user_id))
        if target_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This user doesn't exist"
            )
        if target_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't delete admin user"
            )
        if not target_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='User already has been deleted'
            )
        target_user.is_active = False
        await db.commit()
        await db.refresh(target_user)
        if target_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='something got wrong'
            )