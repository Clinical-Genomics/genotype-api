from datetime import datetime
from typing import Optional, List, Dict, Tuple, Type, Any
from collections import Counter


from pydantic import constr, EmailStr, BaseModel, validator
from sqlmodel import SQLModel, Field, Relationship

from genotype_api.constants import TYPES, SEXES, STATUS, CUTOFS


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
    matches: Optional[int] = 0
    mismatches: Optional[int] = 0
    unknown: Optional[int] = 0


class SampleDetailStatus(BaseModel):
    sex: Optional[str] = None
    snps: Optional[str] = None
    nocalls: Optional[str] = None


class SampleDetail(BaseModel):
    sex: Optional[str] = None
    snps: Optional[str] = None
    nocalls: Optional[str] = None
    matches: Optional[int] = 0
    mismatches: Optional[int] = 0
    unknown: Optional[int] = 0
    failed_snps: Optional[List[str]] = []

    stats: Optional[SampleDetailStats] = SampleDetailStats()
    status: Optional[SampleDetailStatus] = SampleDetailStatus()

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


class GenotypeBase(SQLModel):
    rsnumber: Optional[constr(max_length=10)]
    analysis_id: Optional[int] = Field(default=None, foreign_key="analysis.id")
    allele_1: Optional[constr(max_length=1)]
    allele_2: Optional[constr(max_length=1)]


