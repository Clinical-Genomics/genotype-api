from dataclasses import dataclass
from typing import Type

from sqlalchemy.orm import Session, DeclarativeBase, Query


@dataclass
class BaseHandler:
    """All queries in one base class."""

    def __init__(self, session: Session):
        self.session = session

    def _get_query(self, table: Type[DeclarativeBase]) -> Query:
        """Return a query for the given table."""
        return self.session.query(table)
