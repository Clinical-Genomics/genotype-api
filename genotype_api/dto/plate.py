"""Module for the plate DTOs."""

from collections import Counter
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


class PlateResponse(BaseModel):
    created_at: str
    plate_id: str
    signed_by: int
    signed_at: str
    method_document: str
    method_version: str
    id: str
    user: UserInfoResponse
    analyses: list[AnalysisSampleResponse] = []
    detail: PlateStatusCounts

    @validator("detail")
    def check_detail(self, values):
        analyses = values.get("analyses")
        statuses = [str(analysis.sample.status) for analysis in analyses]
        commented = sum(1 for analysis in analyses if analysis.sample.comment)
        status_counts = Counter(statuses)
        return PlateStatusCounts(**status_counts, total=len(analyses), commented=commented)

    class Config:
        validate_all = True
