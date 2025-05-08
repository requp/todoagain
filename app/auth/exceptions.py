from uuid import UUID

from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.model import User
from app.auth.schema import CreateUser, UpdateUser


async def _is_username_taken(username: str, db: AsyncSession) -> bool:
    """
    Bool value of existing a user with given username

    :param username: str
    :param db: AsyncSession
    :return: bool
    """

    return bool(
        await db.scalar(
            select(User).filter_by(username=username)
        )
    )


async def _is_email_taken(email: str | EmailStr, db: AsyncSession) -> bool:
    """
    Bool value of existing a user with given email

    :param email: str
    :param db: AsyncSession
    :return: bool
    """

    return bool(
        await db.scalar(
            select(User).filter_by(email=email)
        )
    )


def user_not_exist(user: User | None) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="An user with given id doesn't exist"
        )


def user_have_no_admin_permissions(user_id: str | UUID, get_user: dict) -> None:
    if user_id != get_user["id"] or str(user_id) != get_user["id"]:
        if not get_user["is_superuser"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have admin permission"
            )


def admin_cant_edit_other_admin(
        user: User | UUID, get_user: dict, action_name: str = "update"
) -> None:
    if str(user.id) != get_user["id"]:
        if user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You can't {action_name} other admin's data"
            )

async def username_is_taken(
        db: AsyncSession,
        user_data: CreateUser | UpdateUser,
        user: User | None = None
) -> None:
    if not user or (user_data.username and user.username != user_data.username):
        is_username_taken: bool = await _is_username_taken(
            db=db, username=user_data.username
        )
        if is_username_taken:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This username is already taken"
            )


async def email_is_taken(
        db: AsyncSession,
        user_data: CreateUser | UpdateUser,
) -> None:
    is_email_taken: bool = await _is_email_taken(
        db=db, email=user_data.email
    )
    if is_email_taken:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This email is already taken"
        )


def user_is_already_inactive(user: User) -> None:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User already has been deleted"
        )


class UserExceptionManager:
    """

    """

    @staticmethod
    async def create_user_exceptions(
            db: AsyncSession,
            user_data: CreateUser
    ) -> None:
        await username_is_taken(db=db, user_data=user_data)
        await email_is_taken(db=db, user_data=user_data)


    @staticmethod
    def show_user_exceptions(user: User | None) -> None:
        user_not_exist(user=user)


    @staticmethod
    async def update_user_exceptions(
            user: User | None,
            get_user: dict,
            updated_data: UpdateUser,
            db: AsyncSession
    ) -> None:
        user_not_exist(user=user)
        user_have_no_admin_permissions(
            get_user=get_user, user_id=str(user.id)
        )
        admin_cant_edit_other_admin(user=user, get_user=get_user)
        await username_is_taken(
            user=user, user_data=updated_data, db=db
        )


    @staticmethod
    def delete_user_exceptions(
            user: User | None, get_user: dict
    ) -> None:
        user_not_exist(user=user)
        user_have_no_admin_permissions(
            get_user=get_user, user_id=str(user.id)
        )
        admin_cant_edit_other_admin(
            user=user, get_user=get_user, action_name="delete"
        )
        user_is_already_inactive(user=user)