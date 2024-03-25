"""Module for the plate DTOs."""

from collections import Counter
from datetime import datetime

from pydantic import BaseModel, validator, Field
from genotype_api.dto.analysis import AnalysisSampleResponse
from genotype_api.dto.user import UserInfoResponse


class PlateStatusCounts(BaseModel):
    total: int = Field(0, nullable=True)
    failed: int = Field(0, alias="STATUS.FAIL", nullable=True)
    passed: int = Field(0, alias="STATUS.PASS", nullable=True)
    cancelled: int = Field(0, alias="STATUS.CANCEL", nullable=True)
    unknown: int = Field(0, alias="None", nullable=True)
    commented: int = Field(0, nullable=True)

    class Config:
        allow_population_by_field_name = True


class PlateSimple(BaseModel):

    created_at: datetime | None = None
    plate_id: str | None = None
    signed_by: int | None = None
    signed_at: datetime | None = None
    method_document: str | None = None
    method_version: str | None = None
    id: str | None = None
    user: UserInfoResponse | None = None


class PlateResponse(BaseModel):
    created_at: datetime | None = None
    plate_id: str | None = None
    signed_by: int | None = None
    signed_at: datetime | None = None
    method_document: str | None = None
    method_version: str | None = None
    id: str | None = None
    user: UserInfoResponse | None = None
    analyses: list[AnalysisSampleResponse] | None = None
    detail: PlateStatusCounts | None = None

    @validator("detail")
    def check_detail(cls, value, values):
        analyses = values.get("analyses")
        if not analyses:
            return None
        statuses = [str(analysis.sample.status) for analysis in analyses]
        commented = sum(1 for analysis in analyses if analysis.sample.comment)
        status_counts = Counter(statuses)
        return PlateStatusCounts(**status_counts, total=len(analyses), commented=commented)

    class Config:
        validate_all = True
