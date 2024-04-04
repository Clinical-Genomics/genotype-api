"""Module for the plate DTOs."""

from collections import Counter
from datetime import datetime

from pydantic import BaseModel, validator, Field, EmailStr

from genotype_api.constants import Types, Sexes, Status


class PlateStatusCounts(BaseModel):
    total: int = Field(0, nullable=True)
    failed: int = Field(0, alias="Status.FAIL", nullable=True)
    passed: int = Field(0, alias="Status.PASS", nullable=True)
    cancelled: int = Field(0, alias="Status.CANCEL", nullable=True)
    unknown: int = Field(0, alias="None", nullable=True)
    commented: int = Field(0, nullable=True)

    class Config:
        allow_population_by_field_name = True


class UserOnPlate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    id: int | None = None


class SampleStatus(BaseModel):
    status: Status | None = None
    comment: str | None = None


class AnalysisOnPlate(BaseModel):
    type: Types | None
    source: str | None
    sex: Sexes | None
    created_at: datetime | None
    sample_id: str | None
    plate_id: str | None
    id: int | None
    sample: SampleStatus | None = None


class PlateResponse(BaseModel):
    created_at: datetime | None = None
    plate_id: str | None = None
    signed_by: int | None = None
    signed_at: datetime | None = None
    method_document: str | None = None
    method_version: str | None = None
    id: str | None = None
    user: UserOnPlate | None = None
    analyses: list[AnalysisOnPlate] | None = None
    plate_status_counts: PlateStatusCounts | None = None

    @validator("plate_status_counts")
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
