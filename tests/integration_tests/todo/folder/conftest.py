import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.conftest import API_URL

FOLDER_API_URL: str = API_URL + "/folders"

@pytest_asyncio.fixture
async def async_folder_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=FOLDER_API_URL) as client:
        yield client


@pytest.fixture
def folder_data() -> dict:
    return {
            "name": "Some random folder"
        }


@pytest.fixture
def nested_folder_data() -> dict:
    return {
            "name": "A folder inside of other folder",
            "parent_id": None
        }


@pytest.fixture
def folder_update_data() -> dict:
    return {
            "description": "Some description"
        }
