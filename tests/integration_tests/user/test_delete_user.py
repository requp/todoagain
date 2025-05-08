import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.model import User


class TestDeleteUser:
    """Test a route for deleting (making inactive) an account"""


    @pytest.mark.asyncio
    async def test_delete_user_not_auth(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            updated_fields: dict,
            user_1: User,
            db_test: AsyncSession
    ) -> None:
        """Test response with not auth data"""
        response = await async_user_client.delete(url=user_1_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"
        await db_test.refresh(user_1)
        assert user_1.is_active == True


    @pytest.mark.asyncio
    async def test_delete_user_not_exist(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            updated_fields: dict,
            mock_get_current_admin_1,
            fake_uuid: str,
            db_test: AsyncSession
    ) -> None:
        """Test response when user doesn't exist"""

        response = await async_user_client.delete(url=f"/{fake_uuid}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "An user with given id doesn't exist"


    @pytest.mark.asyncio
    async def test_delete_user_other_user_by_user(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            updated_fields: dict,
            mock_get_current_user_2,
            user_1: User,
            db_test: AsyncSession
    ) -> None:
        """Test response with not admin rights or not your own account"""

        assert user_1.is_active
        response = await async_user_client.delete(url=user_1_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You don't have admin permission"
        await db_test.refresh(user_1)
        assert user_1.is_active


    @pytest.mark.asyncio
    async def test_delete_user_other_admin_by_admin(
            self,
            async_user_client: AsyncClient,
            admin_1_url: str,
            updated_fields: dict,
            mock_get_current_admin_2,
            admin_1: User,
            db_test: AsyncSession
    ) -> None:
        """Test response when tries to delete an admin account"""

        assert admin_1.is_active == True
        response = await async_user_client.delete(url=admin_1_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You can't delete other admin's data"
        await db_test.refresh(admin_1)
        assert admin_1.is_active == True


    @pytest.mark.asyncio
    async def test_delete_user_positive_user_by_admin(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            updated_fields: dict,
            mock_get_current_admin_2,
            user_1: User,
            db_test: AsyncSession
    ) -> None:
        """Test response with a positive test case by admin"""

        assert user_1.is_active
        response = await async_user_client.delete(url=user_1_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "User has been successfully deleted"
        await db_test.refresh(user_1)
        assert user_1.is_active == False


    @pytest.mark.asyncio
    async def test_delete_user_positive(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            updated_fields: dict,
            mock_get_current_user_1,
            user_1: User,
            db_test: AsyncSession
    ) -> None:
        """Test response with a positive test"""

        assert user_1.is_active
        response = await async_user_client.delete(url=user_1_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "User has been successfully deleted"
        await db_test.refresh(user_1)
        assert user_1.is_active == False


    @pytest.mark.asyncio
    async def test_delete_user_already_deleted(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            updated_fields: dict,
            mock_get_current_admin_1,
            user_1: User,
            db_test: AsyncSession
    ) -> None:
        """Test response when user already inactive"""

        user_1.is_active = False
        await db_test.commit()
        assert user_1.is_active == False
        response = await async_user_client.delete(url=user_1_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "User already has been deleted"
