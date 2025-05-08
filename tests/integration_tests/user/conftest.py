from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from starlette import status

from contextlib import nullcontext as does_not_raise

from app.main import app
from tests.conftest import API_URL

USER_API_URL: str = API_URL + "/users"
@pytest_asyncio.fixture
async def async_user_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=USER_API_URL) as client:
        yield client


@pytest.fixture
def updated_fields() -> dict:
    return {
            "fullname": "New Fullname",
            "username": "new_username"
        }


@pytest.fixture
def user_data() -> dict:
    return {
            "username": "clint_est",
            "fullname": "Clint Eastwood",
            "email": "clint@gmail.com",
            "raw_password": "Some2Cool@pass"
        }
