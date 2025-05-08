import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.model import User


class TestUpdateUser:
    """Test a route for updating an account"""

    @pytest.mark.asyncio
    async def test_update_user_not_exist(
            self,
            async_user_client: AsyncClient,
            fake_uuid: str,
            mock_get_current_user_1,
            updated_fields
    ) -> None:
        """Test response with not exist user"""

        response = await async_user_client.put(url=f"/{fake_uuid}", json=updated_fields)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "An user with given id doesn't exist"


    @pytest.mark.asyncio
    async def test_update_user_not_auth(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            updated_fields: dict,
            user_1: User,
            db_test: AsyncSession
    ) -> None:
        """Test response with not auth data"""

        assert user_1.username != updated_fields["username"]
        response = await async_user_client.put(url=user_1_url, json=updated_fields)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"
        await db_test.refresh(user_1)
        assert user_1.username != updated_fields["username"]


    @pytest.mark.asyncio
    async def test_update_user_positive(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            updated_fields: dict,
            mock_get_current_user_1,
            user_1: User,
            db_test: AsyncSession
    ) -> None:
        """Test response with a positive test case"""

        assert user_1.fullname != updated_fields["fullname"]
        response = await async_user_client.put(url=user_1_url, json=updated_fields)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "User has been successfully updated"
        await db_test.refresh(user_1)
        assert user_1.fullname == updated_fields["fullname"]
        assert user_1.username == updated_fields["username"]

    @pytest.mark.asyncio
    async def test_update_user_other_user_by_user(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            updated_fields: dict,
            mock_get_current_user_2,
            user_1: User,
            db_test: AsyncSession
    ) -> None:
        """Test response with not admin rights or not your own account"""

        assert user_1.fullname != updated_fields["fullname"]
        response = await async_user_client.put(url=user_1_url, json=updated_fields)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You don't have admin permission"
        await db_test.refresh(user_1)
        assert user_1.fullname != updated_fields["fullname"]


    @pytest.mark.asyncio
    async def test_update_user_other_admin_by_admin(
            self,
            async_user_client: AsyncClient,
            admin_1_url: str,
            updated_fields: dict,
            mock_get_current_admin_2,
            admin_1: User,
            db_test: AsyncSession
    ) -> None:
        """Test response with not admin rights or not your own account"""

        assert admin_1.fullname != updated_fields["fullname"]
        response = await async_user_client.put(url=admin_1_url, json=updated_fields)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You can't update other admin's data"
        await db_test.refresh(admin_1)
        assert admin_1.fullname != updated_fields["fullname"]


    @pytest.mark.asyncio
    async def test_update_user_positive_other_user_by_admin(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            updated_fields: dict,
            mock_get_current_admin_1,
            user_1: User,
            db_test: AsyncSession
    ) -> None:
        """Test response with not admin rights or not your own account"""

        assert user_1.fullname != updated_fields["fullname"]
        response = await async_user_client.put(url=user_1_url, json=updated_fields)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "User has been successfully updated"
        await db_test.refresh(user_1)
        assert user_1.fullname == updated_fields["fullname"]
        assert user_1.username == updated_fields["username"]


    @pytest.mark.asyncio
    async def test_update_user_with_take_username(
            self,
            async_user_client: AsyncClient,
            user_1_url: str,
            updated_fields: dict,
            mock_get_current_user_1,
            user_1: User,
            db_test: AsyncSession,
            user_2: User
    ) -> None:
        """Test response with taken username"""

        assert user_1.username != updated_fields["username"]
        updated_fields["username"] = user_2.username
        response = await async_user_client.put(url=user_1_url, json=updated_fields)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "This username is already taken"
        await db_test.refresh(user_1)
        assert user_1.username != updated_fields["username"]

