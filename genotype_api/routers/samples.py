"""Routes for samples"""

from typing import List

import genotype_api.crud.samples
from fastapi import APIRouter, Depends, HTTPException
from genotype_api import crud
from genotype_api.database import get_db
from genotype_api.schemas.samples import Sample, SampleCreate
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/<sample_id>", response_model=Sample)
def read_sample(sample_id: str, db: Session = Depends(get_db)):
    """Display information about a sample."""
    db_sample = genotype_api.crud.samples.get_sample(db, sample_id=sample_id)
    if db_sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    return db_sample


@router.get("/", response_model=List[Sample])
def read_samples(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Display information about a sample."""
    samples = genotype_api.crud.samples.get_samples(db, skip=skip, limit=limit)

    return samples


@router.post("/", response_model=Sample)
def create_sample(sample: SampleCreate, db: Session = Depends(get_db)):
    db_sample = genotype_api.crud.samples.get_sample(db, sample.id)
    if db_sample:
        raise HTTPException(status_code=400, detail="Sample already exists")
    return genotype_api.crud.samples.create_sample(db=db, sample=sample)
