from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from genotype_api.database.database import close_session
import logging

logger = logging.getLogger(__name__)


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        logger.info("Initialising DBSessionMiddleware")
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        try:
            logger.info("In dispatch")
            response = await call_next(request)
        finally:
            logger.info("Closing session")
            close_session()
        return response
