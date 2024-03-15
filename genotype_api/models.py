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
        populate_by_name = True


class SampleDetailStats(BaseModel):
    matches: int | None
    mismatches: int | None
    unknown: int | None


class SampleDetailStatus(BaseModel):
    sex: str | None
    snps: str | None
    nocalls: str | None


class SampleDetail(BaseModel):
    sex: str | None
    snps: str | None
    nocalls: str | None
    matches: int | None
    mismatches: int | None
    unknown: int | None
    failed_snps: list[str] | None

    stats: SampleDetailStats | None
    status: SampleDetailStatus | None

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
        validate_default = True


class MatchCounts(BaseModel):
    match: int | None = 0
    mismatch: int | None = 0
    unknown: int | None = 0


class MatchResult(BaseModel):
    sample_id: str
    match_results: MatchCounts
