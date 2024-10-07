"""Module for the store handler."""

from sqlalchemy.ext.asyncio import AsyncSession

from genotype_api.database.crud.create import CreateHandler
from genotype_api.database.crud.delete import DeleteHandler
from genotype_api.database.crud.read import ReadHandler
from genotype_api.database.crud.update import UpdateHandler
from genotype_api.database.database import get_session


class Store(
    CreateHandler,
    DeleteHandler,
    ReadHandler,
    UpdateHandler,
):
    def __init__(self, session: AsyncSession):
        """Initialize the Store with an active database session."""
        self.session = session
        CreateHandler.__init__(self, session)
        DeleteHandler.__init__(self, session)
        ReadHandler.__init__(self, session)
        UpdateHandler.__init__(self, session)

    @classmethod
    async def create(cls) -> "Store":
        """Asynchronously create and return a Store instance with a session."""
        async with get_session() as session:  # Correctly use async context manager
            return cls(session)  # Return a Store instance with the session


async def get_store() -> Store:
    """Return a Store instance."""
    store = await Store.create()
    try:
        yield store  # Yield the store for the duration of the request
    finally:
        await store.session.close()
