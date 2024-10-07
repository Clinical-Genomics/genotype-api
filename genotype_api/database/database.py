"""Hold the database information and session manager."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from genotype_api.config import settings
from genotype_api.database.models import Base

LOG = logging.getLogger(__name__)

engine = create_async_engine(
    settings.db_uri,
    echo=settings.echo_sql,
    future=True,
    pool_size=10,
    max_overflow=20,
)

sessionmanager = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides an asynchronous session context manager with retry logic."""
    retries = 0
    while retries < settings.max_retries:
        async with sessionmanager() as session:
            try:
                yield session
                break
            except OperationalError as e:
                retries += 1
                LOG.error(f"OperationalError: {e}, retrying {retries}/{settings.max_retries}...")
                if retries >= settings.max_retries:
                    LOG.error("Max retries exceeded. Could not connect to the database.")
                    raise
                await session.close()
                await asyncio.sleep(settings.retry_delay)
            finally:
                await session.close()


async def create_all_tables():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables():
    """Drop all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.drop_all)
