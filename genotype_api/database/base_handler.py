from dataclasses import dataclass
from typing import Any, List, Type, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeBase, Query

from genotype_api.database.models import Analysis, Sample


@dataclass
class BaseHandler:
    """All queries in one base class."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _get_query(self, table: Type[DeclarativeBase]) -> Query:
        """Return a query for the given table."""
        return select(table)

    def _get_join_analysis_on_sample(self) -> Query:
        return self._get_query(table=Sample).join(Analysis, Analysis.sample_id == Sample.id)

    # Full row fetch methods
    async def fetch_all_rows(self, query: Query) -> List[DeclarativeBase]:
        """Fetch all full rows matching the query."""
        result = await self.session.execute(query)
        return result.scalars().all()

    async def fetch_first_row(self, query: Query) -> DeclarativeBase | None:
        """Fetch the first full row matching the query or None if no match found."""
        result = await self.session.execute(query)
        return result.scalars().first()

    async def fetch_one_or_none(self, query: Query) -> DeclarativeBase | None:
        """Fetch one full row or None if no match found."""
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    # Scalar value fetch methods
    async def fetch_column_values(self, query: Query) -> List:
        """Fetch all values from a single column."""
        result = await self.session.execute(query)
        return result.all()

    async def fetch_first_value(self, query: Query) -> Any | None:
        """Fetch the first value from a single column or None if no match found."""
        result = await self.session.execute(query)
        return result.first()

    async def fetch_one_value_or_none(self, query: Query) -> Any | None:
        """Fetch one value from a single column or None if no match found."""
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def fetch_one_value(self, query: Query) -> Any:
        """Fetch exactly one value from a single column or raise an error if not found."""
        result = await self.session.execute(query)
        return result.scalar_one()
