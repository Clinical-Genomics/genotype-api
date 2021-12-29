from typing import List, Optional

from genotype_api.models import Sample, SNP, Analysis
from sqlmodel import Session, func
from sqlmodel.sql.expression import SelectOfScalar


def get_sample(session: Session, sample_id: str) -> Optional[Sample]:
    return session.get(Sample, sample_id)


def delete_sample(session: Session, sample_id: str) -> Sample:
    db_sample = session.get(Sample, sample_id)
    session.delete(db_sample)
    session.commit()
    return db_sample


def create_sample(session: Session, sample: Sample) -> Sample:
    session.add(sample)
    session.commit()
    session.refresh(sample)
    return sample


def get_incomplete_samples(statement: SelectOfScalar) -> SelectOfScalar:
    # return statement.join(Analysis).where(func.count(Sample.analyses) < 2)
    return (
        statement.join(Analysis)
        .group_by(Analysis.sample_id)
        .order_by(Analysis.created_at)
        .having(func.count(Analysis.sample_id) < 2)
    )


def get_plate_samples(statement: SelectOfScalar, plate_id: str) -> SelectOfScalar:
    return statement.join(Analysis).where(Analysis.plate_id == plate_id)


def get_commented_samples(statement: SelectOfScalar) -> SelectOfScalar:
    return statement.where(Sample.comment != None)


def get_samples_like(statement: SelectOfScalar, query_string: str) -> SelectOfScalar:
    return statement.where(Sample.id.like(f"%/{query_string}\_%"))
