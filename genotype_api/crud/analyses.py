from typing import List, Optional

from genotype_api import models
from sqlalchemy.orm import Session


def get_analyses(db: Session) -> List[models.Analysis]:
    return db.query(models.Analysis).all()


def get_analysis(analysis_id: int, db: Session) -> Optional[models.Analysis]:
    return db.query(models.Analysis).filter(analysis_id == models.Analysis.id).first()


def get_analysis_type_sample(
    sample_id: str, analysis_type: str, db: Session
) -> Optional[models.Analysis]:
    return (
        db.query(models.Analysis)
        .filter(sample_id == models.Analysis.sample_id)
        .filter(analysis_type == models.Analysis.type)
        .first()
    )


def delete_analysis(db: Session, analysis_id: int) -> models.Analysis:
    db_analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
    db.delete(db_analysis)
    db.commit()
    return db_analysis


def create_analysis(db: Session, analysis: models.Analysis) -> models.Analysis:
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
