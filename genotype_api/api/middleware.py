from fastapi import Request
from genotype_api.database.database import close_session


class DBSessionMiddleware:
    async def __call__(self, request: Request, call_next):
        try:
            response = await call_next(request)
        finally:
            close_session()
        return response
