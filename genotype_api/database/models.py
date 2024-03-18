from collections import Counter
from datetime import datetime

from pydantic import EmailStr, constr, validator
from sqlalchemy import Index
from sqlmodel import Field, Relationship, SQLModel

from genotype_api.constants import CUTOFS, SEXES, STATUS, TYPES
from genotype_api.models import PlateStatusCounts, SampleDetail


class GenotypeBase(SQLModel):
    rsnumber: constr(max_length=10) | None
    analysis_id: int | None = Field(default=None, foreign_key="analysis.id")
    allele_1: constr(max_length=1) | None
    allele_2: constr(max_length=1) | None


class Genotype(GenotypeBase, table=True):
    __tablename__ = "genotype"
    __table_args__ = (Index("_analysis_rsnumber", "analysis_id", "rsnumber", unique=True),)
    id: int | None = Field(default=None, primary_key=True)

    analysis: "Analysis" = Relationship(back_populates="genotypes")

    @property
    def alleles(self) -> list[str]:
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
    source: str | None
    sex: SEXES | None
    created_at: datetime | None = datetime.now()
    sample_id: constr(max_length=32) | None = Field(default=None, foreign_key="sample.id")
    plate_id: str | None = Field(default=None, foreign_key="plate.id")


class Analysis(AnalysisBase, table=True):
    __tablename__ = "analysis"
    __table_args__ = (Index("_sample_type", "sample_id", "type", unique=True),)
    id: int | None = Field(default=None, primary_key=True)

    sample: "Sample" = Relationship(back_populates="analyses")
    plate: list["Plate"] = Relationship(back_populates="analyses")
    genotypes: list["Genotype"] = Relationship(back_populates="analysis")

    def check_no_calls(self) -> dict[str, int]:
        """Check that genotypes look ok."""
        calls = ["known" if genotype.is_ok else "unknown" for genotype in self.genotypes]
        return Counter(calls)


class AnalysisRead(AnalysisBase):
    id: int


class AnalysisCreate(AnalysisBase):
    pass


class SampleSlim(SQLModel):
    status: STATUS | None
    comment: str | None


class SampleBase(SampleSlim):
    sex: SEXES | None
    created_at: datetime | None = datetime.now()


class Sample(SampleBase, table=True):
    __tablename__ = "sample"
    id: constr(max_length=32) | None = Field(default=None, primary_key=True)

    analyses: list["Analysis"] = Relationship(back_populates="sample")

    @property
    def genotype_analysis(self) -> Analysis | None:
        """Return genotype analysis."""

        for analysis in self.analyses:
            if analysis.type == "genotype":
                return analysis

        return None

    @property
    def sequence_analysis(self) -> Analysis | None:
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
    ref: constr(max_length=1) | None
    chrom: constr(max_length=5) | None
    pos: int | None


class SNP(SNPBase, table=True):
    __tablename__ = "snp"
    """Represent a SNP position under investigation."""

    id: constr(max_length=32) | None = Field(default=None, primary_key=True)


class SNPRead(SNPBase):
    id: constr(max_length=32)


class UserBase(SQLModel):
    email: EmailStr = Field(index=True, unique=True)
    name: str | None = ""


class User(UserBase, table=True):
    __tablename__ = "user"
    id: int | None = Field(default=None, primary_key=True)
    plates: list["Plate"] = Relationship(back_populates="user")


class UserRead(UserBase):
    id: int


class UserCreate(UserBase):
    pass


class PlateBase(SQLModel):
    created_at: datetime | None = datetime.now()
    plate_id: constr(max_length=16) = Field(index=True, unique=True)
    signed_by: int | None = Field(default=None, foreign_key="user.id")
    signed_at: datetime | None
    method_document: str | None
    method_version: str | None


class Plate(PlateBase, table=True):
    __tablename__ = "plate"
    id: int | None = Field(default=None, primary_key=True)
    user: "User" = Relationship(back_populates="plates")
    analyses: list["Analysis"] = Relationship(back_populates="plate")


class PlateRead(PlateBase):
    id: str
    user: UserRead | None


class PlateCreate(PlateBase):
    analyses: list[Analysis] | None = []


class UserReadWithPlates(UserRead):
    plates: list[Plate] | None = []


class SampleReadWithAnalysis(SampleRead):
    analyses: list[AnalysisRead] | None = []


class AnalysisReadWithGenotype(AnalysisRead):
    genotypes: list[Genotype] | None = []


class SampleReadWithAnalysisDeep(SampleRead):
    analyses: list[AnalysisReadWithGenotype] | None = []
    detail: SampleDetail | None

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
        sex = check_sex(
            sample_sex=values.get("sex"),
            genotype_analysis=genotype_analysis,
            sequence_analysis=sequence_analysis,
        )

        return SampleDetail(**status, sex=sex)

    class Config:
        validate_all = True


class AnalysisReadWithSample(AnalysisRead):
    sample: SampleSlim | None


class AnalysisReadWithSampleDeep(AnalysisRead):
    sample: SampleReadWithAnalysisDeep | None


class PlateReadWithAnalyses(PlateRead):
    analyses: list[AnalysisReadWithSample] | None = []


class PlateReadWithAnalysisDetail(PlateRead):
    analyses: list[AnalysisReadWithSample] | None = []
    detail: PlateStatusCounts | None

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
    analyses: list[AnalysisReadWithSample] | None = []
    detail: PlateStatusCounts | None

    @validator("detail")
    def check_detail(cls, value, values):
        analyses = values.get("analyses")
        statuses = [str(analysis.sample.status) for analysis in analyses]
        commented = sum(1 for analysis in analyses if analysis.sample.comment)
        status_counts = Counter(statuses)
        return PlateStatusCounts(**status_counts, total=len(analyses), commented=commented)

    class Config:
        validate_all = True


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
    """Check if any source disagrees on the sex"""
    if not sample_sex or genotype_analysis.sex == SEXES.UNKNOWN:
        return "fail"
    sexes = {genotype_analysis.sex, sequence_analysis.sex, sample_sex}
    if {SEXES.MALE, SEXES.FEMALE}.issubset(sexes):
        return "fail"
    return "pass"
