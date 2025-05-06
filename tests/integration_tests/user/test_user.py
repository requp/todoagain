import pytest

from fastapi import status
from sqlalchemy import select

from app.auth.auth_router import get_current_user
from app.auth.model import User
from app.main import app
from tests.integration_tests.user.conftest import mock_get_user, mock_get_admin



# TODO: Can't run more than 1 test in pytest. They fail with RuntimeError. Now idk how to fix it


class TestUser:
    """
    Test class for testing creation, showing,
    updating and deleting user accounts
    """

    @pytest.mark.asyncio
    async def test_create_user(self, async_user_client, users_data_and_status) -> None:
        """
        Test a route for creating account

        :param async_user_client:
        :param users_data_and_status: dict - correct and incorrect user_data with status
        :return:
        """

        # Test response with positive and negative cases
        for user_json in users_data_and_status:
            response = await async_user_client.post('/', json=user_json['user'])
            assert response.status_code == user_json['status']
            if response.status_code == status.HTTP_201_CREATED:
                user_data: dict = response.json()
                assert user_data['data']['email'] == user_json['user']['email']
                assert user_data['data']['username'] == user_json['user']['username']


    @pytest.mark.asyncio
    async def test_show_user(self, users: list[User], async_user_client, fake_uuid):
        """
        Test a route for showing user's data

        :param users: list[User]
        :param async_user_client: AsyncClient
        :return: None
        """

        # Test response with positive cases with user's username and id
        user: User = users[0]
        for id_or_username in (user.username, user.id):
            response = await async_user_client.get(url=f'/{id_or_username}')
            assert response.status_code == status.HTTP_200_OK
            user_data: dict = response.json()
            assert user_data['detail'] == 'Successful'
            assert user_data['data']['username'] == user.username
            assert user_data['data']['email'] == user.email

        # Test response with not existing user
        response = await async_user_client.get(url=f'/{fake_uuid}')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['detail'] == "This user doesn't exist"


    @pytest.mark.asyncio
    async def test_update_user(self, users, async_user_client, db_test) -> None:
        """
        Test a route for updating user's data

        :param users: list[User]
        :param async_user_client: AsyncClient
        :param db_test: Async Session
        :return: None
        """

        user = await db_test.scalar(select(User).filter_by(is_superuser=False))
        admin = await db_test.scalar(select(User).filter_by(is_superuser=True))
        UPDATE_USER_URL: str = f'/{user.id}'
        UPDATE_ADMIN_URL: str = f'/{admin.id}'
        updated_fields: dict = {
            'fullname': 'New Fullname',
            'username': 'new_username'
        }

        # Test response with not auth data
        response = await async_user_client.put(url=UPDATE_USER_URL, json=updated_fields)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED # Not Auth
        assert response.json()['detail'] == 'Not authenticated'

        # Test response with not admin rights or not your own account
        app.dependency_overrides[get_current_user] = mock_get_user
        response = await async_user_client.put(url=UPDATE_USER_URL, json=updated_fields)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You don't have admin permission"

        # Test response when tries to update other admin account
        app.dependency_overrides[get_current_user] = mock_get_admin
        assert admin.fullname != updated_fields.get('fullname')
        response = await async_user_client.put(url=UPDATE_ADMIN_URL, json=updated_fields)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You can't change other admins' data"
        await db_test.refresh(admin)
        assert admin.fullname != updated_fields.get('fullname')

        # Test response with positive case of admin account on user
        app.dependency_overrides[get_current_user] = mock_get_admin
        assert user.fullname != updated_fields.get('fullname')
        response = await async_user_client.put(url=UPDATE_USER_URL, json=updated_fields)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == 'User has been successfully updated'
        await db_test.refresh(user)
        assert user.fullname == updated_fields.get('fullname')
        assert user.username == updated_fields.get('username')

        # Test response with taken username
        app.dependency_overrides[get_current_user] = mock_get_admin
        updated_fields['username'] = admin.username
        assert user.username != updated_fields['username']
        response = await async_user_client.put(url=UPDATE_USER_URL, json=updated_fields)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "This username is already taken"
        await db_test.refresh(user)
        assert user.username != updated_fields['username']


    @pytest.mark.asyncio
    async def test_delete_user(self, users, async_user_client, db_test, fake_uuid) -> None:
        """
        Test a route for deleting a user (make a user inactive)

        :param users: list[User]
        :param async_user_client: AsyncClient
        :param db_test: Async Session
        :return: None
        """

        user: User = await db_test.scalar(select(User).filter_by(is_superuser=False))
        admin: User = await db_test.scalar(select(User).filter_by(is_superuser=True))
        DELETE_USER_URL: str = f'/{user.id}'
        DELETE_ADMIN_URL: str = f'/{admin.id}'

        # Test response with not auth data
        response = await async_user_client.delete(url=DELETE_USER_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()['detail'] == 'Not authenticated'
        await db_test.refresh(user)
        assert user.is_active == True

        # Test response with not admin rights
        app.dependency_overrides[get_current_user] = mock_get_user
        response = await async_user_client.delete(url=DELETE_USER_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You don't have admin permission"
        await db_test.refresh(user)
        assert user.is_active == True

        # Test response when tries to delete an admin account
        app.dependency_overrides[get_current_user] = mock_get_admin
        response = await async_user_client.delete(url=DELETE_ADMIN_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You can't delete admin user"
        await db_test.refresh(admin)
        assert admin.is_active == True

        # Test response with a positive test case
        app.dependency_overrides[get_current_user] = mock_get_admin
        if not user.is_active: user.is_active = True
        response = await async_user_client.delete(url=DELETE_USER_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == 'User has been successfully deleted'
        await db_test.refresh(user)
        assert user.is_active == False

        # Test response when user already inactive
        app.dependency_overrides[get_current_user] = mock_get_admin
        if user.is_active: user.is_active = False
        response = await async_user_client.delete(url=DELETE_USER_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == 'User already has been deleted'
        await db_test.refresh(user)
        assert user.is_active == False

        # Test response when user doesn't exist
        response = await async_user_client.delete(url=f'/{fake_uuid}')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['detail'] == "This user doesn't exist"

