import pytest
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


@pytest.fixture
def fake_uuid():
    return '9955edc2-6ac0-402f-9a1e-00d2e28c24cf'


@pytest_asyncio.fixture
async def user_1(users):
    return users[0]


@pytest_asyncio.fixture
async def mock_get_current_user_1(user_1):

    return lambda :{
        'id': str(user_1.id),
        'username': user_1.username,
        'is_superuser': user_1.is_superuser
    }


@pytest_asyncio.fixture
async def user_2(users):
    return users[1]


@pytest_asyncio.fixture
async def mock_get_current_user_2(user_2):

    return lambda :{
        'id': str(user_2.id),
        'username': user_2.username,
        'is_superuser': user_2.is_superuser
    }


@pytest_asyncio.fixture
async def admin_1(users):
    return users[2]


@pytest_asyncio.fixture
async def mock_get_current_admin_1(admin_1):

    return lambda :{
        'id': str(admin_1.id),
        'username': admin_1.username,
        'is_superuser': admin_1.is_superuser
    }


@pytest_asyncio.fixture
async def admin_2(users):
    return users[3]


@pytest_asyncio.fixture
async def mock_get_current_admin_2(admin_2):

    return lambda :{
        'id': str(admin_2.id),
        'username': admin_2.username,
        'is_superuser': admin_2.is_superuser
    }
