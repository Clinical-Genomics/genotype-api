from pydantic import BaseModel, field_validator


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

    @field_validator("stats", mode="before")
    def validate_stats(cls, value, data) -> SampleDetailStats:
        matches = data.get("matches")
        mismatches = data.get("mismatches")
        unknown = data.get("unknown")
        return SampleDetailStats(matches=matches, mismatches=mismatches, unknown=unknown)

    @field_validator("status", mode="before")
    def validate_status(cls, value, data) -> SampleDetailStatus:
        sex = data.get("sex")
        snps = data.get("snps")
        nocalls = data.get("nocalls")
        return SampleDetailStatus(sex=sex, snps=snps, nocalls=nocalls)

    model_config = {"validate_assignment": True}


class MatchCounts(BaseModel):
    match: int | None = 0
    mismatch: int | None = 0
    unknown: int | None = 0


class MatchResult(BaseModel):
    sample_id: str
    match_results: MatchCounts | None = None
