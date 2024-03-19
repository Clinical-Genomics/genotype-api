"""Routes for analysis"""

from pathlib import Path

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from sqlmodel.sql.expression import Select, SelectOfScalar

from genotype_api.database.crud.delete import delete_analysis
from genotype_api.database.crud.create import create_analyses_sample_objects, create_analysis
from genotype_api.database.crud.read import (
    check_analyses_objects,
    get_analysis_by_id,
    get_analyses_with_skip_and_limit,
)
from genotype_api.database.crud.update import refresh_sample_status
from genotype_api.database.models import Analysis, User
from genotype_api.dto.analysis import AnalysisWithGenotypeResponse
from genotype_api.dto.dto import AnalysisRead, AnalysisReadWithGenotype
from genotype_api.database.session_handler import get_session
from genotype_api.file_parsing.files import check_file
from genotype_api.file_parsing.vcf import SequenceAnalysis
from genotype_api.security import get_active_user

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

router = APIRouter()


@router.get("/{analysis_id}", response_model=AnalysisWithGenotypeResponse)
def read_analysis(
    analysis_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Return analysis."""
    return get_analysis_by_id(session=session, analysis_id=analysis_id)


@router.get("/", response_model=list[AnalysisRead])
def read_analyses(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> list[Analysis]:
    """Return all analyses."""
    analyses: list[Analysis] = get_analyses_with_skip_and_limit(
        session=session, skip=skip, limit=limit
    )
    return analyses


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


@router.post("/sequence", response_model=list[Analysis])
def upload_sequence_analysis(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Reading vcf file, creating and uploading sequence analyses and sample objects to db"""

    file_name: Path = check_file(file_path=file.filename, extension=".vcf")
    content = file.file.read().decode("utf-8")
    sequence_analysis = SequenceAnalysis(vcf_file=content, source=str(file_name))
    analyses: list[Analysis] = list(sequence_analysis.generate_analyses())
    check_analyses_objects(session=session, analyses=analyses, analysis_type="sequence")
    create_analyses_sample_objects(session=session, analyses=analyses)
    for analysis in analyses:
        analysis: Analysis = create_analysis(session=session, analysis=analysis)
        refresh_sample_status(session=session, sample=analysis.sample)
    return analyses
