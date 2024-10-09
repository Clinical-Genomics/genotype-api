from dataclasses import dataclass
from typing import Type

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeBase, Query
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from genotype_api.config import settings
from genotype_api.database.models import Analysis, Sample


@dataclass
class BaseHandler:
    """All queries in one base class."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_fixed(settings.retry_delay),
        retry=retry_if_exception_type(OperationalError),
        reraise=True,
    )
    def _get_query(self, table: Type[DeclarativeBase]) -> Query:
        """Return a query for the given table."""
        return select(table)

    def _get_join_analysis_on_sample(self) -> Query:
        return self._get_query(table=Sample).join(Analysis, Analysis.sample_id == Sample.id)
