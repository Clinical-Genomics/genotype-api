"""Routes for uploading sequence analyses"""

from io import BytesIO
from pathlib import Path
from typing import List

import genotype_api.crud.analyses
import genotype_api.crud.samples
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from genotype_api.database import get_session
from genotype_api.schemas.analysis import Analysis
from genotype_api.schemas.samples import SampleCreate
from genotype_api.vcf import SequenceAnalysis
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", response_model=List[Analysis])
def upload_vcf(file: UploadFile = File(...), db: Session = Depends(get_session)):
    file_name: Path = Path(file.filename)
    if not file_name.name.endswith(".vcf"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Please select a vcf file for upload",
        )
    content = file.file.read().decode("utf-8")

    sequence_analysis = SequenceAnalysis(vcf_file=content, source=str(file_name))
    analyses = []
    for analysis_obj in sequence_analysis.generate_analyses():
        db_analysis = genotype_api.crud.analyses.get_analysis_type_sample(
            db=db, sample_id=analysis_obj.sample_id, analysis_type="sequence"
        )
        if db_analysis:
            raise HTTPException(status_code=400, detail="Analysis already exists")
        if not genotype_api.crud.samples.get_sample(db=db, sample_id=analysis_obj.sample_id):
            genotype_api.crud.samples.create_sample(
                db=db, sample=SampleCreate(id=analysis_obj.sample_id)
            )
        analyses.append(genotype_api.crud.analyses.create_analysis(db=db, analysis=analysis_obj))

    return analyses
