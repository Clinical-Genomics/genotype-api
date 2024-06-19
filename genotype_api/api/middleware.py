from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from genotype_api.database.database import close_session, rollback_transactions


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception as error:
            rollback_transactions()
            raise error
        finally:
            close_session()
        return response
