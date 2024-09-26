from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from genotype_api.exceptions import GenotypeDBError
from genotype_api.database.database import close_session


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception:
            raise GenotypeDBError
        finally
            close_session()
        return response
