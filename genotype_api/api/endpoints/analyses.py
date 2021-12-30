"""Routes for analysis"""
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import JSONResponse

from genotype_api.crud.analyses import get_analysis, check_analyses_objects, create_analyses
from genotype_api.crud.samples import create_analyses_sample_objects
from genotype_api.database import get_session
from genotype_api.files import check_file
from genotype_api.models import Analysis, AnalysisRead, AnalysisReadWithGenotype
from sqlmodel import Session, select

from genotype_api.vcf import SequenceAnalysis

router = APIRouter()


@router.get("/{analysis_id}", response_model=AnalysisReadWithGenotype)
def read_analysis(analysis_id: int, session: Session = Depends(get_session)):
    """Return analysis."""

    return get_analysis(session=session, analysis_id=analysis_id)


@router.get("/", response_model=List[AnalysisRead])
def read_analyses(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    session: Session = Depends(get_session),
) -> List[Analysis]:
    """Return all analyses."""
    analyses: List[Analysis] = session.exec(select(Analysis).offset(skip).limit(limit)).all()

    return analyses


@router.delete("/{analysis_id}")
def delete_analysis(analysis_id: int, session: Session = Depends(get_session)):
    """Delete analysis based on analysis_id"""
    analysis = get_analysis(session=session, analysis_id=analysis_id)
    session.delete(analysis)
    session.commit()

    return JSONResponse(f"Deleted analysis: {analysis_id}", status_code=status.HTTP_200_OK)


@router.post("/sequence", response_model=List[Analysis])
def upload_sequence_analysis(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """Reading vcf file, creating and uploading sequence analyses and sample objects to db"""

    file_name: Path = check_file(file_path=file.filename, extension=".vcf")
    content = file.file.read().decode("utf-8")
    sequence_analysis = SequenceAnalysis(vcf_file=content, source=str(file_name))
    analyses: List[Analysis] = list(sequence_analysis.generate_analyses())
    check_analyses_objects(session=session, analyses=analyses, analysis_type="sequence")
    create_analyses_sample_objects(session=session, analyses=analyses)
    create_analyses(session=session, analyses=analyses)
    return analyses
