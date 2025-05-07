import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.auth_router import get_current_user
from app.auth.model import User
from app.main import app
from app.todo.folder.model import Folder


class TestDeleteFolder:
    """Test a route for deleting all user's folders"""

    @pytest.mark.asyncio
    async def test_delete_folder_not_auth(
            self,
            async_folder_client: AsyncClient,
            user_folder_url: str
    ) -> None:
        """Test response with not auth data"""

        response = await async_folder_client.delete(url=user_folder_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()['detail'] == 'Not authenticated'


    @pytest.mark.asyncio
    async def test_delete_folder_not_exist(
            self,
            async_folder_client: AsyncClient,
            mock_get_current_user_1,
            fake_uuid: str
    ) -> None:
        """Test response with a not exist folder"""

        response = await async_folder_client.delete(url=f'/{fake_uuid}')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['detail'] == "A folder with given id doesn't exist"


    @pytest.mark.asyncio
    async def test_delete_folder_other_user_folder_by_user(
            self,
            async_folder_client: AsyncClient,
            admin_folder_url: str,
            mock_get_current_user_1,
            db_test: AsyncSession,
            admin_folder: Folder
    ) -> None:
        """Test response with not admin rights or not your own account"""

        response = await async_folder_client.delete(url=admin_folder_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['detail'] == "You don't have admin permission"
        assert await db_test.scalar(
            select(Folder).filter_by(id=admin_folder.id)
        )


    @pytest.mark.asyncio
    async def test_delete_folder_positive(
            self,
            async_folder_client: AsyncClient,
            user_nested_nested_folder_url: str,
            mock_get_current_user_1,
            db_test: AsyncSession,
            user_nested_nested_folder: Folder
    ) -> None:
        """Test response with a positive test case"""

        response = await async_folder_client.delete(url=user_nested_nested_folder_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == 'Folder has been successfully deleted'

        assert await db_test.scalar(select(Folder).filter_by(id=user_nested_nested_folder.id)) is None


    @pytest.mark.asyncio
    async def test_delete_folder_positive_other_user_by_admin(
            self,
            async_folder_client: AsyncClient,
            user_nested_nested_folder_url: str,
            mock_get_current_admin_1,
            db_test: AsyncSession,
            user_nested_nested_folder: Folder
    ) -> None:
        """
        Test response with a positive test case of deleting
        other user's folder by admin
        """

        response = await async_folder_client.delete(url=user_nested_nested_folder_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == 'Folder has been successfully deleted'

        assert await db_test.scalar(select(Folder).filter_by(id=user_nested_nested_folder.id)) is None


    @pytest.mark.asyncio
    async def test_delete_folder_positive_children_folder_deleting(
            self,
            async_folder_client: AsyncClient,
            user_folder_url: str,
            mock_get_current_user_1,
            db_test: AsyncSession,
            user_1: User
    ) -> None:
        """Test response with a positive with Cascade delete of user folder's children"""

        all_user_folders: list[Folder] = list(
           await db_test.scalars(select(Folder).filter_by(user_id=user_1.id))
        )
        assert len(all_user_folders) == 3

        response = await async_folder_client.delete(url=user_folder_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == 'Folder has been successfully deleted'

        all_user_folders = list(
            await db_test.scalars(select(Folder).filter_by(user_id=user_1.id))
        )
        assert len(all_user_folders) == 0
