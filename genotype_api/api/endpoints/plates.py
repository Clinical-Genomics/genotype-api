"""Routes for plates"""
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from sqlmodel import Session, select

from genotype_api.crud.analyses import create_analysis, get_analysis_type_sample
from genotype_api.crud.samples import create_sample
from genotype_api.crud.plates import create_plate
from genotype_api.database import get_session
from genotype_api.excel import GenotypeAnalysis
from genotype_api.models import (
    Plate,
    PlateReadWithAnalyses,
    PlateRead,
    Sample,
    Analysis,
    PlateCreate,
)

router = APIRouter()


@router.post("/plate", response_model=Plate)
def upload_plate(file: UploadFile = File(...), session: Session = Depends(get_session)):
    file_name: Path = Path(file.filename)
    if not file_name.name.endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Please select an excel book for upload",
        )
    # Get the plate id from the standardized name of the plate
    plate_id = file_name.name.split("_", 1)[0]
    # Check if plate exists
    db_plate = session.get(Plate, plate_id)
    if db_plate:
        raise HTTPException(status_code=400, detail="Plate already uploaded")
    plate_obj = PlateCreate(plate_id=plate_id)

    content = BytesIO(file.file.read())
    excel_parser = GenotypeAnalysis(
        excel_file=content, file_name=str(file_name), include_key="-CG-"
    )
    for analysis_obj in excel_parser.generate_analyses():
        db_analysis: Analysis = get_analysis_type_sample(
            session=session, sample_id=analysis_obj.sample_id, analysis_type="genotype"
        )
        if db_analysis:
            raise HTTPException(status_code=400, detail="Analysis already exists")
        if not session.get(Sample, analysis_obj.sample_id):
            create_sample(session=session, sample=Sample(id=analysis_obj.sample_id))
        plate_obj.analyses.append(create_analysis(session=session, analysis=analysis_obj))

    return create_plate(session=session, plate=plate_obj)


@router.post("/{plate_id}/sign-off", response_model=Plate)
def sign_off_plate(
    plate_id: str,
    method_document: str = Query(...),
    method_version: str = Query(...),
    session: Session = Depends(get_session),
):
    """Sign off a plate.
    This means that current User sign off that the plate is checked
    Add Depends with curent user
    """

    plate = session.get(Plate, plate_id)
    if not plate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plate not found")

    # plate.user = current_user
    plate.signed_at = datetime.now()
    plate.method_document = method_document
    plate.method_version = method_version
    session.commit()
    return plate


@router.get("/{plate_id}", response_model=PlateReadWithAnalyses)
def read_plate(plate_id: int, session: Session = Depends(get_session)):
    """Display information about a plate."""
    plate = session.get(Plate, plate_id)
    if not plate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plate not found")
    return plate


@router.get("/", response_model=List[PlateRead])
def read_plates(
    skip: int = 0, limit: int = Query(default=100, lte=100), session: Session = Depends(get_session)
):
    """Display information about a plate."""
    plates: List[Plate] = session.exec(select(Plate).offset(skip).limit(limit)).all()

    return plates


@router.delete("/{plate_id}", response_model=Plate)
def delete_plate(plate_id: int, session: Session = Depends(get_session)):
    """Delete plate."""
    plate = session.get(Plate, plate_id)
    session.delete(plate)
    session.commit()

    return plate
