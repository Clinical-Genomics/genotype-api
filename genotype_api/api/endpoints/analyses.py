"""Routes for analysis"""

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import JSONResponse
from sqlmodel import Session

from genotype_api.database.crud.delete import delete_analysis
from genotype_api.database.crud.read import (
    get_analysis_by_id,
)
from genotype_api.database.models import Analysis, User
from genotype_api.dto.analysis import AnalysisWithGenotypeResponse, AnalysisResponse
from genotype_api.database.session_handler import get_session
from genotype_api.security import get_active_user
from genotype_api.services.analysis_service.analysis_service import AnalysisService

router = APIRouter()


@router.get("/{analysis_id}", response_model=AnalysisWithGenotypeResponse)
def read_analysis(
    analysis_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Return analysis."""
    analysis_service = AnalysisService(session)
    return analysis_service.get_analysis_with_genotype(analysis_id)


@router.get("/", response_model=list[AnalysisResponse])
def read_analyses(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Return all analyses."""
    analysis_service = AnalysisService(session)
    return analysis_service.get_analyses_to_display(skip=skip, limit=limit)


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Delete analysis based on analysis_id"""
    analysis: Analysis = get_analysis_by_id(session=session, analysis_id=analysis_id)
    delete_analysis(session=session, analysis=analysis)
    return JSONResponse(f"Deleted analysis: {analysis_id}", status_code=status.HTTP_200_OK)


@router.post("/sequence", response_model=list[AnalysisResponse])
def upload_sequence_analysis(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Reading VCF file, creating and uploading sequence analyses and sample objects to the database."""
    analysis_service = AnalysisService(session)
    analyses: list[AnalysisResponse] = analysis_service.get_upload_sequence_analyses(file)
    return analyses
