from uuid import UUID

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from starlette import status

from contextlib import nullcontext as does_not_raise

from app.auth.schema import CreateUser
from app.main import app
from app.queries.user import AsyncUserQueries
from tests.conftest import API_URL


@pytest_asyncio.fixture
async def users_data_and_status() -> list:
    return [
        {
            'user': {
                'username': 'boben',
                'email': 'boben@gmail.com',
                'raw_password': 'Qwerty12',
            },
            'status': status.HTTP_201_CREATED,
            'result': does_not_raise()
        },
        {
            'user': {
                'username': 'robin',
                'email': 'robin@gmail.com',
                'raw_password': 'Qwerty12',
            },
            'status': status.HTTP_201_CREATED,
            'result': does_not_raise()
        },
        {
            'user': {
                'username': 'steve',
                'email': 'ail.com',
                'raw_password': 'Qwerty12',
            },
            'status': status.HTTP_422_UNPROCESSABLE_ENTITY,  # Because of a wrong email
            'result': does_not_raise()

        },
        {
            'user': {
                'username': 'steve',
                'email': 'gmail.com',
                'raw_password': 'Qwerty12',
            },
            'status': status.HTTP_422_UNPROCESSABLE_ENTITY,  # Because of a wrong email
            'result': does_not_raise()

        },
        {
            'user': {
                'username': 'e',
                'email': 'e.ail.com',
                'raw_password': 'Qwerty12',
            },
            'status': status.HTTP_422_UNPROCESSABLE_ENTITY,  # Because of a short username
            'result': does_not_raise()

        },
        {
            'user': {
                'username': 's'*31,
                'email': 'e.ail.com',
                'raw_password': 'Qwerty12',
            },
            'status': status.HTTP_422_UNPROCESSABLE_ENTITY,  # Because of a long username
            'result': does_not_raise()

        },
        {
            'user': {
                'username': 'steve',
                'email': 'e.ail.com',
                'raw_password': 'Qwerty',
            },
            'status': status.HTTP_422_UNPROCESSABLE_ENTITY,  # Because of a short password
            'result': does_not_raise()

        },
    ]

@pytest_asyncio.fixture
async def fake_uuid():
    return '9955edc2-6ac0-402f-9a1e-00d2e28c24cf'

@pytest_asyncio.fixture
async def users():
    users: list = [
        CreateUser(
            username='testtest1',
            email='testtest1@mail.run',
            raw_password='213213werQ',
            fullname='User Petrov'
        ),
        CreateUser(
            username='testtest2',
            email='testtest2@mail.run',
            fullname='User Igorev',
            raw_password='213213werQ'
        ),
        CreateUser(
            username='adminadmin',
            email='adminadmin@mail.run',
            raw_password='213213werQ',
            fullname='Admin Smith',
        ),
        CreateUser(
            username='adminadmin2',
            email='adminadmin2@mail.run',
            raw_password='213213werQ',
            fullname='Admin John'
        ),
    ]
    res = await AsyncUserQueries.create_users(users)
    return res


# @pytest_asyncio.fixture
# async def admin_data() -> dict:
#     admin_data = CreateUser(username='testtest', email='admin@mail.run', raw_password='213213werQ')
#     new_user_data: dict = admin_data.model_dump()
#     new_user_data.pop('raw_password')
#     new_user_data['password'] = bcrypt_context.hash(admin_data.raw_password)
#     async with async_session_maker() as conn:
#         admin: User = User(**new_user_data)
#         admin.is_active = True
#         conn.add(admin)
#         await conn.commit()
#     return ShowUser(**admin.__dict__).model_dump()

async def mock_get_user():
    return {
        'id': UUID('737e2086-a5a6-430f-8c46-8769eaa0c260'),
        'username': 'user1231232134',
        'email': 'user@mail.ru',
        'is_active': True,
        'is_superuser': False,
    }


async def mock_get_admin():
    return {
        'id': UUID('a2e91962-426e-4129-8205-c5ad150ab8bd'),
        'username': 'admin',
        'email': 'admin@mail.ru',
        'is_active': True,
        'is_superuser': True
    }

USER_API_URL: str = API_URL + '/users'
@pytest_asyncio.fixture
async def async_user_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=USER_API_URL) as client:
        yield client