from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.backend.config import settings

# with sync_engine.connect() as conn:
#     res = conn.execute(text('SELECT VERSION()'))
#     print(f'{res=}')
#

sync_engine = create_engine(
    url=settings.DATABASE_URL_sync,
    echo=True
)


async_engine = create_async_engine(
    url=settings.DATABASE_URL_async,
    echo=True
)

async_session_maker = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

class Base(DeclarativeBase):
    pass