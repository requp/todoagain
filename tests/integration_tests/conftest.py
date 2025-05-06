import pytest_asyncio

from app.auth.auth_router import bcrypt_context
from app.auth.model import User


@pytest_asyncio.fixture
async def users(db_test):
    password: str = bcrypt_context.hash('213213werQ')
    users: list = [
        User(
            username='testtest1',
            email='testtest1@mail.run',
            password=password,
            fullname='User Petrov'
        ),
        User(
            username='testtest2',
            email='testtest2@mail.run',
            password=password,
            fullname='User Igorev'
        ),
        User(
            username='adminadmin1',
            email='adminadmin1@mail.run',
            password=password,
            fullname='Admin Smith',
            is_superuser=True
        ),
        User(
            username='adminadmin2',
            email='adminadmin2@mail.run',
            password=password,
            fullname='Admin John',
            is_superuser=True
        )
    ]
    db_test.add_all(users)
    await db_test.commit()
    return users

@pytest_asyncio.fixture
async def fake_uuid():
    return '9955edc2-6ac0-402f-9a1e-00d2e28c24cf'