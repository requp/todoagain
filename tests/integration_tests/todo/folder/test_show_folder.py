import pytest
from httpx import AsyncClient
from starlette import status

from app.auth.auth_router import get_current_user
from app.auth.model import User
from app.main import app
from app.todo.folder.model import Folder


class TestShowFolder:
    """Test a route for showing a folder data"""

    @pytest.mark.asyncio
    async def test_show_folder_not_auth(
            self,
            async_folder_client: AsyncClient,
            user_1: User,
            user_folder_url: str
    ) -> None:
        """Test response with not auth data"""

        response = await async_folder_client.get(url=user_folder_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"


    @pytest.mark.asyncio
    async def test_show_folder_positive(
            self,
            async_folder_client: AsyncClient,
            user_1: User,
            user_folder_url: str,
            mock_get_current_user_1,
            user_folder: Folder
    ) -> None:
        """Test response with a positive test case"""

        response = await async_folder_client.get(url=user_folder_url)
        assert response.status_code == status.HTTP_200_OK
        json_data: dict = response.json()
        assert json_data["detail"] == "Successful"
        assert json_data["data"]["id"] == str(user_folder.id)


    @pytest.mark.asyncio
    async def test_show_folder_positive_admin_see_private_folder(
            self,
            async_folder_client: AsyncClient,
            user_1: User,
            user_folder_url: str,
            mock_get_current_admin_1,
            user_folder: Folder
    ) -> None:
        """
        Test response with a positive test case
        with admin with user's private folder
        """
        assert user_folder.is_private
        response = await async_folder_client.get(url=user_folder_url)
        assert response.status_code == status.HTTP_200_OK
        json_data: dict = response.json()
        assert json_data["detail"] == "Successful"
        assert json_data["data"]["id"] == str(user_folder.id)


    @pytest.mark.asyncio
    async def test_show_folder_private_folder(
            self,
            async_folder_client: AsyncClient,
            user_1: User,
            admin_folder_url: str,
            mock_get_current_user_1,
            admin_folder: Folder
    ) -> None:
        """
        Test response with a user trying to see other user's private folder
        """
        assert admin_folder.is_private
        response = await async_folder_client.get(url=admin_folder_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You can't see a private folder of other user"


    @pytest.mark.asyncio
    async def test_show_folder_not_exist(
            self,
            async_folder_client: AsyncClient,
            user_1: User,
            mock_get_current_user_1,
            fake_uuid: str
    ) -> None:
        """
        Test response with not exist folder
        """

        response = await async_folder_client.get(url=f"/{fake_uuid}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "A folder with given id doesn't exist"
