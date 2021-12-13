from typing import List, Optional

from genotype_api.models import Sample, SampleCreate, SNP
from sqlalchemy.orm import Session


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
