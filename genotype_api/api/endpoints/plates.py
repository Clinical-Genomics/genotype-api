"""Routes for plates"""
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query, status
from sqlmodel import Session, select

from genotype_api.crud.analyses import (
    get_analyses_from_plate,
    check_analyses_objects,
)
from genotype_api.crud.samples import create_analyses_sample_objects, refresh_sample_status
from genotype_api.crud.plates import create_plate, get_plate
from genotype_api.crud.users import get_user_by_email
from genotype_api.database import get_session
from genotype_api.file_parsing.excel import GenotypeAnalysis
from genotype_api.file_parsing.files import check_file
from genotype_api.models import (
    Plate,
    PlateReadWithAnalyses,
    Analysis,
    PlateCreate,
    User,
    PlateRead,
)
from genotype_api.security import get_active_user

router = APIRouter()


def get_plate_id_from_file(file_name: Path) -> str:
    # Get the plate id from the standardized name of the plate
    return file_name.name.split("_", 1)[0]


from fastapi.responses import JSONResponse


@router.post("/plate", response_model=PlateReadWithAnalyses)
def upload_plate(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    file_name: Path = check_file(file_path=file.filename, extension=".xlsx")
    plate_id: str = get_plate_id_from_file(file_name)
    db_plate = session.get(Plate, plate_id)
    if db_plate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Plate with id {db_plate.id} already exists",
        )

    excel_parser = GenotypeAnalysis(
        excel_file=BytesIO(file.file.read()), file_name=str(file_name), include_key="-CG-"
    )
    analyses: List[Analysis] = list(excel_parser.generate_analyses())
    check_analyses_objects(session=session, analyses=analyses, analysis_type="genotype")
    create_analyses_sample_objects(session=session, analyses=analyses)
    plate_obj = PlateCreate(plate_id=plate_id)
    plate_obj.analyses = analyses
    plate: Plate = create_plate(session=session, plate=plate_obj)
    for analysis in plate.analyses:
        refresh_sample_status(sample=analysis.sample, session=session)
    session.refresh(plate)
    return plate


@router.patch("/{plate_id}/sign-off", response_model=Plate)
def sign_off_plate(
    plate_id: int,
    method_document: int = Query(...),
    method_version: int = Query(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Sign off a plate.
    This means that current User sign off that the plate is checked
    Add Depends with current user
    """

    plate: Plate = get_plate(session=session, plate_id=plate_id)
    db_user = get_user_by_email(session=session, email=current_user.email)
    plate.signed_by = db_user.id
    plate.signed_at = datetime.now()
    plate.method_document = method_document
    plate.method_version = method_version
    session.commit()
    session.refresh(plate)
    return plate


@router.get("/{plate_id}", response_model=PlateReadWithAnalyses)
def read_plate(
    plate_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Display information about a plate."""

    return get_plate(session=session, plate_id=plate_id)


@router.get("/", response_model=List[PlateRead])
def read_plates(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Display all plates"""
    plates: List[Plate] = session.exec(select(Plate).offset(skip).limit(limit)).all()

    return plates


@router.delete("/{plate_id}", response_model=Plate)
def delete_plate(
    plate_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
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
