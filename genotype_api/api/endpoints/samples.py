from datetime import date
from http import HTTPStatus
from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette import status

from genotype_api.constants import Sexes, Types
from genotype_api.database.filter_models.sample_models import SampleFilterParams
from genotype_api.database.models import (
    Sample,
    User,
)

from genotype_api.database.store import Store, get_store
from genotype_api.dto.sample import SampleResponse
from genotype_api.exceptions import SampleNotFoundError, SampleExistsError
from genotype_api.models import MatchResult, SampleDetail
from genotype_api.security import get_active_user
from genotype_api.services.endpoint_services.sample_service import SampleService

router = APIRouter()


def get_sample_service(store: Store = Depends(get_store)) -> SampleService:
    return SampleService(store)


@router.get(
    "/{sample_id}",
    response_model=SampleResponse,
)
def read_sample(
    sample_id: str,
    sample_service: SampleService = Depends(get_sample_service),
    current_user: User = Depends(get_active_user),
):
    try:
        return sample_service.get_sample(sample_id)
    except SampleNotFoundError:
        return JSONResponse(
            content=f"Sample with id: {sample_id} not found.", status_code=HTTPStatus.BAD_REQUEST
        )


@router.post(
    "/",
)
def create_sample(
    sample: Sample,
    sample_service: SampleService = Depends(get_sample_service),
    current_user: User = Depends(get_active_user),
):
    try:
        sample_service.create_sample(sample=sample)
        new_sample: SampleResponse = sample_service.get_sample(sample_id=sample.id)
        if not new_sample:
            return JSONResponse(
                content="Failed to create sample.", status_code=HTTPStatus.BAD_REQUEST
            )
        return JSONResponse(f"Sample with id: {sample.id} was created.", status_code=HTTPStatus.OK)
    except SampleExistsError:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=f"Sample with id: {sample.id} already registered.",
        )


@router.get(
    "/",
    response_model=list[SampleResponse],
    response_model_exclude={
        "detail": {
            "sex": True,
            "nocalls": True,
            "snps": True,
            "matches": True,
            "mismatches": True,
            "unknown": True,
        },
    },
)
def read_samples(
    skip: int = 0,
    limit: int = Query(default=10, lte=10),
    sample_id: str | None = None,
    plate_id: str | None = None,
    incomplete: bool | None = False,
    commented: bool | None = False,
    status_missing: bool | None = False,
    sample_service: SampleService = Depends(get_sample_service),
    current_user: User = Depends(get_active_user),
):
    """Returns a list of samples matching the provided filters."""
    filter_params = SampleFilterParams(
        sample_id=sample_id,
        plate_id=plate_id,
        is_incomplete=incomplete,
        is_commented=commented,
        is_missing=status_missing,
        skip=skip,
        limit=limit,
    )

    return sample_service.get_samples(filter_params)


@router.put("/{sample_id}/sex")
def update_sex(
    sample_id: str,
    sex: Sexes = Query(...),
    genotype_sex: Sexes | None = None,
    sequence_sex: Sexes | None = None,
    sample_service: SampleService = Depends(get_sample_service),
    current_user: User = Depends(get_active_user),
):
    """Updating sex field on sample and sample analyses."""
    try:
        sample_service.set_sex(
            sample_id=sample_id, sex=sex, genotype_sex=genotype_sex, sequence_sex=sequence_sex
        )
    except SampleNotFoundError:
        return JSONResponse(
            content=f"Could not find sample with id: {sample_id}",
            status_code=HTTPStatus.BAD_REQUEST,
        )


@router.put(
    "/{sample_id}/comment",
    response_model=SampleResponse,
)
def update_comment(
    sample_id: str,
    comment: str = Query(...),
    sample_service: SampleService = Depends(get_sample_service),
    current_user: User = Depends(get_active_user),
):
    """Updating comment field on sample."""
    try:
        return sample_service.set_sample_comment(sample_id=sample_id, comment=comment)
    except SampleNotFoundError:
        return JSONResponse(
            content=f"Could not find sample with id: {sample_id}",
            status_code=HTTPStatus.BAD_REQUEST,
        )


@router.put(
    "/{sample_id}/status",
    response_model=SampleResponse,
)
def set_sample_status(
    sample_id: str,
    sample_service: SampleService = Depends(get_sample_service),
    status: Literal["pass", "fail", "cancel"] | None = None,
    current_user: User = Depends(get_active_user),
):
    """Check sample analyses and update sample status accordingly."""
    try:
        return sample_service.set_sample_status(sample_id=sample_id, status=status)
    except SampleNotFoundError:
        return JSONResponse(
            content=f"Could not find sample with id: {sample_id}",
            status_code=HTTPStatus.BAD_REQUEST,
        )


@router.get("/{sample_id}/match", response_model=list[MatchResult])
def match(
    sample_id: str,
    analysis_type: Types,
    comparison_set: Types,
    date_min: date | None = date.min,
    date_max: date | None = date.max,
    sample_service: SampleService = Depends(get_sample_service),
    current_user: User = Depends(get_active_user),
) -> list[MatchResult]:
    """Match sample genotype against all other genotypes."""
    return sample_service.get_match_results(
        sample_id=sample_id,
        analysis_type=analysis_type,
        comparison_set=comparison_set,
        date_max=date_max,
        date_min=date_min,
    )


@router.get(
    "/{sample_id}/status_detail",
    response_model=SampleDetail,
    deprecated=True,
    response_model_include={"sex": True, "nocalls": True, "snps": True},
)
def get_status_detail(
    sample_id: str,
    sample_service: SampleService = Depends(get_sample_service),
    current_user: User = Depends(get_active_user),
):
    try:
        return sample_service.get_status_detail(sample_id)
    except SampleNotFoundError:
        return JSONResponse(
            content=f"Sample with id: {sample_id} not found.", status_code=HTTPStatus.BAD_REQUEST
        )


@router.delete("/{sample_id}")
def delete_sample(
    sample_id: str,
    sample_service: SampleService = Depends(get_sample_service),
    current_user: User = Depends(get_active_user),
):
    """Delete sample and its Analyses."""
    sample_service.delete_sample(sample_id)
    return JSONResponse(
        content=f"Deleted sample with id: {sample_id}", status_code=status.HTTP_200_OK
    )
