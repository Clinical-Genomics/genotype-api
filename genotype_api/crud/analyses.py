from typing import List, Optional, Literal

from fastapi import HTTPException

from genotype_api.models import Analysis, AnalysisRead
from sqlmodel import Session, select


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


def delete_analysis(session: Session, analysis_id: int) -> Analysis:
    db_analysis = session.get(Analysis, analysis_id)
    session.delete(db_analysis)
    session.commit()
    return db_analysis


def create_analysis(session: Session, analysis: Analysis) -> Analysis:
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


def check_analyses_objects(
    session: Session, analyses: List[Analysis], analysis_type: Literal["genotype", "sequence"]
) -> None:
    """Raising 400 if any analysis in the list already exist in the database"""
    for analysis_obj in analyses:
        db_analysis: Analysis = get_analysis_type_sample(
            session=session, sample_id=analysis_obj.sample_id, analysis_type=analysis_type
        )
        if db_analysis:
            raise HTTPException(status_code=400, detail="Analysis already exists")
