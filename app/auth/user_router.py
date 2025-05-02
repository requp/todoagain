from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, Path
# from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select, update

from app.auth.service import UserManager
from app.depends.model_depends.uuid_depends import get_uuid_or_str
from app.auth.model import User
from app.auth.auth_router import get_current_user
from app.backend.config import ROOT_API
from app.auth.schema import CreateUser, ShowUser, UpdateUser
from app.backend.db_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix=ROOT_API + '/users', tags=['users'])

@router.post(path='/', status_code=status.HTTP_201_CREATED, response_model=ShowUser)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], new_user_raw: CreateUser):
    new_user: User = await UserManager.create_user(db=db, new_user_raw=new_user_raw)
    if not new_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="something got wrong with creation")
    user_data: dict = new_user.__dict__
    #user_data['role'] = new_user.role.value
    # return {
    #     'user_data': ShowUser(**user_data),
    #     'status_code': status.HTTP_201_CREATED,
    #     'transaction': 'Successful'
    # }
    return new_user


@router.get('/{id_or_username}', response_model=dict)
async def show_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        id_or_username: Annotated[UUID | str, Depends(get_uuid_or_str)]
):
    user: User | None = await UserManager.show_user(db=db, id_or_username=id_or_username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="this user doesn\'t exist")
    response = {
        'status_code': status.HTTP_200_OK,
        'detail': 'Successful',
        'data': ShowUser(**user.__dict__)
    }
    return response

@router.delete('/{user_id}/delete', response_model=dict)
async def delete_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        user_id: Annotated[UUID, Path()],
):
    result: dict =  await UserManager.delete_user(db=db, get_user=get_user, user_id=user_id)
    return result

@router.put('/{user_id}/update', response_model=dict)
async def update_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        user_id: Annotated[UUID, Path()],
        updated_data: UpdateUser
):
    result: dict =  await UserManager.update_user(
        db=db, get_user=get_user, user_id=user_id, updated_data=updated_data
    )
    return result
