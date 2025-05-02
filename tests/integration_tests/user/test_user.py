import pytest
import pytest_asyncio

from fastapi import status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.auth.auth_router import get_current_user
from app.auth.model import User
from app.main import app
from tests.integration_tests.user.conftest import mock_get_user, mock_get_admin

API_URL: str = 'http://127.0.0.1:8000/api/v1'
USER_API_URL: str = API_URL + '/users'
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=USER_API_URL) as client:
        yield client

# TODO: Can't run more than 1 test in pytest. They fail with RuntimeError. Now idk how to fix it

@pytest.mark.usefixtures("async_setup")
class TestUser:
    # @pytest.mark.asyncio
    # async def test_create_user(self, async_setup, async_client, users_data_and_status):
    #     for user_json in users_data_and_status:
    #         response = await async_client.post('/', json=user_json['user'])
    #         assert response.status_code == user_json['status']
    #         if response.status_code == status.HTTP_201_CREATED:
    #             user_data: dict = response.json()
    #             assert user_data['email'] == user_json['user']['email']
    #             assert user_data['username'] == user_json['user']['username']
    #
    #
    # @pytest.mark.asyncio
    # async def test_show_user(self, users: list[User], async_client):
    #     user: User = users[0]
    #     for id_or_username in (user.username, user.id):
    #         response = await async_client.get(url=f'/{id_or_username}')
    #         assert response.status_code == status.HTTP_200_OK
    #         user_data: dict = response.json()
    #         assert user_data['detail'] == 'Successful'
    #         assert user_data['data']['username'] == user.username
    #         assert user_data['data']['email'] == user.email
    #
    #     response_not_exist = await async_client.get(url=f'/wrwerwerwer')
    #     assert response_not_exist.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_user(self, users, async_client, db_test):
        user = await db_test.scalar(select(User).filter_by(is_superuser=False))
        admin = await db_test.scalar(select(User).filter_by(is_superuser=True))
        UPDATE_USER_URL: str = f'/{user.id}/update'
        UPDATE_ADMIN_URL: str = f'/{admin.id}/update'
        updated_fields: dict = {
            'fullname': 'New Fullname',
            'username': 'new_username'
        }

        response = await async_client.put(url=UPDATE_USER_URL, json=updated_fields)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED # Not Auth
        assert response.json()['detail'] == 'Not authenticated'

        app.dependency_overrides[get_current_user] = mock_get_user
        response = await async_client.put(url=UPDATE_USER_URL, json=updated_fields)
        assert response.status_code == status.HTTP_403_FORBIDDEN # Not Admin
        assert response.json()['detail'] == "You don't have admin permission"

        app.dependency_overrides[get_current_user] = mock_get_admin

        assert admin.fullname != updated_fields.get('fullname')
        response = await async_client.put(url=UPDATE_ADMIN_URL, json=updated_fields)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You can't change other admins' data"
        await db_test.refresh(admin)
        assert admin.fullname != updated_fields.get('fullname')

        assert user.fullname != updated_fields.get('fullname')
        response = await async_client.put(url=UPDATE_USER_URL, json=updated_fields)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == 'User has been successfully updated'
        await db_test.refresh(user)
        assert user.fullname == updated_fields.get('fullname')
        assert user.username == updated_fields.get('username')

        updated_fields['username'] = admin.username
        assert user.username != updated_fields['username']
        response = await async_client.put(url=UPDATE_USER_URL, json=updated_fields)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "This username is already taken"
        await db_test.refresh(user)
        assert user.username != updated_fields['username']


    # @pytest.mark.asyncio
    # async def test_delete_user(self, users, async_client, db_test):
    #
    #     user: User = users[0]
    #     DELETE_URL: str = f'/{user.id}/delete'
    #
    #     response = await async_client.delete(url=DELETE_URL)
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED # Not Auth
    #     assert response.json()['detail'] == 'Not authenticated'
    #
    #     app.dependency_overrides[get_current_user] = mock_get_user
    #     response = await async_client.delete(url=DELETE_URL)
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED # Not Admin
    #     assert response.json()['detail'] == "You don't have admin permission"
    #
    #     # User still exists
    #     user = await db_test.scalar(select(User).filter_by(id=user.id))
    #     assert isinstance(user, User) == True
    #     assert user.is_active == True
    #
    #     app.dependency_overrides[get_current_user] = mock_get_admin
    #
    #     response = await async_client.delete(url=f'/{users[-1].id}')
    #     assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    #     assert response.json()['detail'] == 'Method Not Allowed'
    #
    #     response = await async_client.delete(url=DELETE_URL)
    #     assert response.status_code == status.HTTP_200_OK
    #     assert response.json()['detail'] == 'User has been successfully deleted'
    #     await db_test.refresh(user)
    #     assert user.is_active == False
    #
    #     # deleted already
    #     response = await async_client.delete(url=DELETE_URL)
    #     assert response.status_code == status.HTTP_403_FORBIDDEN
    #     assert response.json()['detail'] == 'User already has been deleted'
    #
    #     # user not found
    #     fake_uuid: str = '9955edc2-6ac0-402f-9a1e-00d2e28c24cf'
    #     response = await async_client.delete(url=f'{fake_uuid}/delete')
    #     assert response.status_code == status.HTTP_404_NOT_FOUND
    #     assert response.json()['detail'] == "This user doesn't exist"



