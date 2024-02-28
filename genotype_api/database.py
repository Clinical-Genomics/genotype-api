"""Hold the database information"""

from sqlmodel import Session, SQLModel, create_engine

from genotype_api.config import settings

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(settings.db_uri, pool_pre_ping=True)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
