import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.auth_router import get_current_user
from app.main import app
from app.todo.folder.model import Folder


class TestUpdateFolder:
    """Test a route for updating all user's folders"""

    @pytest.mark.asyncio
    async def test_update_folder_not_exist(
            self,
            async_folder_client: AsyncClient,
            folder_update_data: dict,
            mock_get_current_user_1,
            db_test: AsyncSession,
            fake_uuid: str
    ) -> None:
        """Test response with a not exist folder"""

        response = await async_folder_client.put(url=f"/{fake_uuid}", json=folder_update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "A folder with given id doesn't exist"


    @pytest.mark.asyncio
    async def test_update_folder_not_auth(
            self,
            async_folder_client: AsyncClient,
            folder_update_data: dict,
            user_folder_url: str
    ) -> None:
        """Test response with not auth data"""

        response = await async_folder_client.put(url=user_folder_url, json=folder_update_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"


    @pytest.mark.asyncio
    async def test_update_folder_other_user_folder_by_user(
            self,
            async_folder_client: AsyncClient,
            folder_update_data: dict,
            admin_folder_url: str,
            mock_get_current_user_1,
            db_test: AsyncSession,
            admin_folder: Folder
    ) -> None:
        """Test response with not admin rights or not your own account"""

        response = await async_folder_client.put(url=admin_folder_url, json=folder_update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        json_data: dict = response.json()
        assert json_data["detail"] == "You don't have admin permission"
        await db_test.refresh(admin_folder)
        assert admin_folder.description != folder_update_data["description"]


    @pytest.mark.asyncio
    async def test_update_folder_positive_other_user_folder_by_admin(
            self,
            async_folder_client: AsyncClient,
            folder_update_data: dict,
            user_folder_url: str,
            mock_get_current_admin_1,
            db_test: AsyncSession,
            user_folder: Folder
    ) -> None:
        """Test response with positive case of admin account on user"""

        assert user_folder.description != folder_update_data["description"]
        response = await async_folder_client.put(url=user_folder_url, json=folder_update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "Folder has been successfully updated"
        await db_test.refresh(user_folder)
        assert user_folder.description == folder_update_data["description"]


    @pytest.mark.asyncio
    async def test_update_folder_positive(
            self,
            async_folder_client: AsyncClient,
            user_nested_nested_folder_url: str,
            mock_get_current_user_1,
            db_test: AsyncSession,
            user_folder: Folder,
            user_nested_nested_folder: Folder,
            user_nested_folder: Folder
    ) -> None:
        """Test response with positive case"""


        assert user_nested_nested_folder.parent_id == user_nested_folder.id
        assert user_nested_nested_folder.name == "Nested Nested User Folder"

        new_update_data: dict = {
            "parent_id": str(user_folder.id),
            "name": "Second nested user folder"
        }
        response = await async_folder_client.put(url=user_nested_nested_folder_url, json=new_update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "Folder has been successfully updated"

        await db_test.refresh(user_nested_nested_folder)
        assert user_nested_nested_folder.parent_id == user_folder.id
        assert user_nested_nested_folder.name == "Second nested user folder"


    @pytest.mark.asyncio
    async def test_update_folder_taken_name_by_user(
            self,
            async_folder_client: AsyncClient,
            folder_update_data: dict,
            user_nested_folder_url: str,
            mock_get_current_user_1,
            db_test: AsyncSession,
            user_folder: Folder,
            user_nested_folder
    ) -> None:
        """Test response with taken folder's name by user"""

        assert user_nested_folder.name != user_folder.name

        folder_update_data["name"] = user_folder.name
        response = await async_folder_client.put(url=user_nested_folder_url, json=folder_update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You can't update a folder with the same name which you already have"

        await db_test.refresh(user_nested_folder)
        assert user_nested_folder.name != user_folder.name


    @pytest.mark.asyncio
    async def test_update_folder_other_user_parent_id_by_user(
            self,
            async_folder_client: AsyncClient,
            user_nested_nested_folder_url: str,
            mock_get_current_user_1,
            db_test: AsyncSession,
            admin_folder: Folder,
            user_nested_nested_folder: Folder,
            user_nested_folder: Folder
    ) -> None:
        """Test response with update other folder parent_id by user"""

        assert user_nested_nested_folder.parent_id == user_nested_folder.id
        assert user_nested_nested_folder.name == "Nested Nested User Folder"

        nested_folder_data: dict = {
            "name": "A folder inside of other folder",
            "parent_id": str(admin_folder.id)
        }
        response = await async_folder_client.put(url=user_nested_nested_folder_url, json=nested_folder_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You can't update a nested folder with the other user's folder"

        await db_test.refresh(user_nested_nested_folder)
        assert user_nested_nested_folder.parent_id == user_nested_folder.id
        assert user_nested_nested_folder.name == "Nested Nested User Folder"
