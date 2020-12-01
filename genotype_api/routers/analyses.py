"""Routes for plates"""

from typing import List

import genotype_api.crud.analyses
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from genotype_api.database import get_db
from genotype_api.schemas.analysis import Analysis
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[Analysis])
def read_analyses(db: Session = Depends(get_db)):
    """Return all analyses."""
    analyses = genotype_api.crud.analyses.get_analyses(db)

    return analyses


@router.get("/<analysis_id>", response_model=Analysis)
def read_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Return all analyses."""
    analyses = genotype_api.crud.analyses.get_analysis(analysis_id=analysis_id, db=db)

    return analyses


@router.delete("/<analysis_id>", response_model=Analysis)
def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Return all analyses."""
    analysis = genotype_api.crud.analyses.delete_analysis(db, analysis_id=analysis_id)

    return analysis
