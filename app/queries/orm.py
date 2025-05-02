from sqlalchemy import select, func, cast, Integer, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db import async_session_maker


# async def get_db() -> AsyncSession:
#     async with async_session_maker() as ac:
#         yield ac
class AsyncOrmQueries:

    @staticmethod
    async def insert_data():
        new_workers: list[Worker] = [Worker(username='test6'), Worker(username='Vlad')]
        async with async_session_maker() as ac:
            ac.add_all(new_workers)
            await ac.commit()

    @staticmethod
    async def select_data():
        async with async_session_maker() as ac:
            res = await ac.scalar(select(Worker).filter_by(id=1))
            print(res.username)

    @staticmethod
    async def update_data():
        # ac = get_db()
        # user: Worker | None = await ac.get(Worker, 1)
        # user.username = 'Bob'
        # await ac.commit()
        async with async_session_maker() as ac:
            user: Worker = await ac.get(Worker, 1)
            user.username = 'Bob'
            await ac.commit()

    @staticmethod
    async def load_resumes():
        resumes_data: list = [
            {
                'title': 'Python Junior',
                'compensation': 50000,
                'workload': 'fulltime',
                'worker_id': 1
            },
            {
                'title': 'Python Middle',
                'compensation': 100000,
                'workload': 'fulltime',
                'worker_id': 1
            },
            {
                'title': 'Python Senior',
                'compensation': 250000,
                'workload': 'fulltime',
                'worker_id': 3
            },
            {
                'title': 'Python Super Dev',
                'compensation': 600000,
                'workload': 'fulltime',
                'worker_id': 3
            },
            {
                'title': 'Python Super Part',
                'compensation': 200000,
                'workload': 'parttime',
                'worker_id': 2
            },
            {
                'title': 'Python Middle Part',
                'compensation': 90000,
                'workload': 'parttime',
                'worker_id': 2
            },
        ]
        async with async_session_maker() as ac:
            resumes: list[Resume] = [Resume(**data) for data in resumes_data]
            ac.add_all(resumes)
            await ac.commit()

    @staticmethod
    async def select_resumes_avg_comp(like_lang: str = 'Python'):
        """
            select workload, avg(compensation)::int as avg_comp
            from resumes
            where title like '%Python%' and compensation > 60000
            group by "workload"
        """
        async with async_session_maker() as ac:
            query = (
                select(
                    Resume.workload,
                    cast(func.avg(Resume.compensation), Integer).label('avg_comp')
                )
                .select_from(Resume)
                .filter(
                    and_(Resume.title.contains(like_lang)),
                    Resume.compensation > 40000
                )
                .group_by(Resume.workload)
            )
            print(query.compile(compile_kwargs={'literal_binds': True}))
            res = await ac.execute(query)
            print(res.all())
