from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from database.base import Base
from utils.config import settings


engine = create_async_engine(
    url=settings.get_url_database,
    echo=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

async_session = AsyncSession(bind=engine)

async def get_db():
    async with async_session as session:
        yield session