import pytest
from sqlalchemy import select, and_
from starlette import status

from app.auth.auth_router import get_current_user
from app.auth.model import User
from app.main import app
from app.todo.folder.model import Folder
from tests.integration_tests.todo.conftest import async_folder_client


class TestFolder:
    """
    Test class for testing creation, showing,
    updating and deleting folders
    """

    @pytest.mark.asyncio
    async def test_create_folder(self, async_folder_client, users, db_test, fake_uuid) -> None:
        """
        Test a route for creating account

        :param async_folder_client: Async client for testing an api route
        :param users: list[Users]
        :db_test: AsyncSession
        :folders: list[Folder]
        :fake_uuid: UUID
        :return:
        """

        user_1: User = users[0]
        user_2: User = users[1]
        folder_data: dict = {
            'name': 'Some random folder'
        }
        nested_folder_data: dict = {
            'name': 'A folder inside of other folder',
            'parent_id': None
        }
        def mock_get_current_user_1():
            return {
                'id': str(user_1.id),
                'username': user_1.username,
                'is_superuser': user_1.is_superuser
            }
        def mock_get_current_user_2():
            return {
                'id': str(user_2.id),
                'username': user_2.username,
                'is_superuser': user_2.is_superuser
            }

        # Test response with not auth data
        response = await async_folder_client.post(url='/', json=folder_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()['detail'] == 'Not authenticated'

        # Test response with a positive test case
        app.dependency_overrides[get_current_user] = mock_get_current_user_1
        response = await async_folder_client.post(url='/', json=folder_data)
        assert response.status_code == status.HTTP_201_CREATED
        json_data: dict = response.json()
        assert json_data['detail'] == 'Successful'
        nested_folder_data['parent_id'] = json_data['data']['id']

        # Test response with a positive test case of a nested folder
        app.dependency_overrides[get_current_user] = mock_get_current_user_1
        response = await async_folder_client.post(url='/', json=nested_folder_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['detail'] == 'Successful'

        # Test response with creating a folder with the same name and the same user
        app.dependency_overrides[get_current_user] = mock_get_current_user_1
        response = await async_folder_client.post(url='/', json=folder_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You can't create a folder with the same name which you already have"

        # Test response with a positive test case of the same folder's name but other user
        app.dependency_overrides[get_current_user] = mock_get_current_user_2
        response = await async_folder_client.post(url='/', json=folder_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['detail'] == 'Successful'

        # Test response with a nested folder of other user's id
        app.dependency_overrides[get_current_user] = mock_get_current_user_2
        response = await async_folder_client.post(url='/', json=nested_folder_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You can't create a nested folder with the other user's folder"

        # Test response with a nested folder with no exist id
        app.dependency_overrides[get_current_user] = mock_get_current_user_2
        nested_folder_data['parent_id'] = fake_uuid
        response = await async_folder_client.post(url='/', json=nested_folder_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['detail'] == "Given parent_id folder doesn't exist"


    @pytest.mark.asyncio
    async def test_show_folder(self, async_folder_client, users, folders, fake_uuid) -> None:
        """
        Test a route for showing a folder data

        :param async_folder_client: Async client for testing an api route
        :param users: list[Users]
        :folders: list[Folder]
        :fake_uuid: UUID
        :return:
        """

        user_folder: Folder = folders[0]
        admin_folder: Folder = folders[1]
        USER_FOLDER_URL: str = f'/{user_folder.id}'
        ADMIN_FOLDER_URL: str = f'/{admin_folder.id}'
        user: User = users[0]
        admin: User = users[-1]

        def mock_get_current_user():
            return {
                'id': str(user.id),
                'username': user.username,
                'is_superuser': user.is_superuser
            }
        def mock_get_current_admin():
            return {
                'id': str(admin.id),
                'username': admin.username,
                'is_superuser': admin.is_superuser
            }

        # Test response with not auth data
        response = await async_folder_client.get(url=USER_FOLDER_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()['detail'] == 'Not authenticated'

        # Test response with a positive test case
        app.dependency_overrides[get_current_user] = mock_get_current_user
        response = await async_folder_client.get(url=USER_FOLDER_URL)
        assert response.status_code == status.HTTP_200_OK
        json_data: dict = response.json()
        assert json_data['detail'] == 'Successful'
        assert json_data['data']['id'] == str(folders[0].id)
        #assert json_data['data']['children'][0]['id'] == str(folders[2].id)

        # Test response with a positive test case with admin with user's private folder
        app.dependency_overrides[get_current_user] = mock_get_current_admin
        response = await async_folder_client.get(url=USER_FOLDER_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == 'Successful'

        # Test response with a user trying to see other user's private folder
        app.dependency_overrides[get_current_user] = mock_get_current_user
        response = await async_folder_client.get(url=ADMIN_FOLDER_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You can't see a private folder of other user"

        # Test response with a not exist folder
        app.dependency_overrides[get_current_user] = mock_get_current_user
        response = await async_folder_client.get(url=f'/{fake_uuid}')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['detail'] == "A folder with given id doesn't exist"


    @pytest.mark.asyncio
    async def test_list_folders(self, async_folder_client, users, folders) -> None:
        """
        Test a route for listing all user's folders

        :param async_folder_client: Async client for testing an api route
        :param users: list[Users]
        :folders: list[Folder]
        :return:
        """

        user: User = users[0]

        def mock_get_current_user():
            return {
                'id': str(user.id),
                'username': user.username,
                'is_superuser': user.is_superuser
            }

        # Test response with not auth data
        response = await async_folder_client.get(url='/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()['detail'] == 'Not authenticated'

        # Test response with a positive test case
        app.dependency_overrides[get_current_user] = mock_get_current_user
        response = await async_folder_client.get(url='/')
        assert response.status_code == status.HTTP_200_OK
        json_data: dict = response.json()
        assert json_data['detail'] == 'Successful'
        assert len(json_data['data']) == 3


    @pytest.mark.asyncio
    async def test_update_folder(
            self, users, async_folder_client, folders, db_test, fake_uuid
    ) -> None:
        """
        Test a route for updating folder's data

        :param users: list[User]
        :param async_folder_client: AsyncClient
        :param db_test: Async Session
        :folders: list[Folder]
        :return: None
        """

        user: User = users[0]
        admin: User = users[-1]
        user_folder: Folder = await db_test.scalar(
            select(Folder)
            .filter(and_(
                Folder.user_id == user.id, Folder.parent_id == folders[2].id
            ))
        )
        admin_folder: Folder = await db_test.scalar(
            select(Folder)
            .filter(and_(
                Folder.user_id == admin.id, Folder.parent_id == folders[3].id
            ))
        )
        USER_FOLDER_1_URL: str = f'/{user_folder.id}'
        USER_FOLDER_2_URL: str = f'/{folders[0].id}'
        ADMIN_FOLDER_URL: str = f'/{admin_folder.id}'

        def mock_get_current_user():
            return {
                'id': str(user.id),
                'username': user.username,
                'is_superuser': user.is_superuser
            }
        def mock_get_current_admin():
            return {
                'id': str(admin.id),
                'username': admin.username,
                'is_superuser': admin.is_superuser
            }

        updated_fields: dict = {
            'description': 'Some description'
        }

        # Test response with not auth data
        response = await async_folder_client.put(url=USER_FOLDER_1_URL, json=updated_fields)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()['detail'] == 'Not authenticated'

        # Test response with not admin rights or not your own account
        app.dependency_overrides[get_current_user] = mock_get_current_user
        response = await async_folder_client.put(url=ADMIN_FOLDER_URL, json=updated_fields)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        json_data: dict = response.json()
        assert json_data['detail'] == "You don't have admin permission"
        await db_test.refresh(admin_folder)
        assert admin_folder.description != updated_fields['description']

        # Test response with a not exist folder
        app.dependency_overrides[get_current_user] = mock_get_current_user
        response = await async_folder_client.put(url=f'/{fake_uuid}', json=updated_fields)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['detail'] == "A folder with given id doesn't exist"

        # Test response with positive case of admin account on user
        app.dependency_overrides[get_current_user] = mock_get_current_admin
        response = await async_folder_client.put(url=USER_FOLDER_1_URL, json=updated_fields)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == 'Folder has been successfully updated'
        await db_test.refresh(user_folder)
        assert user_folder.description == updated_fields['description']

        # Test response with positive case
        app.dependency_overrides[get_current_user] = mock_get_current_user
        new_update_data: dict = {
            'parent_id': str(folders[0].id),
            'name': 'Second nested user folder'
        }
        response = await async_folder_client.put(url=USER_FOLDER_1_URL, json=new_update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == 'Folder has been successfully updated'
        await db_test.refresh(user_folder)
        assert user_folder.parent_id == folders[0].id
        assert user_folder.name == 'Second nested user folder'

        # Test response with a nested folder of other user's id
        nested_folder_data: dict = {
            'name': 'A folder inside of other folder',
            'parent_id': str(folders[1].id)
        }
        app.dependency_overrides[get_current_user] = mock_get_current_user
        response = await async_folder_client.put(url=USER_FOLDER_1_URL, json=nested_folder_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You can't update a nested folder with the other user's folder"

        # Test response with taken folder's name by user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        updated_fields['name'] = 'Second nested user folder'
        response = await async_folder_client.put(url=USER_FOLDER_2_URL, json=updated_fields)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You can't update a folder with the same name which you already have"


    @pytest.mark.asyncio
    async def test_delete_folder(
            self, users, async_folder_client, folders, db_test, fake_uuid
    ) -> None:
        """
        Test a route for deleting a folder object

        :param users: list[User]
        :param async_folder_client: AsyncClient
        :param db_test: Async Session
        :folders: list[Folder]
        :return: None
        """

        user: User = users[0]
        admin: User = users[-1]
        user_folder: Folder = await db_test.scalar(
            select(Folder)
            .filter(and_(
                Folder.user_id == user.id, Folder.parent_id == folders[2].id
            ))
        )
        admin_folder: Folder = await db_test.scalar(
            select(Folder)
            .filter(and_(
                Folder.user_id == admin.id, Folder.parent_id == folders[3].id
            ))
        )
        USER_FOLDER_1_URL: str = f'/{user_folder.id}'
        ADMIN_FOLDER_URL: str = f'/{admin_folder.id}'

        def mock_get_current_user():
            return {
                'id': str(user.id),
                'username': user.username,
                'is_superuser': user.is_superuser
            }

        # Test response with not auth data
        response = await async_folder_client.delete(url=USER_FOLDER_1_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED # Not Auth
        assert response.json()['detail'] == 'Not authenticated'

        # Test response with not admin rights or not your own account
        app.dependency_overrides[get_current_user] = mock_get_current_user
        response = await async_folder_client.delete(url=ADMIN_FOLDER_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You don't have admin permission"
        assert await db_test.scalar(select(Folder).filter_by(id=admin_folder.id))

        # Test response with a not exist folder
        app.dependency_overrides[get_current_user] = mock_get_current_user
        response = await async_folder_client.delete(url=f'/{fake_uuid}')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['detail'] == "A folder with given id doesn't exist"


        # Test response with a positive test case
        app.dependency_overrides[get_current_user] = mock_get_current_user
        response = await async_folder_client.delete(url=USER_FOLDER_1_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == 'Folder has been successfully deleted'