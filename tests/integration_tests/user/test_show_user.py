import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.model import User


class TestShowUser:
    """Test a route for showing an account"""

    @pytest.mark.asyncio
    async def test_show_user_not_auth(
            self,
            async_user_client: AsyncClient,
            user_1_url,
    ) -> None:
        """Test response with not auth data"""

        response = await async_user_client.get(url=user_1_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        json_result: dict = response.json()
        assert json_result["detail"] == "Not authenticated"
        assert "data" not in json_result


    @pytest.mark.asyncio
    async def test_show_user_not_exist(
            self,
            async_user_client: AsyncClient,
            fake_uuid: str,
            mock_get_current_user_1
    ) -> None:
        """Test response with not exist user"""

        response = await async_user_client.get(url=f"/{fake_uuid}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "An user with given id doesn't exist"


    @pytest.mark.asyncio
    async def test_show_user_positive_with_user_id(
            self,
            async_user_client: AsyncClient,
            db_test: AsyncSession,
            mock_get_current_user_1,
            user_1,
            user_1_url
    ) -> None:
        """Test create user positive test case"""

        response = await async_user_client.get(url=user_1_url)
        assert response.status_code == status.HTTP_200_OK
        user_data: dict = response.json()
        assert user_data["detail"] == "Successful"
        assert user_data["data"]["username"] == user_1.username
        assert user_data["data"]["email"] == user_1.email


    @pytest.mark.asyncio
    async def test_show_user_positive_with_user_username(
            self,
            async_user_client: AsyncClient,
            db_test: AsyncSession,
            mock_get_current_user_1,
            user_1
    ) -> None:
        """Test create user positive test case"""

        response = await async_user_client.get(url=f"/{user_1.username}")
        assert response.status_code == status.HTTP_200_OK
        user_data: dict = response.json()
        assert user_data["detail"] == "Successful"
        assert user_data["data"]["username"] == user_1.username
        assert user_data["data"]["email"] == user_1.email