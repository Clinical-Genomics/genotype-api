from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from starlette import status

from genotype_api.constants import STATUS, SEXES
from genotype_api.database import get_session
from genotype_api.match import check_sample
from genotype_api.models import Sample, SampleReadWithAnalysis, SampleRead, User
from genotype_api import crud
from genotype_api.crud.samples import (
    get_incomplete_samples,
    get_plate_samples,
    get_commented_samples,
    get_sample,
    get_status_missing_samples,
)
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from genotype_api.security import get_active_user


router = APIRouter()


@router.get("/{sample_id}", response_model=SampleReadWithAnalysis)
def read_sample(
    sample_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    return get_sample(session=session, sample_id=sample_id)


@router.get("/", response_model=List[SampleReadWithAnalysis])
def read_samples(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    plate_id: Optional[str] = None,
    incomplete: Optional[bool] = False,
    commented: Optional[bool] = False,
    status_missing: Optional[bool] = False,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    statement: SelectOfScalar = select(Sample)
    if plate_id:
        statement: SelectOfScalar = get_plate_samples(statement=statement, plate_id=plate_id)
    if incomplete:
        statement: SelectOfScalar = get_incomplete_samples(statement=statement)
    if commented:
        statement: SelectOfScalar = get_commented_samples(statement=statement)
    if status_missing:
        statement: SelectOfScalar = get_status_missing_samples(statement=statement)
    samples: List[Sample] = session.exec(statement.offset(skip).limit(limit)).all()
    return samples


@router.post("/", response_model=SampleRead)
def create_sample(
    sample: Sample,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    return crud.samples.create_sample(session=session, sample=sample)


@router.patch("/{sample_id}/sex", response_model=SampleRead)
def update_sex(
    sample_id: str,
    sex: SEXES = Query(...),
    genotype_sex: Optional[SEXES] = None,
    sequence_sex: Optional[SEXES] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Updating sex field on sample and sample analyses"""

    sample_in_db: Sample = get_sample(session=session, sample_id=sample_id)
    sample_in_db.sex = sex
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


@router.patch("/{sample_id}/comment", response_model=SampleRead)
def update_comment(
    sample_id: str,
    comment: str = Query(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Updating comment field on sample"""

    sample_in_db: Sample = get_sample(session=session, sample_id=sample_id)
    sample_in_db.comment = comment
    session.add(sample_in_db)
    session.commit()
    session.refresh(sample_in_db)
    return sample_in_db


@router.patch("/{sample_id}/status", response_model=SampleRead)
def update_status(
    sample_id: str,
    status: STATUS = Query(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Updating status field on sample"""

    sample_in_db: Sample = get_sample(session=session, sample_id=sample_id)
    sample_in_db.status = status
    session.add(sample_in_db)
    session.commit()
    session.refresh(sample_in_db)
    return sample_in_db


@router.put("/{sample_id}/status", response_model=SampleRead)
def check(
    sample_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Check sample."""

    sample: Sample = get_sample(session=session, sample_id=sample_id)
    if len(sample.analyses) != 2:
        sample.status = None
    else:
        results = check_sample(sample=sample)
        sample.status = "fail" if "fail" in results.values() else "pass"

    session.add(sample)
    session.commit()
    session.refresh(sample)
    return sample


@router.delete("/{sample_id}", response_model=Sample)
def delete_sample(
    sample_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Delete sample and its Analyses"""

    sample: Sample = get_sample(session=session, sample_id=sample_id)
    for analysis in sample.analyses:
        session.delete(analysis)
    session.delete(sample)
    session.commit()
    return JSONResponse(
        f"Deleted sample: {sample_id} and analyses: {[analysis.id for analysis in sample.analyses]}",
        status_code=status.HTTP_200_OK,
    )
