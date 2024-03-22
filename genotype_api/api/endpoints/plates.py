"""Routes for plates"""

from pathlib import Path
from typing import Literal, Sequence
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy import asc, desc
from sqlmodel import Session
from sqlmodel.sql.expression import Select, SelectOfScalar
from genotype_api.database.crud.delete import delete_analysis
from genotype_api.database.crud.read import (
    get_analyses_from_plate,
    get_plate_read_analysis_single,
    get_ordered_plates,
)
from genotype_api.database.filter_models.plate_models import PlateOrderParams
from genotype_api.database.models import (
    Analysis,
    Plate,
    User,
)
from genotype_api.dto.dto import (
    PlateReadWithAnalysisDetail,
    PlateReadWithAnalysisDetailSingle,
)
from genotype_api.database.session_handler import get_session
from genotype_api.dto.plate import PlateAnalysesResponse, PlateResponse
from genotype_api.security import get_active_user
from genotype_api.services.plate_service.plate_service import PlateService

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

router = APIRouter()


def get_plate_id_from_file(file_name: Path) -> str:
    # Get the plate id from the standardized name of the plate
    return file_name.name.split("_", 1)[0]


@router.post("/plate", response_model=PlateAnalysesResponse)
def upload_plate(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    plate_service = PlateService(session)
    return plate_service.upload_plate(file)


@router.patch("/{plate_id}/sign-off", response_model=PlateResponse)
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
    plate_service = PlateService(session)
    return plate_service.update_plate_sign_off(
        plate_id=plate_id,
        user_id=current_user.id,
        method_version=method_version,
        method_document=method_document,
    )


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
    return get_plate_read_analysis_single(session=session, plate_id=plate_id)


@router.get(
    "/",
    response_model=list[PlateReadWithAnalysisDetail],
    response_model_exclude={"analyses"},
    response_model_by_alias=False,
)
async def read_plates(
    order_by: Literal["created_at", "plate_id", "signed_at", "id"] | None = "id",
    sort_order: Literal["ascend", "descend"] | None = "descend",
    skip: int | None = 0,
    limit: int | None = 10,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> Sequence[Plate]:
    """Display all plates"""
    sort_func = desc if sort_order == "descend" else asc
    order_params = PlateOrderParams(order_by=order_by, skip=skip, limit=limit)
    plates: Sequence[Plate] = get_ordered_plates(
        session=session, order_params=order_params, sort_func=sort_func
    )
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
        delete_analysis(session=session, analysis=analysis)
    delete_plate(session=session, plate=plate)

    return JSONResponse(
        f"Deleted plate: {plate_id} and analyses: {analyse_ids}",
        status_code=status.HTTP_200_OK,
    )
