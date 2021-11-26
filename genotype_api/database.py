"""Hold the database information"""
from sqlmodel import Session, SQLModel, create_engine

from genotype_api.config import settings

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(settings.db_uri, echo=True) # remove echo=True when going to prod


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

