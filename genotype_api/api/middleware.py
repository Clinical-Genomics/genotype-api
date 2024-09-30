import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, PendingRollbackError
from starlette.middleware.base import BaseHTTPMiddleware

from genotype_api.database.database import close_session, get_session
from genotype_api.exceptions import GenotypeDBError

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        session = get_session()
        if session is None:
            LOG.info("No database session found.")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Internal server error: No database session."},
            )

        # Ensure session is clean before processing the request
        if not session.is_active:
            LOG.info("Session not active, rolling back any uncommitted transactions.")

        try:
            response = await call_next(request)

            if session.dirty:
                session.flush()

            return response

        except PendingRollbackError:
            LOG.info("Pending rollback error, rolling back session", exc_info=True)
            if session.is_active:
                session.rollback()
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Internal server error: Pending rollback."},
            )

        except OperationalError:
            LOG.info("Operational error: database connection lost", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Internal server error: Database connection lost."},
            )

        except Exception as e:
            LOG.info(f"Unexpected error occurred: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Internal server error: Unexpected error occurred."},
            )

        finally:
            close_session()
