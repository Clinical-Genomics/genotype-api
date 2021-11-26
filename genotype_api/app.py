"""
Main functions for the genotype api

"""
from fastapi import FastAPI, status
from genotype_api.database import create_db_and_tables
from genotype_api.routers import analyses, plates, samples, sequences, snps, users


app = FastAPI()


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

app.include_router(
    sequences.router,
    prefix="/sequences",
    tags=["sequences"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Sample endpoints


# @app.get("/samples/<sample_id>", response_model=schemas.Sample)
# def read_sample(sample_id: int, db: Session = Depends(get_session)):
#     """Display information about a sample."""
#     db_sample = crud.get_sample(db, sample_id=sample_id)
#     if db_sample is None:
#         raise HTTPException(status_code=404, detail="Sample not found")
#     return db_sample


# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_session)):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)
#
#
# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items
