from collections import Counter
from datetime import date, timedelta
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from sqlmodel.sql.expression import Select, SelectOfScalar
from starlette import status

import genotype_api.database.crud.create
from genotype_api.constants import SEXES
from genotype_api.database.crud.read import (get_commented_samples,
                                             get_incomplete_samples,
                                             get_plate_samples, get_sample,
                                             get_samples,
                                             get_status_missing_samples)
from genotype_api.database.crud.update import refresh_sample_status
from genotype_api.database.models import (Analysis, Sample, SampleRead,
                                          SampleReadWithAnalysisDeep, User,
                                          compare_genotypes)
from genotype_api.database.session_handler import get_session
from genotype_api.match import check_sample
from genotype_api.models import MatchCounts, MatchResult, SampleDetail
from genotype_api.security import get_active_user

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
    sample_id: Optional[str] = None,
    plate_id: Optional[str] = None,
    incomplete: Optional[bool] = False,
    commented: Optional[bool] = False,
    status_missing: Optional[bool] = False,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> list[Sample]:
    """Returns a list of samples matching the provided filters."""
    statement: SelectOfScalar = select(Sample).distinct().join(Analysis)
    if sample_id:
        statement: SelectOfScalar = get_samples(statement=statement, sample_id=sample_id)
    if plate_id:
        statement: SelectOfScalar = get_plate_samples(statement=statement, plate_id=plate_id)
    if incomplete:
        statement: SelectOfScalar = get_incomplete_samples(statement=statement)
    if commented:
        statement: SelectOfScalar = get_commented_samples(statement=statement)
    if status_missing:
        statement: SelectOfScalar = get_status_missing_samples(statement=statement)
    return session.exec(
        statement.order_by(Sample.created_at.desc()).offset(skip).limit(limit)
    ).all()


@router.post("/", response_model=SampleRead)
def create_sample(
    sample: Sample,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    return genotype_api.database.database.crud.create.create_sample(session=session, sample=sample)


@router.put("/{sample_id}/sex", response_model=SampleRead)
def update_sex(
    sample_id: str,
    sex: SEXES = Query(...),
    genotype_sex: Optional[SEXES] = None,
    sequence_sex: Optional[SEXES] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Updating sex field on sample and sample analyses."""

    sample_in_db: Sample = get_sample(session=session, sample_id=sample_id)
    sample_in_db.sex = sex
    for analysis in sample_in_db.analyses:
        if genotype_sex and analysis.type == "genotype":
            analysis.sex = genotype_sex
        elif sequence_sex and analysis.type == "sequence":
            analysis.sex = sequence_sex
        session.add(analysis)
    session.add(sample_in_db)
    session.commit()
    session.refresh(sample_in_db)
    sample_in_db: Sample = refresh_sample_status(session=session, sample=sample_in_db)
    return sample_in_db


@router.put("/{sample_id}/comment", response_model=SampleRead)
def update_comment(
    sample_id: str,
    comment: str = Query(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Updating comment field on sample."""

    sample_in_db: Sample = get_sample(session=session, sample_id=sample_id)
    sample_in_db.comment = comment
    session.add(sample_in_db)
    session.commit()
    session.refresh(sample_in_db)
    return sample_in_db


@router.put("/{sample_id}/status", response_model=SampleRead)
def set_sample_status(
    sample_id: str,
    session: Session = Depends(get_session),
    status: Optional[Literal["pass", "fail", "cancel"]] = None,
    current_user: User = Depends(get_active_user),
):
    """Check sample analyses and update sample status accordingly."""

    sample: Sample = get_sample(session=session, sample_id=sample_id)
    sample.status = status
    session.add(sample)
    session.commit()
    session.refresh(sample)
    return sample


@router.get("/{sample_id}/match", response_model=list[MatchResult])
def match(
    sample_id: str,
    analysis_type: Literal["genotype", "sequence"],
    comparison_set: Literal["genotype", "sequence"],
    date_min: Optional[date] = date.min,
    date_max: Optional[date] = date.max,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> list[MatchResult]:
    """Match sample genotype against all other genotypes."""

    all_genotypes: Analysis = session.query(Analysis).filter(
        Analysis.type == comparison_set,
        Analysis.created_at > date_min - timedelta(days=1),
        Analysis.created_at < date_max + timedelta(days=1),
    )
    genotype_checked = (
        session.query(Analysis).filter(
            Analysis.sample_id == sample_id, Analysis.type == analysis_type
        )
    ).one()

    match_results = []
    for genotype in all_genotypes:
        genotype_pairs = zip(genotype.genotypes, genotype_checked.genotypes)
        results = dict(
            compare_genotypes(genotype_1, genotype_2) for genotype_1, genotype_2 in genotype_pairs
        )
        count = Counter([val for key, val in results.items()])
        if count.get("match", 0) + count.get("unknown", 0) > 40:
            match_results.append(
                MatchResult(
                    sample_id=genotype.sample_id,
                    match_results=MatchCounts.parse_obj(count),
                ),
            )
    return match_results


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
    return check_sample(sample=sample)


@router.delete("/{sample_id}", response_model=Sample)
def delete_sample(
    sample_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Delete sample and its Analyses."""

    sample: Sample = get_sample(session=session, sample_id=sample_id)
    for analysis in sample.analyses:
        session.delete(analysis)
    session.delete(sample)
    session.commit()
    return JSONResponse("Deleted", status_code=status.HTTP_200_OK)
