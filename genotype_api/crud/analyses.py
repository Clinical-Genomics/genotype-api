from typing import List, Optional

from fastapi import HTTPException, status

from genotype_api.constants import TYPES
from genotype_api.models import Analysis
from sqlmodel import Session, select
from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True


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
    session: Session, analyses: List[Analysis], analysis_type: TYPES
) -> None:
    """Raising 400 if any analysis in the list already exist in the database"""
    for analysis_obj in analyses:
        db_analysis: Analysis = get_analysis_type_sample(
            session=session, sample_id=analysis_obj.sample_id, analysis_type=analysis_type
        )
        if db_analysis:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=db_analysis.plate_id,
            )
