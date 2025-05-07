import pytest
from httpx import AsyncClient
from starlette import status

from app.auth.auth_router import get_current_user
from app.auth.model import User
from app.main import app
from app.todo.folder.model import Folder


class TestListFolder:
    """Test a route for listing all user's folders"""

    @pytest.mark.asyncio
    async def test_list_folders_not_auth(
            self, async_folder_client: AsyncClient
    ) -> None:
        """Test response with not auth data"""

        response = await async_folder_client.get(url='/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()['detail'] == 'Not authenticated'


    @pytest.mark.asyncio
    async def test_list_folders_positive(
            self,
            async_folder_client: AsyncClient,
            mock_get_current_user_1,
            folders: list[Folder]
    ) -> None:
        """Test response with a positive test case"""

        response = await async_folder_client.get(url='/')
        assert response.status_code == status.HTTP_200_OK
        json_data: dict = response.json()
        assert json_data['detail'] == 'Successful'
        assert isinstance(json_data['data'], list)
        assert len(json_data['data']) == 3