class Genotype(GenotypeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    analysis: Optional["Analysis"] = Relationship(back_populates="genotypes")

    @property
    def alleles(self) -> List[str]:
        """Return sorted because we are not dealing with phased data."""

        return sorted([self.allele_1, self.allele_2])

    @property
    def is_ok(self) -> bool:
        """Check that the allele determination is ok."""
        return "0" not in self.alleles


class GenotypeRead(GenotypeBase):
    id: int


class GenotypeCreate(GenotypeBase):
    pass


class AnalysisBase(SQLModel):
    type: TYPES
    source: Optional[str]
    sex: Optional[SEXES]
    created_at: Optional[datetime] = datetime.now()
    sample_id: Optional[constr(max_length=32)] = Field(default=None, foreign_key="sample.id")
    plate_id: Optional[str] = Field(default=None, foreign_key="plate.id")


class Analysis(AnalysisBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    sample: Optional["Sample"] = Relationship(back_populates="analyses")
    plate: Optional[List["Plate"]] = Relationship(back_populates="analyses")
    genotypes: Optional[List["Genotype"]] = Relationship(back_populates="analysis")

    def check_no_calls(self) -> Dict[str, int]:
        """Check that genotypes look ok."""
        calls = ["known" if genotype.is_ok else "unknown" for genotype in self.genotypes]
        return Counter(calls)


class AnalysisRead(AnalysisBase):
    id: int


class AnalysisCreate(AnalysisBase):
    pass


class SampleSlim(SQLModel):
    status: Optional[STATUS]
    comment: Optional[str]


class SampleBase(SampleSlim):
    sex: Optional[SEXES]
    created_at: Optional[datetime] = datetime.now()


class Sample(SampleBase, table=True):
    id: Optional[constr(max_length=32)] = Field(default=None, primary_key=True)

    analyses: Optional[List["Analysis"]] = Relationship(back_populates="sample")

    @property
    def genotype_analysis(self) -> Optional[Analysis]:
        """Return genotype analysis."""

        for analysis in self.analyses:
            if analysis.type == "genotype":
                return analysis

        return None

    @property
    def sequence_analysis(self) -> Optional[Analysis]:
        """Return sequence analysis."""

        for analysis in self.analyses:
            if analysis.type == "sequence":
                return analysis

        return None


class SampleRead(SampleBase):
    id: constr(max_length=32)


class SampleCreate(SampleBase):
    pass


class SNPBase(SQLModel):
    ref: Optional[constr(max_length=1)]
    chrom: Optional[constr(max_length=5)]
    pos: Optional[int]


class SNP(SNPBase, table=True):
    """Represent a SNP position under investigation."""

    id: Optional[constr(max_length=32)] = Field(default=None, primary_key=True)


class SNPRead(SNPBase):
    id: constr(max_length=32)


class UserBase(SQLModel):
    email: EmailStr = Field(index=True)
    name: Optional[str] = ""


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plates: Optional[List["Plate"]] = Relationship(back_populates="user")


class UserRead(UserBase):
    id: int


class UserCreate(UserBase):
    pass


class PlateBase(SQLModel):

    created_at: Optional[datetime] = datetime.now()
    plate_id: constr(max_length=16)
    signed_by: Optional[int] = Field(default=None, foreign_key="user.id")
    signed_at: Optional[datetime]
    method_document: Optional[int] = 1477
    method_version: Optional[int]


class Plate(PlateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: Optional["User"] = Relationship(back_populates="plates")
    analyses: Optional[List["Analysis"]] = Relationship(back_populates="plate")


class PlateRead(PlateBase):
    id: str
    user: Optional[UserRead]


class PlateCreate(PlateBase):
    analyses: Optional[List[Analysis]] = []


class UserReadWithPlates(UserRead):
    plates: Optional[List[Plate]] = []


class SampleReadWithAnalysis(SampleRead):
    analyses: Optional[List[AnalysisRead]] = []


class AnalysisReadWithGenotype(AnalysisRead):
    genotypes: Optional[List[Genotype]] = []


class SampleReadWithAnalysisDeep(SampleRead):
    analyses: Optional[List[AnalysisReadWithGenotype]] = []
    detail: Optional[SampleDetail]

    @validator("detail")
    def get_detail(cls, value, values) -> SampleDetail:
        analyses = values.get("analyses")
        if len(analyses) != 2:
            return SampleDetail()
        genotype_analysis = [analysis for analysis in analyses if analysis.type == "genotype"][0]
        sequence_analysis = [analysis for analysis in analyses if analysis.type == "sequence"][0]
        status = check_snps(
            genotype_analysis=genotype_analysis, sequence_analysis=sequence_analysis
        )
        status.update(
            {
                "sex": check_sex(
                    sample_sex=values.get("sex"),
                    genotype_analysis=genotype_analysis,
                    sequence_analysis=sequence_analysis,
                )
            }
        )

        return SampleDetail(**status)

    class Config:
        validate_all = True


class AnalysisReadWithSample(AnalysisRead):
    sample: Optional[SampleSlim]


def compare_genotypes(genotype_1: Genotype, genotype_2: Genotype) -> Tuple[str, str]:
    """Compare two genotypes if they have the same alleles."""

    if "0" in genotype_1.alleles or "0" in genotype_2.alleles:
        return genotype_1.rsnumber, "unknown"
    elif genotype_1.alleles == genotype_2.alleles:
        return genotype_1.rsnumber, "match"
    else:
        return genotype_1.rsnumber, "mismatch"


def check_snps(genotype_analysis, sequence_analysis):
    genotype_pairs = zip(genotype_analysis.genotypes, sequence_analysis.genotypes)
    results = dict(
        compare_genotypes(genotype_1, genotype_2) for genotype_1, genotype_2 in genotype_pairs
    )
    count = Counter([val for key, val in results.items()])
    unknown = count.get("unknown", 0)
    matches = count.get("match", 0)
    mismatches = count.get("mismatch", 0)
    snps = (
        "pass"
        if all([matches >= CUTOFS.get("min_matches") and mismatches <= CUTOFS.get("max_mismatch")])
        else "fail"
    )
    nocalls = "pass" if unknown <= CUTOFS.get("max_nocalls") else "fail"
    failed_snps = [key for key, val in results.items() if val == "mismatch"]

    return {
        "unknown": unknown,
        "matches": matches,
        "mismatches": mismatches,
        "snps": snps,
        "nocalls": nocalls,
        "failed_snps": failed_snps,
    }


def check_sex(sample_sex, genotype_analysis, sequence_analysis):
    if sample_sex in ["unknown", None]:
        return "fail"
    elif genotype_analysis.sex == sequence_analysis.sex == sample_sex:
        return "pass"
    return "fail"


class AnalysisReadWithSampleDeep(AnalysisRead):
    sample: Optional[SampleReadWithAnalysisDeep]


class PlateReadWithAnalyses(PlateRead):
    analyses: Optional[List[AnalysisReadWithSample]] = []


class PlateReadWithAnalysisDetail(PlateRead):
    analyses: Optional[List[AnalysisReadWithSample]] = []
    detail: Optional[PlateStatusCounts]

    @validator("detail")
    def check_detail(cls, value, values):
        analyses = values.get("analyses")
        statuses = [str(analysis.sample.status) for analysis in analyses]
        commented = sum(1 for analysis in analyses if analysis.sample.comment)
        status_counts = Counter(statuses)
        return PlateStatusCounts(**status_counts, total=len(analyses), commented=commented)

    class Config:
        validate_all = True


class PlateReadWithAnalysisDetailSingle(PlateRead):
    analyses: Optional[List[AnalysisReadWithSample]] = []
    detail: Optional[PlateStatusCounts]

    @validator("detail")
    def check_detail(cls, value, values):
        analyses = values.get("analyses")
        statuses = [str(analysis.sample.status) for analysis in analyses]
        commented = sum(1 for analysis in analyses if analysis.sample.comment)
        status_counts = Counter(statuses)
        return PlateStatusCounts(**status_counts, total=len(analyses), commented=commented)

    class Config:
        validate_all = True


class MatchCounts(BaseModel):
    match: Optional[int] = 0
    mismatch: Optional[int] = 0
    unknown: Optional[int] = 0


class MatchResult(BaseModel):
    sample_id: str
    match_results: MatchCounts
