from pydantic import BaseModel, validator


class SampleDetailStats(BaseModel):
    matches: int | None = None
    mismatches: int | None = None
    unknown: int | None = None


class SampleDetailStatus(BaseModel):
    sex: str | None = None
    snps: str | None = None
    nocalls: str | None = None


class SampleDetail(BaseModel):
    sex: str | None = None
    snps: str | None = None
    nocalls: str | None = None
    matches: int | None = None
    mismatches: int | None = None
    unknown: int | None = None
    failed_snps: list[str] | None = None

    stats: SampleDetailStats | None = None
    status: SampleDetailStatus | None = None

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
    match: int | None = 0
    mismatch: int | None = 0
    unknown: int | None = 0


class MatchResult(BaseModel):
    sample_id: str = None
    match_results: MatchCounts | None = None
