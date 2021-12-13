"""Routes for plates"""

from typing import List

import genotype_api.crud.analyses
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from genotype_api.database import get_session
from genotype_api.models import Analysis, AnalysisRead, AnalysisReadWithGenotype
from sqlmodel import Session, select, delete

router = APIRouter()


@router.get("/{analysis_id}", response_model=AnalysisReadWithGenotype)
def read_analysis(analysis_id: int, session: Session = Depends(get_session)):
    """Return analysis."""
    analysis = session.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

    return analysis


@router.get("/", response_model=List[AnalysisRead])
def read_analyses(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    session: Session = Depends(get_session),
) -> List[Analysis]:
    """Return all analyses."""
    analyses: List[Analysis] = session.exec(select(Analysis).offset(skip).limit(limit)).all()

    return analyses


@router.delete("/<analysis_id>", response_model=AnalysisRead)
def delete_analysis(analysis_id: int, session: Session = Depends(get_session)):
    """Delete analysis based on analysis_id"""
    analysis = session.get(Analysis, analysis_id)
    session.delete(analysis)
    session.commit()

    return analysis
