
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.auth_router import get_current_user
from app.auth.model import User
from app.main import app
from app.todo.folder.model import Folder


class TestCreateFolder:
    """Test a route for creating account"""


    @pytest.mark.asyncio
    async def test_create_folder_not_auth(
            self,
            async_folder_client: AsyncClient,
            folder_data: dict
    ):
        """Test response with not auth data"""

        response = await async_folder_client.post(url='/', json=folder_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()['detail'] == 'Not authenticated'


    @pytest.mark.asyncio
    async def test_create_folder_positive(
            self,
            async_folder_client: AsyncClient,
            folder_data: dict,
            mock_get_current_user_1,
            nested_folder_data: dict,
            folders: list[Folder]
    ):
        """Test response with a positive test case"""

        response = await async_folder_client.post(url='/', json=folder_data)
        assert response.status_code == status.HTTP_201_CREATED
        json_data: dict = response.json()
        assert json_data['detail'] == 'Successful'
        nested_folder_data['parent_id'] = json_data['data']['id']


    @pytest.mark.asyncio
    async def test_create_folder_positive_nested_folder(
            self,
            async_folder_client: AsyncClient,
            nested_folder_data: dict,
            folders: list[Folder],
            mock_get_current_user_1,
            user_1: User,
            folder_data: dict,
            db_test: AsyncSession
    ):
        """Test response with a positive test case of a nested folder"""

        # Create a folder with some text as name by user_1
        new_folder: Folder = Folder(
            **folder_data, user_id=user_1.id
        )
        db_test.add(new_folder)
        await db_test.commit()

        # Create a naster folder with paren_id as new_folder by user_1 with success
        nested_folder_data['parent_id'] = str(new_folder.id)
        response = await async_folder_client.post(url='/', json=nested_folder_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['detail'] == 'Successful'


    @pytest.mark.asyncio
    async def test_create_folder_taken_by_user(
            self,
            async_folder_client: AsyncClient,
            folder_data: dict,
            folders: list[Folder],
            user_1: User,
            mock_get_current_user_1,
            db_test: AsyncSession
    ):
        """Test response with creating a folder with the same name and the same user"""

        # Create a folder with some text as name by user_1
        new_folder: Folder = Folder(
            **folder_data, user_id=user_1.id
        )
        db_test.add(new_folder)
        await db_test.commit()

        # Trying to create a folder with the same text as name by the same user_1
        response = await async_folder_client.post(url='/', json=folder_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You can't create a folder with the same name which you already have"


    @pytest.mark.asyncio
    async def test_create_folder_positive_the_same_name_by_other_user(
            self,
            async_folder_client: AsyncClient,
            folder_data: dict,
            folders: list[Folder],
            user_1: User,
            mock_get_current_user_2,
            db_test: AsyncSession
    ):
        """Test response with a positive test case of the same folder's name but other user"""

        # Create a folder with some text as name by user_1
        new_folder: Folder = Folder(
            **folder_data, user_id=user_1.id
        )
        db_test.add(new_folder)
        await db_test.commit()

        # Create a folder with the same text as name but by user_2 with success
        response = await async_folder_client.post(url='/', json=folder_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['detail'] == 'Successful'


    @pytest.mark.asyncio
    async def test_create_folder_other_user_in_parent_id(
            self,
            async_folder_client: AsyncClient,
            folder_data: dict,
            folders: list[Folder],
            user_1: User,
            mock_get_current_user_2,
            db_test: AsyncSession,
            nested_folder_data: dict
    ):
        """Test response with a nested folder of other user's id"""

        # Make a folder with user_1 id
        new_folder: Folder = Folder(
            **folder_data, user_id=user_1.id
        )
        db_test.add(new_folder)
        await db_test.commit()

        # Trying to create a folder for user_2 with user_1 folder id as a parent
        nested_folder_data['parent_id'] = str(new_folder.id)
        response = await async_folder_client.post(url='/', json=nested_folder_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You can't create a nested folder with the other user's folder"


    @pytest.mark.asyncio
    async def test_create_folder_not_exist_in_parent_id(
            self,
            async_folder_client: AsyncClient,
            folder_data: dict,
            folders: list[Folder],
            mock_get_current_user_1,
            db_test: AsyncSession,
            nested_folder_data: dict,
            fake_uuid: str
    ):
        """Test response with a nested folder with no exist id"""

        nested_folder_data['parent_id'] = fake_uuid
        response = await async_folder_client.post(url='/', json=nested_folder_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['detail'] == "Given parent_id folder doesn't exist"
