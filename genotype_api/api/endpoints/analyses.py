"""Routes for analysis"""
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from fastapi.responses import JSONResponse

from genotype_api.crud.analyses import get_analysis, check_analyses_objects, create_analysis
from genotype_api.crud.samples import create_analyses_sample_objects, refresh_sample_status
from genotype_api.database import get_session
from genotype_api.file_parsing.files import check_file
from genotype_api.models import Analysis, AnalysisRead, AnalysisReadWithGenotype, User
from sqlmodel import Session, select

from genotype_api.security import get_active_user
from genotype_api.file_parsing.vcf import SequenceAnalysis
from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

router = APIRouter()


@router.get("/{analysis_id}", response_model=AnalysisReadWithGenotype)
def read_analysis(
    analysis_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Return analysis."""

    return get_analysis(session=session, analysis_id=analysis_id)


@router.get("/", response_model=List[AnalysisRead])
def read_analyses(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> List[Analysis]:
    """Return all analyses."""
    analyses: List[Analysis] = session.exec(select(Analysis).offset(skip).limit(limit)).all()

    return analyses


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Delete analysis based on analysis_id"""
    analysis = get_analysis(session=session, analysis_id=analysis_id)
    session.delete(analysis)
    session.commit()

    return JSONResponse(f"Deleted analysis: {analysis_id}", status_code=status.HTTP_200_OK)


@router.post("/sequence", response_model=List[Analysis])
def upload_sequence_analysis(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Reading vcf file, creating and uploading sequence analyses and sample objects to db"""

    file_name: Path = check_file(file_path=file.filename, extension=".vcf")
    content = file.file.read().decode("utf-8")
    sequence_analysis = SequenceAnalysis(vcf_file=content, source=str(file_name))
    analyses: List[Analysis] = list(sequence_analysis.generate_analyses())
    check_analyses_objects(session=session, analyses=analyses, analysis_type="sequence")
    create_analyses_sample_objects(session=session, analyses=analyses)
    for analysis in analyses:
        analysis: Analysis = create_analysis(session=session, analysis=analysis)
        refresh_sample_status(session=session, sample=analysis.sample)
    return analyses
