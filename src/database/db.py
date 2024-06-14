import contextlib
import logging
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)

from src.config.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataBaseSessionManager:
    def __init__(self, url: str):
        # self._engine: AsyncEngine | None = create_async_engine(url)
        self._engine: Optional[AsyncEngine] = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine, class_=AsyncSession
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except HTTPException as err:
            raise err
        except Exception as err:
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DataBaseSessionManager(config.DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session
