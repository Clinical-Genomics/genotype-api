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
        session = None
        error_message = JSONResponse(
            status_code=500, content={"message": "Internal server error: database session error."}
        )

        try:
            session = get_session()
            if session is None:
                return error_message
            elif session.dirty:
                session.flush()
            else:
                response = await call_next(request)
                return response

        except PendingRollbackError as e:
            if session and session.is_active:
                session.rollback()
            LOG.debug(f"DB session error occurred: {e}")
            return error_message

        except OperationalError as e:
            LOG.debug(f"Database connection lost: {e}")
            return error_message

        except Exception as e:
            if session and session.is_active:
                session.rollback()
            LOG.debug(f"DB session occurred: {e}")
            return error_message
        finally:
            if session:
                close_session()
