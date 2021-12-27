"""Routes for samples"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from genotype_api.database import get_session
from genotype_api.models import Sample, SampleRead, SampleReadWithAnalysis, Analysis
from sqlmodel import Session, select

router = APIRouter()


@router.get("/{sample_id}", response_model=SampleReadWithAnalysis)
def read_sample(sample_id: str, session: Session = Depends(get_session)):
    sample = session.get(Sample, sample_id)
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found"
        )
    return sample


@router.get("/", response_model=List[SampleRead])
def read_samples(
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
        plate_id: Optional[str] = None,
        incomplete: Optional[str] = None,
        commented: Optional[str] = None,
        query_string: Optional[str] = None,
        session: Session = Depends(get_session),
) -> List[Sample]:
    statement = select(Sample)
    if plate_id:
        statement = statement.join(Analysis).where(f"%/{plate_id}\_%" in Analysis.source)  # like doesnt exist it seems
    if incomplete:
        statement.where(len(Sample.analyses) < 2) # probably not as it should. see original
    if commented:
        statement.where(Sample.comment is not None)
    if query_string:
        statement.where(f"%/{query_string}\_%" in Sample.id) # like doesnt exist it seems

    samples: List[Sample] = session.exec(statement.offset(skip).limit(limit)).all()
    return samples


@router.post("/", response_model=SampleRead)
def create_sample(sample: Sample, session: Session = Depends(get_session)):
    sample_in_db = session.get(Sample, sample.id)
    if sample_in_db:
        raise HTTPException(status_code=400, detail="Sample already registered")
    db_sample = Sample.from_orm(sample)
    session.add(db_sample)
    session.commit()
    session.refresh(db_sample)
    return db_sample


@router.put("/update-sex/{sample_id}", response_model=SampleRead)
def update_sex(
        sample: Sample,
        sex: str = Query(...),
        genotype_sex: Optional[str] = None,
        sequence_sex: Optional[str] = None,
        comment: str = Query(...),
        session: Session = Depends(get_session),
):
    sample_in_db = session.get(Sample, sample.id)
    if not sample_in_db:
        raise HTTPException(status_code=404, detail="Sample not in db")

    db_sample = Sample.from_orm(sample)
    db_sample.sex = sex
    db_sample.comment = comment
    for analysis in db_sample.analyses:
        if analysis.type == "genotype":
            analysis.sex = genotype_sex
        elif analysis.type == "sequence":
            analysis.sex = sequence_sex
        session.add(analysis)
    session.add(db_sample)
    session.commit()
    session.refresh(db_sample)
    return db_sample


@router.put("/update-status/{sample_id}", response_model=SampleRead)
def update_status(
        sample: Sample,
        status: str = Query(...),
        comment: str = Query(...),
        session: Session = Depends(get_session),
):
    sample_in_db = session.get(Sample, sample.id)
    if not sample_in_db:
        raise HTTPException(status_code=404, detail="Sample not in db")

    db_sample = Sample.from_orm(sample)
    db_sample.status = status
    if db_sample.comment:
        comment = f"{db_sample.comment}\n\n{comment}"
    db_sample.comment = comment
    session.add(db_sample)
    session.commit()
    session.refresh(db_sample)
    return db_sample


@router.delete("/{sample_id}", response_model=Sample)
def delete_sample(sample_id: int, session: Session = Depends(get_session)):
    """Delete sample."""
    sample = session.get(Sample, sample_id)
    session.delete(sample)
    session.commit()

    return sample
