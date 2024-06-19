"""Hold the database information"""

import logging

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from genotype_api.exceptions import GenotypeDBError
from genotype_api.database.models import Base

SESSION: scoped_session | None = None
ENGINE: Engine | None = None
LOG = logging.getLogger(__name__)


def initialise_database(db_uri: str) -> None:
    """Initialize the SQLAlchemy engine and session for genotype api."""
    global SESSION, ENGINE

    ENGINE = create_engine(db_uri, pool_pre_ping=True)
    session_factory = sessionmaker(autoflush=False, bind=ENGINE)
    SESSION = scoped_session(session_factory)


def get_session() -> scoped_session:
    """Get a SQLAlchemy session with a connection to genotype api."""
    if not SESSION:
        raise GenotypeDBError
    return SESSION


def get_scoped_session_registry() -> scoped_session | None:
    """Get the scoped session registry for genotype api."""
    return SESSION


def get_engine() -> Engine:
    """Get the SQLAlchemy engine with a connection to genotype api."""
    if not ENGINE:
        raise GenotypeDBError
    return ENGINE


def create_all_tables() -> None:
    """Create all tables in genotype api."""
    session: Session = get_session()
    Base.metadata.create_all(bind=session.get_bind())
    close_session()


def drop_all_tables() -> None:
    """Drop all tables in genotype api."""
    session: Session = get_session()
    Base.metadata.drop_all(bind=session.get_bind())
    close_session()


def get_tables() -> list[str]:
    """Get a list of all tables in genotype api."""
    engine: Engine = get_engine()
    inspector: Inspector = inspect(engine)
    return inspector.get_table_names()


def close_session():
    """Close the global database session of the genotype api."""
    LOG.error("Closing database session")
    SESSION.close()


def rollback_transactions():
    """Rollback the global database session of the genotype api."""
    LOG.error("Rolling back database transactions")
    SESSION.rollback()
