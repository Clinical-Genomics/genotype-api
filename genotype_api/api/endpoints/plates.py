"""Routes for plates"""

from http import HTTPStatus
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import JSONResponse

from genotype_api.database.filter_models.plate_models import PlateOrderParams
from genotype_api.database.store import Store, get_store
from genotype_api.dto.plate import PlateResponse
from genotype_api.dto.user import CurrentUser
from genotype_api.exceptions import PlateExistsError, PlateNotFoundError
from genotype_api.security import get_active_user
from genotype_api.services.endpoint_services.plate_service import PlateService

router = APIRouter()


def get_plate_service(store: Store = Depends(get_store)) -> PlateService:
    return PlateService(store)


@router.post(
    "/plate",
)
async def upload_plate(
    file: UploadFile = File(...),
    plate_service: PlateService = Depends(get_plate_service),
    current_user: CurrentUser = Depends(get_active_user),
):

    try:
        await plate_service.upload_plate(file)
    except PlateExistsError:
        raise HTTPException(
            detail="Plate already exists in the database.", status_code=HTTPStatus.BAD_REQUEST
        )
    return JSONResponse("Plate uploaded successfully", status_code=status.HTTP_201_CREATED)


@router.patch(
    "/{plate_id}/sign-off",
    response_model=PlateResponse,
    response_model_exclude={"analyses", "user", "plate_status_counts"},
)
async def sign_off_plate(
    plate_id: int,
    method_document: str = Query(...),
    method_version: str = Query(...),
    plate_service: PlateService = Depends(get_plate_service),
    current_user: CurrentUser = Depends(get_active_user),
):
    """Sign off a plate.
    This means that current CurrentUser sign off that the plate is checked
    Add Depends with current user
    """

    return await plate_service.update_plate_sign_off(
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
async def read_plate(
    plate_id: int,
    plate_service: PlateService = Depends(get_plate_service),
    current_user: CurrentUser = Depends(get_active_user),
):
    """Display information about a plate."""
    try:
        return await plate_service.get_plate(plate_id=plate_id)
    except PlateNotFoundError:
        raise HTTPException(
            detail=f"Could not find plate with id: {plate_id}", status_code=HTTPStatus.BAD_REQUEST
        )


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
    current_user: CurrentUser = Depends(get_active_user),
):
    """Display all plates"""
    order_params = PlateOrderParams(
        order_by=order_by, skip=skip, limit=limit, sort_order=sort_order
    )
    try:
        return await plate_service.get_plates(order_params=order_params)
    except PlateNotFoundError:
        raise HTTPException(
            detail="Could not fetch plates from backend.", status_code=HTTPStatus.BAD_REQUEST
        )


@router.delete("/{plate_id}")
async def delete_plate(
    plate_id: int,
    plate_service: PlateService = Depends(get_plate_service),
    current_user: CurrentUser = Depends(get_active_user),
):
    """Delete plate."""
    try:
        analysis_ids = await plate_service.delete_plate(plate_id)
        return JSONResponse(
            f"Deleted plate: {plate_id} and analyses: {analysis_ids}",
            status_code=status.HTTP_200_OK,
        )
    except PlateNotFoundError:
        raise HTTPException(
            detail=f"Could not find plate with id: {plate_id}", status_code=HTTPStatus.BAD_REQUEST
        )
