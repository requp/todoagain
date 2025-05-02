from sqlalchemy import text, select, insert, update

from app.backend.db import async_engine, Base
# from app.models.models1 import Worker


class AsyncCoreQueries:
    @staticmethod
    async def get_version():
        async with async_engine.connect() as ac:
            res = await ac.execute(text('SELECT VERSION()'))
            print(f'{res.first()=}')
            # yield res

    # @staticmethod
    # async def create_tables():
    #     async with async_engine.begin() as conn:
    #         await conn.run_sync(Base.metadata.drop_all)
    #         await conn.run_sync(Base.metadata.create_all)
    #
    # @staticmethod
    # async def select_data():
    #     async with async_engine.begin() as ac:
    #         query = select(Worker).filter_by(id=1)
    #         res = await ac.execute(query)
    #         print(res.first())
    #
    # @staticmethod
    # async def insert_data():
    #     async with async_engine.connect() as ac:
    #         query = insert(Worker).values(username='Petr')
    #         await ac.execute(query)
    #         await ac.commit()
    #
    # @staticmethod
    # async def update_data():
    #     async with async_engine.connect() as ac:
    #         query = update(Worker).filter_by(username='Petr').values(username='Igor')
    #         await ac.execute(query)
    #         await ac.commit()
