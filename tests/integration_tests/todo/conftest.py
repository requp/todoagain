import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from slugify import slugify

from app.auth.model import User
from app.main import app
from app.todo.folder.model import Folder
from tests.conftest import API_URL

FOLDER_API_URL: str = API_URL + '/folders'
TASK_API_URL: str = API_URL + '/tasks'

@pytest_asyncio.fixture
async def async_folder_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=FOLDER_API_URL) as client:
        yield client


@pytest_asyncio.fixture
async def async_task_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=TASK_API_URL) as client:
        yield client


@pytest_asyncio.fixture
async def folders(users, db_test):
    user: User = users[0]
    admin: User = users[-1]

    folders = [
        Folder(
            name='Test User Folder',
            user_id=user.id,
        ),
        Folder(
            name='Test Admin Folder',
            user_id=admin.id,
        ),
    ]
    db_test.add_all(folders)
    await db_test.commit()
    nested_folders: list = [
        Folder(
            name='Nested User Folder',
            user_id=user.id,
            parent_id=folders[0].id
        ),
        Folder(
            name='Nested Admin Folder',
            user_id=admin.id,
            parent_id=folders[1].id
        )
    ]
    db_test.add_all(nested_folders)
    await db_test.commit()

    folders.extend(nested_folders)

    db_test.add_all(folders)
    await db_test.commit()
    nested_nested_folders: list = [
        Folder(
            name='Nested Nested User Folder',
            user_id=user.id,
            parent_id=folders[2].id
        ),
        Folder(
            name='Nested Nested Admin Folder',
            user_id=admin.id,
            parent_id=folders[3].id
        )
    ]
    db_test.add_all(nested_nested_folders)
    await db_test.commit()

    folders.extend(nested_nested_folders)
    return folders