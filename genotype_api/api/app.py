"""
Main functions for the genotype api

"""
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from genotype_api.database import create_db_and_tables
from genotype_api.api.endpoints import samples, snps, users
from genotype_api.api.endpoints import plates, analyses
from sqlalchemy.exc import NoResultFound

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
