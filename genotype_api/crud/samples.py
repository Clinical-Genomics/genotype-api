from typing import List, Optional

from genotype_api import models
from genotype_api.schemas import samples
from sqlalchemy.orm import Session


def get_samples(db: Session, skip: int = 0, limit: int = 100) -> List[models.Sample]:
    return db.query(models.Sample).offset(skip).limit(limit).all()


def get_sample(db: Session, sample_id: str) -> Optional[models.Sample]:
    return db.query(models.Sample).filter(models.Sample.id == sample_id).first()


def delete_sample(db: Session, id: str) -> models.SNP:
    db_sample = db.query(models.Sample).filter(models.Sample.id == id).first()
    db.delete(db_sample)
    db.commit()
    return db_sample


def create_sample(db: Session, sample: samples.SampleCreate):
    db_sample = models.Sample(id=sample.id, sex=sample.sex)
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample
