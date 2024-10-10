"""Hold the database information and session manager."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from genotype_api.config import settings
from genotype_api.database.models import Base

LOG = logging.getLogger(__name__)

engine = create_async_engine(
    settings.db_uri,
    echo=settings.echo_sql,
    future=True,
    pool_recycle=3600,  # Recycle connections after 3600 seconds (1 hour)
    pool_pre_ping=True,  # Enable connection health checks (pings)
)

sessionmanager = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@retry(
    stop=stop_after_attempt(settings.max_retries),
    wait=wait_fixed(settings.retry_delay),
    retry=retry_if_exception_type(OperationalError),
    reraise=True,
)
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a valid database session with retry logic for OperationalError."""
    async with sessionmanager() as session:
        try:
            # Test if the session is still valid by executing a simple query
            await session.execute(text("SELECT 1"))
            yield session
        except OperationalError as e:
            # If session is invalid, retry
            LOG.error(f"OperationalError: {e}")
            raise


async def create_all_tables():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables():
    """Drop all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
