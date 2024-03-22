import logging
from datetime import timedelta, date
from typing import Callable, Sequence

from sqlalchemy import func
from sqlalchemy.orm import Query
from sqlmodel import Session, select
from sqlmodel.sql.expression import Select, SelectOfScalar

from genotype_api.constants import Types
from genotype_api.database.filter_models.plate_models import PlateOrderParams
from genotype_api.database.filter_models.sample_models import SampleFilterParams
from genotype_api.database.models import (
    Analysis,
    Plate,
    Sample,
    User,
    SNP,
)
from genotype_api.dto.dto import PlateReadWithAnalysisDetailSingle

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

LOG = logging.getLogger(__name__)


def get_analyses_from_plate(plate_id: int, session: Session) -> list[Analysis]:
    statement = select(Analysis).where(Analysis.plate_id == plate_id)
    return session.exec(statement).all()


def get_analysis_by_type_sample(
    sample_id: str, analysis_type: str, session: Session
) -> Analysis | None:
    statement = select(Analysis).where(
        Analysis.sample_id == sample_id, Analysis.type == analysis_type
    )
    return session.exec(statement).first()


def get_analysis_by_id(session: Session, analysis_id: int) -> Analysis:
    """Get analysis"""
    statement = select(Analysis).where(Analysis.id == analysis_id)
    return session.exec(statement).one()


def get_analyses(session: Session) -> list[Analysis]:
    statement = select(Analysis)
    return session.exec(statement).all()


def get_analyses_with_skip_and_limit(session: Session, skip: int, limit: int) -> list[Analysis]:
    statement = select(Analysis).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_analyses_by_type_between_dates(
    session, analysis_type: str, date_min: date, date_max: date
) -> list[Analysis]:
    analyses: Query = session.query(Analysis).filter(
        Analysis.type == analysis_type,
        Analysis.created_at > date_min - timedelta(days=1),
        Analysis.created_at < date_max + timedelta(days=1),
    )
    return analyses.all()


def get_analysis_by_type_and_sample_id(
    session: Session, analysis_type: str, sample_id: str
) -> Analysis:
    return (
        session.query(Analysis).filter(
            Analysis.sample_id == sample_id, Analysis.type == analysis_type
        )
    ).one()


def get_plate_by_id(session: Session, plate_id: int) -> Plate:
    """Get plate"""

    statement = select(Plate).where(Plate.id == plate_id)
    return session.exec(statement).one()


def get_plate_read_analysis_single(
    session: Session, plate_id: int
) -> PlateReadWithAnalysisDetailSingle:
    plate: Plate = get_plate_by_id(session=session, plate_id=plate_id)
    return PlateReadWithAnalysisDetailSingle.from_orm(plate)


def get_ordered_plates(
    session: Session, order_params: PlateOrderParams, sort_func: Callable
) -> Sequence[Plate]:
    plates: Sequence[Plate] = session.exec(
        select(Plate)
        .order_by(sort_func(order_params.order_by))
        .offset(order_params.skip)
        .limit(order_params.limit)
    ).all()
    return plates


def get_incomplete_samples(statement: SelectOfScalar) -> SelectOfScalar:
    """Returning sample query statement for samples with less than two analyses."""

    return (
        statement.group_by(Analysis.sample_id)
        .order_by(Analysis.created_at)
        .having(func.count(Analysis.sample_id) < 2)
    )


def get_filtered_samples(session: Session, filter_params: SampleFilterParams) -> list[Sample]:
    statement: SelectOfScalar = select(Sample).distinct().join(Analysis)
    if filter_params.sample_id:
        statement: SelectOfScalar = get_samples(
            statement=statement, sample_id=filter_params.sample_id
        )
    if filter_params.plate_id:
        statement: SelectOfScalar = get_plate_samples(
            statement=statement, plate_id=filter_params.plate_id
        )
    if filter_params.is_incomplete:
        statement: SelectOfScalar = get_incomplete_samples(statement=statement)
    if filter_params.is_commented:
        statement: SelectOfScalar = get_commented_samples(statement=statement)
    if filter_params.is_missing:
        statement: SelectOfScalar = get_status_missing_samples(statement=statement)
    return session.exec(
        statement.order_by(Sample.created_at.desc())
        .offset(filter_params.skip)
        .limit(filter_params.limit)
    ).all()


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


def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_users(session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    statement = select(User).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_users_with_skip_and_limit(session: Session, skip: int, limit: int) -> list[User]:
    return session.exec(select(User).offset(skip).limit(limit)).all()


def check_analyses_objects(
    session: Session, analyses: list[Analysis], analysis_type: Types
) -> None:
    """Raising 400 if any analysis in the list already exist in the database"""
    for analysis_obj in analyses:
        existing_analysis: Analysis = get_analysis_by_type_sample(
            session=session,
            sample_id=analysis_obj.sample_id,
            analysis_type=analysis_type,
        )
        if existing_analysis:
            session.delete(existing_analysis)


def get_snps(session) -> list[SNP]:
    return session.exec(select(SNP)).all()


def get_snps_by_limit_and_skip(session: Session, skip: int, limit: int) -> list[SNP]:
    return session.exec(select(SNP).offset(skip).limit(limit)).all()
