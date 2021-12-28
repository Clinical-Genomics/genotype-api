from typing import List, Optional

from genotype_api.models import Sample, SampleCreate, SNP, Analysis
from sqlmodel import Session, func
from sqlmodel.sql.expression import SelectOfScalar


def get_samples(db: Session, skip: int = 0, limit: int = 100) -> List[Sample]:
    return db.query(Sample).offset(skip).limit(limit).all()


def get_sample(db: Session, sample_id: str) -> Optional[Sample]:
    return db.query(Sample).filter(Sample.id == sample_id).first()


def delete_sample(db: Session, id: str) -> SNP:
    db_sample = db.query(Sample).filter(Sample.id == id).first()
    db.delete(db_sample)
    db.commit()
    return db_sample


def create_sample(db: Session, sample: SampleCreate):
    db_sample = Sample(id=sample.id, sex=sample.sex)
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample


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
