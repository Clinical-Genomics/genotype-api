"""Module for the store handler."""

from sqlalchemy.orm import Session

from genotype_api.config import DBSettings
from genotype_api.database.crud.create import CreateHandler
from genotype_api.database.crud.delete import DeleteHandler
from genotype_api.database.crud.read import ReadHandler
from genotype_api.database.crud.update import UpdateHandler
from genotype_api.database.database import get_session, initialise_database


class Store(
    CreateHandler,
    DeleteHandler,
    ReadHandler,
    UpdateHandler,
):
    def __init__(self):
        self.session: Session = get_session()
        DeleteHandler(self.session)
        ReadHandler(self.session)
        UpdateHandler(self.session)


def get_store() -> Store:
    """Return a store."""
    return Store()
