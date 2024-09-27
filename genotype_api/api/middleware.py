import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, PendingRollbackError
from starlette.middleware.base import BaseHTTPMiddleware

from genotype_api.database.database import close_session, get_session
from genotype_api.exceptions import GenotypeDBError

LOG = logging.getLogger(__name__)


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        session = get_session()
        if session is None:
            LOG.error("No database session found.")
            return JSONResponse(
                status_code=500, content={"message": "Internal server error: No database session."}
            )

        try:
            response = await call_next(request)

            if session.dirty:
                session.flush()

            return response

        except PendingRollbackError as e:
            LOG.error("Pending rollback error, rolling back session", exc_info=True)
            if session.is_active:
                session.rollback()
            return JSONResponse(
                status_code=500, content={"message": "Internal server error: Pending rollback."}
            )

        except OperationalError as e:
            LOG.error("Operational error: database connection lost", exc_info=True)
            if session.is_active:
                session.rollback()
            return JSONResponse(
                status_code=500,
                content={"message": "Internal server error: Database connection lost."},
            )

        except Exception as e:
            LOG.error(f"Unexpected error occurred: {e}", exc_info=True)
            if session.is_active:
                session.rollback()
            return JSONResponse(
                status_code=500,
                content={"message": "Internal server error: Unexpected error occurred."},
            )

        finally:
            close_session()
