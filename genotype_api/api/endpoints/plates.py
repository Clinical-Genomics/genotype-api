"""Routes for plates"""
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import List

import genotype_api.crud.analyses
import genotype_api.crud.plates
import genotype_api.crud.samples
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query

from genotype_api.database import get_session
from genotype_api.excel import GenotypeAnalysis
from genotype_api.models import SampleCreate, Plate, PlateReadWithAnalyses, PlateRead
from sqlmodel import Session, select

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
    db_plate = genotype_api.crud.plates.get_plate_by_plate_id(session, plate_id)
    if db_plate:
        raise HTTPException(status_code=400, detail="Plate already uploaded")
    plate_obj = Plate(plate_id=plate_id)
    content = BytesIO(file.file.read())
    excel_parser = GenotypeAnalysis(
        excel_file=content, file_name=str(file_name), include_key="-CG-"
    )
    for analysis_obj in excel_parser.generate_analyses():
        db_analysis = genotype_api.crud.analyses.get_analysis_type_sample(
            db=session, sample_id=analysis_obj.sample_id, analysis_type="genotype"
        )
        if db_analysis:
            raise HTTPException(status_code=400, detail="Analysis already exists")
        if not genotype_api.crud.samples.get_sample(db=session, sample_id=analysis_obj.sample_id):
            genotype_api.crud.samples.create_sample(
                db=session, sample=SampleCreate(id=analysis_obj.sample_id)
            )
        plate_obj.analyses.append(
            genotype_api.crud.analyses.create_analysis(db=session, analysis=analysis_obj)
        )

    return genotype_api.crud.plates.create_plate(db=session, plate=plate_obj)


@router.get("/{plate_id}", response_model=PlateReadWithAnalyses)
def read_plate(plate_id: str, session: Session = Depends(get_session)):
    """Display information about a plate."""
    plate = session.get(Plate, plate_id)
    if not plate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plate not found")
    return plate


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
