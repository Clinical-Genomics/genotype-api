"""Routes for analysis"""

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import JSONResponse
from sqlmodel import Session


from genotype_api.database.models import User
from genotype_api.dto.analysis import AnalysisResponse

from genotype_api.database.session_handler import get_session
from genotype_api.security import get_active_user
from genotype_api.services.analysis_service.analysis_service import AnalysisService

router = APIRouter()


def get_analysis_service(session: Session = Depends(get_session)):
    return AnalysisService(session)


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def read_analysis(
    analysis_id: int,
    analysis_service: AnalysisService = Depends(get_analysis_service),
    current_user: User = Depends(get_active_user),
):
    """Return analysis."""
    return analysis_service.get_analysis(analysis_id)


@router.get("/", response_model=list[AnalysisResponse], response_model_exclude={"genotypes"})
def read_analyses(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    analysis_service: AnalysisService = Depends(get_analysis_service),
    current_user: User = Depends(get_active_user),
):
    """Return all analyses."""
    return analysis_service.get_analyses(skip=skip, limit=limit)


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    analysis_service: AnalysisService = Depends(get_analysis_service),
    current_user: User = Depends(get_active_user),
):
    """Delete analysis based on analysis_id"""
    analysis_service.delete_analysis(analysis_id)
    return JSONResponse(f"Deleted analysis: {analysis_id}", status_code=status.HTTP_200_OK)


@router.post(
    "/sequence", response_model=list[AnalysisResponse], response_model_exclude={"genotypes"}
)
def upload_sequence_analysis(
    file: UploadFile = File(...),
    analysis_service: AnalysisService = Depends(get_analysis_service),
    current_user: User = Depends(get_active_user),
):
    """Reading VCF file, creating and uploading sequence analyses and sample objects to the database."""

    analyses: list[AnalysisResponse] = analysis_service.get_upload_sequence_analyses(file)
    return analyses
