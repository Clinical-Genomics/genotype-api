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
        validate_default = True


class MatchCounts(BaseModel):
    match: int | None = 0
    mismatch: int | None = 0
    unknown: int | None = 0


class MatchResult(BaseModel):
    sample_id: str
    match_results: MatchCounts | None = None


class RealmAccess(BaseModel):
    roles: list[str]


class DecodingResponse(BaseModel):
    exp: int
    iat: int
    auth_time: int
    jti: str
    iss: str
    sub: str
    typ: str
    azp: str
    sid: str
    acr: str
    allowed_origins: list[str] | None = None
    realm_access: RealmAccess
    scope: str
    email_verified: bool
    name: str
    preferred_username: str
    given_name: str
    family_name: str
    email: str
