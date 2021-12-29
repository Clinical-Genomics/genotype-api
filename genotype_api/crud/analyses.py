from typing import List, Optional

from genotype_api.models import Analysis, AnalysisRead
from sqlmodel import Session, select


def get_analyses_from_plate(plate_id: int, session: Session) -> List[Analysis]:
    statement = select(Analysis).where(Analysis.plate_id == plate_id)
    return session.exec(statement).all()


def get_analysis(analysis_id: int, session: Session) -> Optional[Analysis]:
    return session.get(Analysis, analysis_id)


def get_analysis_type_sample(
    sample_id: str, analysis_type: str, session: Session
) -> Optional[Analysis]:
    statement = select(Analysis).where(
        Analysis.sample_id == sample_id, Analysis.type == analysis_type
    )
    return session.exec(statement).first()


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
