"""Routes for plates"""
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from genotype_api.crud.analyses import (
    get_analyses_from_plate,
    check_analyses_objects,
)
from genotype_api.crud.samples import create_analyses_sample_objects
from genotype_api.crud.plates import create_plate, get_plate
from genotype_api.database import get_session
from genotype_api.excel import GenotypeAnalysis
from genotype_api.files import check_file
from genotype_api.models import (
    Plate,
    PlateReadWithAnalyses,
    PlateRead,
    Analysis,
    PlateCreate,
)

router = APIRouter()


def get_plate_id_from_file(file_name: Path) -> str:
    # Get the plate id from the standardized name of the plate
    return file_name.name.split("_", 1)[0]


@router.post("/plate", response_model=Plate)
def upload_plate(file: UploadFile = File(...), session: Session = Depends(get_session)):
    file_name: Path = check_file(file_path=file.filename, extension=".xlsx")
    plate_id: str = get_plate_id_from_file(file_name)
    db_plate = session.get(Plate, plate_id)
    if db_plate:
        raise HTTPException(status_code=400, detail="Plate already uploaded")

    excel_parser = GenotypeAnalysis(
        excel_file=BytesIO(file.file.read()), file_name=str(file_name), include_key="-CG-"
    )
    analyses: List[Analysis] = list(excel_parser.generate_analyses())
    check_analyses_objects(session=session, analyses=analyses, analysis_type="genotype")
    create_analyses_sample_objects(session=session, analyses=analyses)
    plate_obj = PlateCreate(plate_id=plate_id)
    plate_obj.analyses = analyses
    return create_plate(session=session, plate=plate_obj)


@router.patch("/{plate_id}/sign-off", response_model=Plate)
def sign_off_plate(
    plate_id: int,
    method_document: str = Query(...),
    method_version: str = Query(...),
    session: Session = Depends(get_session),
):
    """Sign off a plate.
    This means that current User sign off that the plate is checked
    Add Depends with current user
    """

    plate: Plate = get_plate(session=session, plate_id=plate_id)

    # plate.user = current_user
    plate.signed_at = datetime.now()
    plate.method_document = method_document
    plate.method_version = method_version
    session.commit()
    session.refresh(plate)
    return plate


@router.get("/{plate_id}", response_model=PlateReadWithAnalyses)
def read_plate(plate_id: int, session: Session = Depends(get_session)):
    """Display information about a plate."""

    return get_plate(session=session, plate_id=plate_id)


@router.get("/", response_model=List[PlateRead])
def read_plates(
    skip: int = 0, limit: int = Query(default=100, lte=100), session: Session = Depends(get_session)
):
    """Display all plates"""
    plates: List[Plate] = session.exec(select(Plate).offset(skip).limit(limit)).all()

    return plates


@router.delete("/{plate_id}", response_model=Plate)
def delete_plate(plate_id: int, session: Session = Depends(get_session)):
    """Delete plate."""
    plate = session.get(Plate, plate_id)
    analyses: List[Analysis] = get_analyses_from_plate(session=session, plate_id=plate_id)
    analyse_ids = [analyse.id for analyse in analyses]
    for analysis in analyses:
        session.delete(analysis)
    session.delete(plate)
    session.commit()

    return JSONResponse(
        f"Deleted plate: {plate_id} and analyses: {analyse_ids}", status_code=status.HTTP_200_OK
    )
