from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from genotype_api.database import get_session
from genotype_api.models import Sample, SampleReadWithAnalysis, SampleRead
from genotype_api import crud
from genotype_api.crud.samples import (
    get_incomplete_samples,
    get_plate_samples,
    get_commented_samples,
    get_samples_like,
    get_sample,
)
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

router = APIRouter()


@router.get("/{sample_id}", response_model=SampleReadWithAnalysis)
def read_sample(sample_id: str, session: Session = Depends(get_session)):
    return get_sample(session=session, sample_id=sample_id)


@router.get("/", response_model=List[SampleReadWithAnalysis])
def read_samples(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    plate_id: Optional[str] = None,
    incomplete: Optional[bool] = False,
    commented: Optional[bool] = False,
    query_string: Optional[str] = None,
    session: Session = Depends(get_session),
):
    statement: SelectOfScalar = select(Sample)
    if plate_id:
        statement: SelectOfScalar = get_plate_samples(statement=statement, plate_id=plate_id)
    if incomplete:
        statement: SelectOfScalar = get_incomplete_samples(statement=statement)
    if commented:
        statement: SelectOfScalar = get_commented_samples(statement=statement)
    if query_string:
        statement: SelectOfScalar = get_samples_like(statement=statement, query_string=query_string)
    samples: List[Sample] = session.exec(statement.offset(skip).limit(limit)).all()
    return samples


@router.post("/", response_model=SampleRead)
def create_sample(sample: Sample, session: Session = Depends(get_session)):
    return crud.samples.create_sample(session=session, sample=sample)


@router.put("/update-sex/{sample_id}", response_model=SampleRead)
def update_sex(
    sample_id: str,
    sex: str = Query(...),
    genotype_sex: Optional[str] = None,
    sequence_sex: Optional[str] = None,
    comment: str = Query(...),
    session: Session = Depends(get_session),
):
    """Updating sex field on sample and sample analyses"""

    sample_in_db: Sample = get_sample(session=session, sample_id=sample_id)
    sample_in_db.sex = sex
    sample_in_db.comment = comment
    for analysis in sample_in_db.analyses:
        if analysis.type == "genotype":
            analysis.sex = genotype_sex
        elif analysis.type == "sequence":
            analysis.sex = sequence_sex
        session.add(analysis)
    session.add(sample_in_db)
    session.commit()
    session.refresh(sample_in_db)
    return sample_in_db


@router.put("/update-status/{sample_id}", response_model=SampleRead)
def update_status(
    sample_id: str,
    status: str = Query(...),
    comment: str = Query(...),
    session: Session = Depends(get_session),
):
    """Updating status and comment field on sample"""

    sample_in_db: Sample = get_sample(session=session, sample_id=sample_id)
    sample_in_db.status = status
    if sample_in_db.comment:
        comment = f"{sample_in_db.comment}\n\n{comment}"
    sample_in_db.comment = comment
    session.add(sample_in_db)
    session.commit()
    session.refresh(sample_in_db)
    return sample_in_db


@router.delete("/{sample_id}", response_model=Sample)
def delete_sample(sample_id: str, session: Session = Depends(get_session)):
    """Delete sample"""
    sample: Sample = session.get(Sample, sample_id)
    session.delete(sample)
    session.commit()
    return sample
