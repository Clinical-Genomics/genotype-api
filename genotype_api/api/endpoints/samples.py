"""Routes for samples"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from genotype_api.database import get_session
from genotype_api.models import Sample, SampleRead, SampleReadWithAnalysis
from sqlmodel import Session, select

router = APIRouter()


@router.get("/{sample_id}", response_model=SampleReadWithAnalysis)
def read_sample(sample_id: str, session: Session = Depends(get_session)):
    sample = session.get(Sample, sample_id)
    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found")
    return sample


@router.get("/", response_model=List[SampleRead])
def read_samples(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    session: Session = Depends(get_session),
) -> List[Sample]:
    samples: List[Sample] = session.exec(select(Sample).offset(skip).limit(limit)).all()
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
