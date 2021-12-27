from typing import List, Optional

from genotype_api.models import Analysis
from sqlalchemy.orm import Session


def get_analyses(db: Session) -> List[Analysis]:
    return db.query(Analysis).all()


def get_analysis(analysis_id: int, db: Session) -> Optional[Analysis]:
    return db.query(Analysis).filter(analysis_id == Analysis.id).first()


def get_analysis_type_sample(sample_id: str, analysis_type: str, db: Session) -> Optional[Analysis]:
    return (
        db.query(Analysis)
        .filter(sample_id == Analysis.sample_id)
        .filter(analysis_type == Analysis.type)
        .first()
    )


def delete_analysis(db: Session, analysis_id: int) -> Analysis:
    db_analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    db.delete(db_analysis)
    db.commit()
    return db_analysis


def create_analysis(db: Session, analysis: Analysis) -> Analysis:
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
