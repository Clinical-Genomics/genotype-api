"""Routes for uploading sequence analyses"""

from pathlib import Path
from typing import List

from genotype_api.crud.analyses import get_analysis_type_sample, create_analysis
from genotype_api.crud.samples import create_sample
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from genotype_api.database import get_session
from genotype_api.files import check_file
from genotype_api.models import Analysis, Sample
from genotype_api.vcf import SequenceAnalysis
from sqlmodel import Session

router = APIRouter()


@router.post("/", response_model=List[Analysis])
def upload_sequence_analysis(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """Reading vcf file, creating and uploading analysis and sample objects to db"""

    file_name: Path = check_file(file_path=file.filename, extension=".vcf")
    content = file.file.read().decode("utf-8")
    sequence_analysis = SequenceAnalysis(vcf_file=content, source=str(file_name))
    analyses = []
    for analysis_obj in sequence_analysis.generate_analyses():
        db_analysis = get_analysis_type_sample(
            session=session, sample_id=analysis_obj.sample_id, analysis_type="sequence"
        )
        if db_analysis:
            raise HTTPException(status_code=400, detail="Analysis already exists")
        if not session.get(Sample, analysis_obj.sample_id):
            create_sample(session=session, sample=Sample(id=analysis_obj.sample_id))
        analyses.append(create_analysis(session=session, analysis=analysis_obj))

    return analyses
