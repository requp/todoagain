import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.model import User


class TestCreateUser:
    """Test a route for creating account"""

    @pytest.mark.asyncio
    async def test_create_user_positive(
            self,
            async_user_client: AsyncClient,
            db_test: AsyncSession,
            user_data: dict
    ) -> None:
        """Test create user positive test case"""


        assert await db_test.scalar(
            select(User).filter_by(username=user_data["username"])
        ) is None

        response = await async_user_client.post("/", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert await db_test.scalar(
            select(User).filter_by(username=user_data["username"])
        )


    @pytest.mark.asyncio
    async def test_create_user_with_taken_username(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            user_data: dict,
            mock_get_current_user_1,
            user_1: User,
    ) -> None:
        """Test response with taken username"""

        user_data["username"] = user_1.username
        response = await async_user_client.post(url="/", json=user_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "This username is already taken"


    @pytest.mark.asyncio
    async def test_create_user_with_taken_email(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            user_data: dict,
            mock_get_current_user_2,
            user_1: User,
    ) -> None:
        """Test response with taken email"""

        user_data["email"] = user_1.email
        response = await async_user_client.post(url="/", json=user_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "This email is already taken"
