import logging
from typing import List, Optional

from sqlalchemy import func
from sqlmodel import Session, select

from genotype_api.constants import TYPES
from genotype_api.database.models.models import Analysis, Sample, User, Plate
from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

LOG = logging.getLogger(__name__)


def get_analyses_from_plate(plate_id: int, session: Session) -> List[Analysis]:
    statement = select(Analysis).where(Analysis.plate_id == plate_id)
    return session.exec(statement).all()


def get_analysis_type_sample(
    sample_id: str, analysis_type: str, session: Session
) -> Optional[Analysis]:
    statement = select(Analysis).where(
        Analysis.sample_id == sample_id, Analysis.type == analysis_type
    )
    return session.exec(statement).first()


def get_analysis(session: Session, analysis_id: int) -> Analysis:
    """Get analysis"""

    statement = select(Analysis).where(Analysis.id == analysis_id)
    return session.exec(statement).one()


def get_plate(session: Session, plate_id: int) -> Plate:
    """Get plate"""

    statement = select(Plate).where(Plate.id == plate_id)
    return session.exec(statement).one()


def get_incomplete_samples(statement: SelectOfScalar) -> SelectOfScalar:
    """Returning sample query statement for samples with less than two analyses."""

    return (
        statement.group_by(Analysis.sample_id)
        .order_by(Analysis.created_at)
        .having(func.count(Analysis.sample_id) < 2)
    )


def get_plate_samples(statement: SelectOfScalar, plate_id: str) -> SelectOfScalar:
    """Returning sample query statement for samples analysed on a specific plate."""
    return statement.where(Analysis.plate_id == plate_id)


def get_commented_samples(statement: SelectOfScalar) -> SelectOfScalar:
    """Returning sample query statement for samples with no comment."""

    return statement.where(Sample.comment != None)


def get_status_missing_samples(statement: SelectOfScalar) -> SelectOfScalar:
    """Returning sample query statement for samples with no comment."""

    return statement.where(Sample.status == None)


def get_sample(session: Session, sample_id: str) -> Sample:
    """Get sample or raise 404."""

    statement = select(Sample).where(Sample.id == sample_id)
    return session.exec(statement).one()


def get_samples(statement: SelectOfScalar, sample_id: str) -> SelectOfScalar:
    """Returns a query for samples containing the given sample_id."""
    return statement.where(Sample.id.contains(sample_id))


def get_user(session: Session, user_id: int):
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).one()


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_users(session: Session, skip: int = 0, limit: int = 100) -> List[User]:
    statement = select(User).offset(skip).limit(limit)
    return session.exec(statement).all()


def check_analyses_objects(
    session: Session, analyses: List[Analysis], analysis_type: TYPES
) -> None:
    """Raising 400 if any analysis in the list already exist in the database"""
    for analysis_obj in analyses:
        db_analysis: Analysis = get_analysis_type_sample(
            session=session,
            sample_id=analysis_obj.sample_id,
            analysis_type=analysis_type,
        )
        if db_analysis:
            session.delete(db_analysis)