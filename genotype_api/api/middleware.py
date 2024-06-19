import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from genotype_api.database.database import close_session, rollback_transactions

LOG = logging.getLogger(__name__)


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        try:
            LOG.error("Opening dispatching request")
            response = await call_next(request)
        except Exception as error:
            LOG.error(f"Caught exception: {error}")
            rollback_transactions()
            raise error
        finally:
            close_session()
        return response
