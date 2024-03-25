from pydantic import BaseModel, validator


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
        validate_all = True


class MatchCounts(BaseModel):
    match: int | None = 0
    mismatch: int | None = 0
    unknown: int | None = 0


class MatchResult(BaseModel):
    sample_id: str
    match_results: MatchCounts
