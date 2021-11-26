"""Routes for plates"""

from io import BytesIO
from pathlib import Path
from typing import List

import genotype_api.crud.analyses
import genotype_api.crud.plates
import genotype_api.crud.samples
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from genotype_api import models
from genotype_api.database import get_session
from genotype_api.excel import GenotypeAnalysis
from genotype_api.schemas.plates import Plate
from genotype_api.schemas.samples import SampleCreate
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/plate", response_model=Plate)
def upload_plate(file: UploadFile = File(...), db: Session = Depends(get_session)):
    file_name: Path = Path(file.filename)
    if not file_name.name.endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Please select an excel book for upload",
        )
    # Get the plate id from the standardized name of the plate
    plate_id = file_name.name.split("_", 1)[0]
    # Check if plate exists
    db_plate = genotype_api.crud.plates.get_plate_by_plate_id(db, plate_id)
    if db_plate:
        raise HTTPException(status_code=400, detail="Plate already uploaded")
    plate_obj = models.Plate(plate_id=plate_id)
    content = BytesIO(file.file.read())
    excel_parser = GenotypeAnalysis(
        excel_file=content, file_name=str(file_name), include_key="-CG-"
    )
    for analysis_obj in excel_parser.generate_analyses():
        db_analysis = genotype_api.crud.analyses.get_analysis_type_sample(
            db=db, sample_id=analysis_obj.sample_id, analysis_type="genotype"
        )
        if db_analysis:
            raise HTTPException(status_code=400, detail="Analysis already exists")
        if not genotype_api.crud.samples.get_sample(db=db, sample_id=analysis_obj.sample_id):
            genotype_api.crud.samples.create_sample(
                db=db, sample=SampleCreate(id=analysis_obj.sample_id)
            )
        plate_obj.analyses.append(
            genotype_api.crud.analyses.create_analysis(db=db, analysis=analysis_obj)
        )

    return genotype_api.crud.plates.create_plate(db=db, plate=plate_obj)


@router.get("/<plate_id>", response_model=Plate)
def read_plate(plate_id: str, db: Session = Depends(get_session)):
    """Display information about a plate."""
    db_plate = genotype_api.crud.plates.get_plate_by_plate_id(db, plate_id=plate_id)
    if db_plate is None:
        raise HTTPException(status_code=404, detail="Plate not found")
    return db_plate


@router.get("/<plate_id>/sign-off/<name>", response_model=Plate)
def sign_off_plate(plate_id: str, name: str, db: Session = Depends(get_session)):
    """Sign off a plate.

    This means that current User sign off that the plate is checked
    """
    db_plate = genotype_api.crud.plates.get_plate_by_plate_id(db, plate_id=plate_id)
    if db_plate is None:
        raise HTTPException(status_code=404, detail="Plate not found")
    return db_plate


@router.get("/", response_model=List[Plate])
def read_plates(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    """Display information about a plate."""
    plates = genotype_api.crud.plates.get_plates(db, skip=skip, limit=limit)

    return plates


@router.delete("/<plate_id>", response_model=Plate)
def delete_plate(plate_id: int, db: Session = Depends(get_session)):
    """Display information about a plate."""
    db_plate = genotype_api.crud.plates.delete_plate(db, plate_id=plate_id)
    if db_plate is None:
        raise HTTPException(status_code=404, detail="Plate not found")
    return db_plate
