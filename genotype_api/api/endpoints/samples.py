from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session
from sqlmodel.sql.expression import Select, SelectOfScalar
from starlette import status

from genotype_api.database.crud import create, delete
from genotype_api.constants import SEXES, TYPES
from genotype_api.database.crud.read import (
    get_sample,
    get_filtered_samples,
    get_analyses_by_type_between_dates,
    get_analysis_by_type_and_sample_id,
)
from genotype_api.database.crud.update import (
    refresh_sample_status,
    update_sample_comment,
    update_sample_status,
    update_sample_sex,
)
from genotype_api.database.filter_models.sample_models import SampleFilterParams, SampleSexesUpdate
from genotype_api.database.models import (
    Analysis,
    Sample,
    User,
)
from genotype_api.dto.dto import SampleRead, SampleReadWithAnalysisDeep
from genotype_api.database.session_handler import get_session
from genotype_api.models import MatchResult, SampleDetail
from genotype_api.security import get_active_user
from genotype_api.service.match_genotype_service.match_genotype import MatchGenotypeService

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True


router = APIRouter()


@router.get(
    "/{sample_id}",
    response_model=SampleReadWithAnalysisDeep,
    response_model_by_alias=False,
    response_model_exclude={
        "analyses": {"__all__": {"genotypes": True, "source": True, "created_at": True}},
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
def read_sample(
    sample_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    sample: Sample = get_sample(session=session, sample_id=sample_id)
    if len(sample.analyses) == 2 and not sample.status:
        sample: Sample = refresh_sample_status(session=session, sample=sample)
    return sample


@router.get(
    "/",
    response_model=list[SampleReadWithAnalysisDeep],
    response_model_by_alias=False,
    response_model_exclude={
        "analyses": {"__all__": {"genotypes": True, "source": True, "created_at": True}},
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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> list[Sample]:
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
    return get_filtered_samples(session=session, filter_params=filter_params)


@router.post("/", response_model=SampleRead)
def create_sample(
    sample: Sample,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    return create.create_sample(session=session, sample=sample)


@router.put("/{sample_id}/sex", response_model=SampleRead)
def update_sex(
    sample_id: str,
    sex: SEXES = Query(...),
    genotype_sex: SEXES | None = None,
    sequence_sex: SEXES | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Updating sex field on sample and sample analyses."""
    sexes_update = SampleSexesUpdate(
        sample_id=sample_id, sex=sex, genotype_sex=genotype_sex, sequence_sex=sequence_sex
    )
    sample: Sample = update_sample_sex(session=session, sexes_update=sexes_update)
    return sample


@router.put("/{sample_id}/comment", response_model=SampleRead)
def update_comment(
    sample_id: str,
    comment: str = Query(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> Sample:
    """Updating comment field on sample."""
    return update_sample_comment(session=session, sample_id=sample_id, comment=comment)


@router.put("/{sample_id}/status", response_model=SampleRead)
def set_sample_status(
    sample_id: str,
    session: Session = Depends(get_session),
    status: Literal["pass", "fail", "cancel"] | None = None,
    current_user: User = Depends(get_active_user),
) -> Sample:
    """Check sample analyses and update sample status accordingly."""

    return update_sample_status(session=session, sample_id=sample_id, status=status)


@router.get("/{sample_id}/match", response_model=list[MatchResult])
def match(
    sample_id: str,
    analysis_type: TYPES,
    comparison_set: TYPES,
    date_min: date | None = date.min,
    date_max: date | None = date.max,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> list[MatchResult]:
    """Match sample genotype against all other genotypes."""
    analyses: list[Analysis] = get_analyses_by_type_between_dates(
        session=session, analysis_type=comparison_set, date_max=date_max, date_min=date_min
    )
    sample_analysis: Analysis = get_analysis_by_type_and_sample_id(
        session=session, analysis_type=analysis_type, sample_id=sample_id
    )
    matches: list[MatchResult] = MatchGenotypeService.get_matches(
        analyses=analyses, sample_analysis=sample_analysis
    )
    return matches


@router.get(
    "/{sample_id}/status_detail",
    response_model=SampleDetail,
    deprecated=True,
    response_model_include={"sex": True, "nocalls": True, "snps": True},
)
def get_status_detail(
    sample_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    sample: Sample = get_sample(session=session, sample_id=sample_id)
    if len(sample.analyses) != 2:
        return SampleDetail()
    return MatchGenotypeService.check_sample(sample=sample)


@router.delete("/{sample_id}", response_model=Sample)
def delete_sample(
    sample_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Delete sample and its Analyses."""

    sample: Sample = get_sample(session=session, sample_id=sample_id)
    for analysis in sample.analyses:
        delete.delete_analysis(session=session, analysis=analysis)
    delete.delete_sample(session=session, sample=sample)
    return JSONResponse("Deleted", status_code=status.HTTP_200_OK)
