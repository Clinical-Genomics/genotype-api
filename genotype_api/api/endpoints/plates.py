"""Routes for plates"""

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Literal, Optional

from fastapi import (APIRouter, Depends, File, HTTPException, Query,
                     UploadFile, status)
from fastapi.responses import JSONResponse
from sqlalchemy import asc, desc
from sqlmodel import Session, select
from sqlmodel.sql.expression import Select, SelectOfScalar

from genotype_api.database.crud.create import (create_analyses_sample_objects,
                                               create_plate)
from genotype_api.database.crud.read import (check_analyses_objects,
                                             get_analyses_from_plate,
                                             get_plate, get_user_by_email)
from genotype_api.database.crud.update import refresh_sample_status
from genotype_api.database.models import (Analysis, Plate, PlateCreate,
                                          PlateReadWithAnalyses,
                                          PlateReadWithAnalysisDetail,
                                          PlateReadWithAnalysisDetailSingle,
                                          User)
from genotype_api.database.session_handler import get_session
from genotype_api.file_parsing.excel import GenotypeAnalysis
from genotype_api.file_parsing.files import check_file
from genotype_api.security import get_active_user

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

router = APIRouter()


def get_plate_id_from_file(file_name: Path) -> str:
    # Get the plate id from the standardized name of the plate
    return file_name.name.split("_", 1)[0]


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
        excel_file=BytesIO(file.file.read()),
        file_name=str(file_name),
        include_key="-CG-",
    )
    analyses: list[Analysis] = list(excel_parser.generate_analyses())
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
    method_document: str = Query(...),
    method_version: str = Query(...),
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


@router.get(
    "/{plate_id}",
    response_model=PlateReadWithAnalysisDetailSingle,
    response_model_by_alias=False,
    response_model_exclude={
        "analyses": {
            "__all__": {
                "sample": {
                    "analyses": True,
                    "created_at": True,
                    "sex": True,
                    "id": True,
                },
                "source": True,
                "created_at": True,
                "type": True,
                "plate_id": True,
                "id": True,
            }
        }
    },
)
def read_plate(
    plate_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Display information about a plate."""

    return PlateReadWithAnalysisDetailSingle.from_orm(get_plate(session=session, plate_id=plate_id))


@router.get(
    "/",
    response_model=list[PlateReadWithAnalysisDetail],
    response_model_exclude={"analyses"},
    response_model_by_alias=False,
)
async def read_plates(
    order_by: Optional[Literal["created_at", "plate_id", "signed_at", "id"]] = "id",
    sort_order: Optional[Literal["ascend", "descend"]] = "descend",
    skip: Optional[int] = 0,
    limit: Optional[int] = 10,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Display all plates"""
    sort_func = desc if sort_order == "descend" else asc
    plates: list[Plate] = session.exec(
        select(Plate).order_by(sort_func(order_by)).offset(skip).limit(limit)
    ).all()

    return plates


@router.delete("/{plate_id}", response_model=Plate)
def delete_plate(
    plate_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Delete plate."""
    plate = session.get(Plate, plate_id)
    analyses: list[Analysis] = get_analyses_from_plate(session=session, plate_id=plate_id)
    analyse_ids = [analyse.id for analyse in analyses]
    for analysis in analyses:
        session.delete(analysis)
    session.delete(plate)
    session.commit()

    return JSONResponse(
        f"Deleted plate: {plate_id} and analyses: {analyse_ids}",
        status_code=status.HTTP_200_OK,
    )
