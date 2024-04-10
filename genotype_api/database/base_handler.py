from dataclasses import dataclass
from typing import Type
from sqlalchemy.orm import Session, Query, DeclarativeBase
from genotype_api.database.models import Analysis, Sample


@dataclass
class BaseHandler:
    """All queries in one base class."""

    def __init__(self, session: Session):
        self.session = session

    def _get_query(self, table: Type[DeclarativeBase]) -> Query:
        """Return a query for the given table."""
        return self.session.query(table)

    def _get_join_analysis_on_sample(self) -> Query:
        return self._get_query(table=Sample).join(Analysis)
