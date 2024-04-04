from dataclasses import dataclass

from sqlalchemy.orm import Session


@dataclass
class BaseHandler:
    """All queries in one base class."""

    def __init__(self, session: Session):
        self.session = session
