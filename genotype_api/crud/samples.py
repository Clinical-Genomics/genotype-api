from typing import List

from genotype_api.models import Sample, Analysis
from sqlmodel import Session, func, select
from sqlmodel.sql.expression import SelectOfScalar
from fastapi import status, HTTPException


def get_sample(session: Session, sample_id: str) -> Sample:
    """Get sample or raise 404"""

    statement = select(Sample).where(Sample.id == sample_id)
    return session.exec(statement).one()


def create_sample(session: Session, sample: Sample) -> Sample:
    """Adding a sample to db"""

    sample_in_db = session.get(Sample, sample.id)
    if sample_in_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Sample already registered"
        )
    session.add(sample)
    session.commit()
    session.refresh(sample)
    return sample


def get_incomplete_samples(statement: SelectOfScalar) -> SelectOfScalar:
    """Returning sample query statement for samples with les than two analyses"""

    # return statement.join(Analysis).where(func.count(Sample.analyses) < 2)
    return (
        statement.join(Analysis)
        .group_by(Analysis.sample_id)
        .order_by(Analysis.created_at)
        .having(func.count(Analysis.sample_id) < 2)
    )


def get_plate_samples(statement: SelectOfScalar, plate_id: str) -> SelectOfScalar:
    """Returning sample query statement for samples analysed on a specific plate"""

    return statement.join(Analysis).where(Analysis.plate_id == plate_id)


def get_commented_samples(statement: SelectOfScalar) -> SelectOfScalar:
    """Returning sample query statement for samples with no comment"""

    return statement.where(Sample.comment != None)


def get_samples_like(statement: SelectOfScalar, query_string: str) -> SelectOfScalar:
    """Returning sample id query filter statement. NOT WORKING"""

    return statement.where(Sample.id.like(f"%/{query_string}\_%"))


def create_analyses_sample_objects(session: Session, analyses: List[Analysis]) -> List[Sample]:
    """creating samples in an analysis if not already in db"""
    return [
        create_sample(session=session, sample=Sample(id=analysis_obj.sample_id))
        for analysis_obj in analyses
        if not session.get(Sample, analysis_obj.sample_id)
    ]
