"""Routes for analysis"""

from http import HTTPStatus

from fastapi import APIRouter, Depends, File, Query, UploadFile, status, HTTPException
from fastapi.responses import JSONResponse

from genotype_api.database.store import Store, get_store
from genotype_api.dto.analysis import AnalysisResponse
from genotype_api.dto.user import CurrentUser

from genotype_api.exceptions import AnalysisNotFoundError
from genotype_api.security import get_active_user
from genotype_api.services.endpoint_services.analysis_service import (
    AnalysisService,
)


router = APIRouter()


def get_analysis_service(store: Store = Depends(get_store)) -> AnalysisService:
    return AnalysisService(store)


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def read_analysis(
    analysis_id: int,
    analysis_service: AnalysisService = Depends(get_analysis_service),
    current_user: CurrentUser = Depends(get_active_user),
):
    """Return analysis."""
    try:
        return analysis_service.get_analysis(analysis_id)
    except AnalysisNotFoundError:
        raise HTTPException(
            detail=f"Could not find analysis with id: {analysis_id}",
            status_code=HTTPStatus.BAD_REQUEST,
        )


@router.get("/", response_model=list[AnalysisResponse], response_model_exclude={"genotypes"})
def read_analyses(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    analysis_service: AnalysisService = Depends(get_analysis_service),
    current_user: CurrentUser = Depends(get_active_user),
):
    """Return all analyses."""
    try:
        return analysis_service.get_analyses(skip=skip, limit=limit)
    except AnalysisNotFoundError:
        raise HTTPException(
            detail="Could not fetch analyses from backend.",
            status_code=HTTPStatus.BAD_REQUEST,
        )


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    analysis_service: AnalysisService = Depends(get_analysis_service),
    current_user: CurrentUser = Depends(get_active_user),
):
    """Delete analysis based on analysis id."""
    try:
        analysis_service.delete_analysis(analysis_id)
    except AnalysisNotFoundError:
        raise HTTPException(
            detail=f"Could not find analysis with id: {analysis_id}",
            status_code=HTTPStatus.BAD_REQUEST,
        )
    return JSONResponse(content=f"Deleted analysis: {analysis_id}", status_code=status.HTTP_200_OK)


@router.post(
    "/sequence", response_model=list[AnalysisResponse], response_model_exclude={"genotypes"}
)
def upload_sequence_analysis(
    file: UploadFile = File(...),
    analysis_service: AnalysisService = Depends(get_analysis_service),
    current_user: CurrentUser = Depends(get_active_user),
):
    """Reading VCF file, creating and uploading sequence analyses and sample objects to the database."""

    analyses: list[AnalysisResponse] = analysis_service.get_upload_sequence_analyses(file)
    return analyses
