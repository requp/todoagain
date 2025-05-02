
from uuid import UUID

from sqlalchemy import select

from app.backend.db import async_engine, Base, async_session_maker
from app.depends.model_depends.uuid_depends import get_uuid_or_str
from app.auth.model import User
from app.auth.schema import CreateUser, ShowUser
from app.auth.auth_router import bcrypt_context


async def get_async_db_conn():
    async with async_session_maker() as conn:
        yield conn

class AsyncUserQueries:
    @staticmethod
    async def load_data():
        users: list = [
            {
                'email': 'some_user@mail.ru',
                'username': 'some_user',
                'password': bcrypt_context.hash("Wrerew123456")
            },
            {
                'email': 'some_user1@mail.ru',
                'username': 'some_user1',
                'password': bcrypt_context.hash("Wrerew123456")
            },
            {
                'email': 'some_user2@mail.ru',
                'username': 'some_user2',
                'password': bcrypt_context.hash("Wrerew123456")
            },
        ]
        new_users: list = []
        async with async_session_maker() as conn:
            for user_data in users:
                target_user: User | None = await conn.scalar(select(User).filter_by(email=user_data['email']))
                if not target_user:
                    new_users.append(User(**user_data))
            if new_users:
                conn.add_all(new_users)
                await conn.commit()

    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def create_user(user_data: CreateUser) -> dict:
        print(user_data)
        new_user_data: dict = user_data.model_dump()
        new_user_data.pop('raw_password')
        new_user_data['password'] = bcrypt_context.hash(user_data.raw_password)
        res: dict = {}
        # conn = get_async_db_conn()
        async with async_session_maker() as conn:
            new_user: User = User(**new_user_data)
            conn.add(new_user)
            await conn.commit()
            user: User = await conn.scalar(
                select(User)
                .filter_by(email=user_data.email)
            )
            res = ShowUser(**user.__dict__).model_dump()
            await conn.delete(user)
            await conn.commit()
            print()
        return res

    @staticmethod
    async def create_users(
            users_data: list[CreateUser]
    ) -> list[User]:
        print(users_data)
        res: list[dict] = []
        new_users: list[User] = []
        all_new_users_emails: list = []
        for user_data in users_data:
            new_user_data: dict = user_data.model_dump()
            new_user_data.pop('raw_password')
            new_user_data['password'] = bcrypt_context.hash(user_data.raw_password)
            new_user: User = User(**new_user_data)
            if 'admin' in new_user.fullname.lower():
                new_user.is_superuser = True
            new_users.append(new_user)
            all_new_users_emails.append(user_data.email)
        async with async_session_maker() as conn:
            conn.add_all(new_users)
            await conn.commit()
            # res = [ShowUser(**user.__dict__).model_dump() for user in users]
        return new_users

    @staticmethod
    async def show_user(id_or_username: str):
        uuid_or_str: UUID | str = await get_uuid_or_str(id_or_username)
        async with async_session_maker() as conn:
            user: User | None = None
            if isinstance(uuid_or_str, UUID):
                user = await conn.get(User, id_or_username)
            elif isinstance(uuid_or_str, str):
                user = await conn.scalar(select(User).filter_by(username=id_or_username))
            if user:
                res = ShowUser(**user.__dict__)
                return res.model_dump()

    @staticmethod
    async def update_user(user_id: UUID):
        pass

    @staticmethod
    async def delete_user(user_id: UUID):
        pass