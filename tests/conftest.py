import asyncio

import pytest
import pytest_asyncio
from pygments.styles.dracula import yellow
from sqlalchemy_utils import database_exists, create_database, drop_database

from app.auth.auth_router import get_current_user
from app.backend.config import settings
from app.backend.db import sync_engine, Base, async_engine, async_session_maker
from app.main import app

DEFAULT_DROP_DB_FLAG: str = 'false'
API_URL: str = 'http://127.0.0.1:8000/api/v1'


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# @pytest.fixture(scope='session', autouse=True)
# def setup_db():
#     assert settings.MODE == 'TEST'
#     if not database_exists(sync_engine.url):
#         create_database(sync_engine.url)
#     Base.metadata.drop_all(sync_engine)
#     Base.metadata.create_all(sync_engine)

# @pytest.fixture(scope='session')
# def create_db():
#     assert settings.MODE == 'TEST'
#     if not database_exists(sync_engine.url):
#         create_database(sync_engine.url)


@pytest_asyncio.fixture(scope='function',autouse=True)
async def async_setup():
    assert settings.MODE == 'TEST'
    async with async_engine.begin() as conn:
        # Очистить все таблицы
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await async_engine.dispose()


def pytest_addoption(parser):
    parser.addoption(
        "--drop_db",
        default=DEFAULT_DROP_DB_FLAG,
        choices=('false', 'true')
    )


@pytest.fixture(scope='session')
def does_drop_db(request):
    return request.config.getoption('--drop_db')


@pytest.fixture(scope='session', autouse=True)
def drop_db(does_drop_db):
    yield
    if does_drop_db == 'true':
        assert settings.MODE == 'TEST'
        if database_exists(sync_engine.url):
            drop_database(sync_engine.url)


@pytest_asyncio.fixture
async def db_test():
    async with async_session_maker() as conn:
        yield conn


@pytest.fixture(autouse=True, scope='function')
def drop_get_current_db():
    yield
    app.dependency_overrides.clear()