"""Routes for plates"""

from typing import Literal
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from genotype_api.database.filter_models.plate_models import PlateOrderParams
from genotype_api.database.models import User
from genotype_api.database.session_handler import get_session
from genotype_api.dto.plate import PlateResponse
from genotype_api.security import get_active_user
from genotype_api.services.plate_service.plate_service import PlateService


router = APIRouter()


def get_plate_service(session: Session = Depends(get_session)) -> PlateService:
    return PlateService(session)


@router.post(
    "/plate",
    response_model=PlateResponse,
    response_model_exclude={"plate_status_counts"},
)
def upload_plate(
    file: UploadFile = File(...),
    plate_service: PlateService = Depends(get_plate_service),
    current_user: User = Depends(get_active_user),
):
    return plate_service.upload_plate(file)


@router.patch(
    "/{plate_id}/sign-off",
    response_model=PlateResponse,
    response_model_exclude={"analyses", "user", "plate_status_counts"},
)
def sign_off_plate(
    plate_id: int,
    method_document: str = Query(...),
    method_version: str = Query(...),
    plate_service: PlateService = Depends(get_plate_service),
    current_user: User = Depends(get_active_user),
):
    """Sign off a plate.
    This means that current User sign off that the plate is checked
    Add Depends with current user
    """

    return plate_service.update_plate_sign_off(
        plate_id=plate_id,
        user_email=current_user.email,
        method_version=method_version,
        method_document=method_document,
    )


@router.get(
    "/{plate_id}",
    response_model=PlateResponse,
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
    plate_service: PlateService = Depends(get_plate_service),
    current_user: User = Depends(get_active_user),
):
    """Display information about a plate."""

    return plate_service.read_plate(plate_id=plate_id)


@router.get(
    "/",
    response_model=list[PlateResponse],
    response_model_exclude={"analyses"},
    response_model_by_alias=False,
)
async def read_plates(
    order_by: Literal["created_at", "plate_id", "signed_at", "id"] | None = "id",
    sort_order: Literal["ascend", "descend"] | None = "descend",
    skip: int | None = 0,
    limit: int | None = 10,
    plate_service: PlateService = Depends(get_plate_service),
    current_user: User = Depends(get_active_user),
):
    """Display all plates"""
    order_params = PlateOrderParams(
        order_by=order_by, skip=skip, limit=limit, sort_order=sort_order
    )
    return plate_service.read_plates(order_params=order_params)


@router.delete("/{plate_id}")
def delete_plate(
    plate_id: int,
    plate_service: PlateService = Depends(get_plate_service),
    current_user: User = Depends(get_active_user),
):
    """Delete plate."""
    analysis_ids = plate_service.delete_plate(plate_id)
    return JSONResponse(
        f"Deleted plate: {plate_id} and analyses: {analysis_ids}",
        status_code=status.HTTP_200_OK,
    )
