from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import select

from app.backend.config import settings
from app.auth.model import User
from app.backend.db_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from passlib.context import CryptContext
from datetime import datetime, timedelta

router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
async def create_access_token(username: str, user_id: str, is_superuser: bool, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'is_superuser': is_superuser}
    expires = datetime.now() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str):
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not bcrypt_context.verify(password, str(user.password)) or user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

from jose import jwt, JWTError


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        is_admin: bool = payload.get('is_superuser')
        expire = payload.get('exp')
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied"
            )
        if datetime.now() > datetime.fromtimestamp(expire):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token expired!"
            )

        return {
            'username': username,
            'id': user_id,
            'is_superuser': is_admin,
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )

@router.post('/token')
async def login(db: Annotated[AsyncSession, Depends(get_db)], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(db, form_data.username, form_data.password)

    if not user or user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )

    token = await create_access_token(
        username=str(user.username),
        user_id=str(user.id),
        is_superuser=bool(user.is_superuser),
        expires_delta=timedelta(minutes=20)
    )
    return {
        'access_token': token,
        'token_type': 'bearer'
    }

