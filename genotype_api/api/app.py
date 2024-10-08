"""
Main functions for the genotype api

"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound, OperationalError

from genotype_api.api.endpoints import analyses, plates, samples, snps, users
from genotype_api.config import security_settings

LOG = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions, like connecting to the database
    LOG.debug("Starting up...")
    yield  # This is important, it must yield control
    # Shutdown actions, like closing the database connection
    LOG.debug("Shutting down...")


app = FastAPI(lifespan=lifespan, root_path=security_settings.api_root_path)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(OperationalError)
async def db_connection_exception_handler(request: Request, exc: OperationalError):
    LOG.error(f"Database connection error: {exc}")
    return JSONResponse(
        content={"detail": "Database connection error. Please try again later."},
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,  # 503 indicates a service is unavailable
    )


@app.exception_handler(NoResultFound)
async def not_found_exception_handler(request: Request, exc: NoResultFound):
    return JSONResponse("Document not found", status_code=status.HTTP_404_NOT_FOUND)


@app.get("/")
def welcome():
    return {"hello": "Welcome to the genotype api"}


app.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

app.include_router(
    samples.router,
    prefix="/samples",
    tags=["samples"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

app.include_router(
    plates.router,
    prefix="/plates",
    tags=["plates"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

app.include_router(
    snps.router,
    prefix="/snps",
    tags=["snps"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

app.include_router(
    analyses.router,
    prefix="/analyses",
    tags=["analyses"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)
