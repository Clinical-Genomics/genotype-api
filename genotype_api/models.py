from typing import List, Optional

from pydantic import BaseModel, validator
from sqlmodel import Field


class PlateStatusCounts(BaseModel):
    total: int = Field(0, nullable=True)
    failed: int = Field(0, alias="STATUS.FAIL", nullable=True)
    passed: int = Field(0, alias="STATUS.PASS", nullable=True)
    cancelled: int = Field(0, alias="STATUS.CANCEL", nullable=True)
    unknown: int = Field(0, alias="None", nullable=True)
    commented: int = Field(0, nullable=True)

    class Config:
        allow_population_by_field_name = True


class SampleDetailStats(BaseModel):
    matches: Optional[int]
    mismatches: Optional[int]
    unknown: Optional[int]


class SampleDetailStatus(BaseModel):
    sex: Optional[str]
    snps: Optional[str]
    nocalls: Optional[str]


class SampleDetail(BaseModel):
    sex: Optional[str]
    snps: Optional[str]
    nocalls: Optional[str]
    matches: Optional[int]
    mismatches: Optional[int]
    unknown: Optional[int]
    failed_snps: Optional[List[str]]

    stats: Optional[SampleDetailStats]
    status: Optional[SampleDetailStatus]

    @validator("stats")
    def validate_stats(cls, value, values) -> SampleDetailStats:
        matches = values.get("matches")
        mismatches = values.get("mismatches")
        unknown = values.get("unknown")
        return SampleDetailStats(matches=matches, mismatches=mismatches, unknown=unknown)

    @validator("status")
    def validate_status(cls, value, values) -> SampleDetailStatus:
        sex = values.get("sex")
        snps = values.get("snps")
        nocalls = values.get("nocalls")
        return SampleDetailStatus(sex=sex, snps=snps, nocalls=nocalls)

    class Config:
        validate_all = True


class MatchCounts(BaseModel):
    match: Optional[int] = 0
    mismatch: Optional[int] = 0
    unknown: Optional[int] = 0


class MatchResult(BaseModel):
    sample_id: str
    match_results: MatchCounts
