from datetime import datetime
from typing import Optional, List, Dict
from collections import Counter


from pydantic import constr, EmailStr, BaseModel, validator
from sqlmodel import SQLModel, Field, Relationship

from genotype_api.constants import TYPES, SEXES, STATUS


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
    pass


class UserReadWithPlates(UserRead):
    plates: Optional[List[Plate]] = []


class AnalysisReadWithSample(AnalysisRead):
    sample: Optional[SampleSlim]


class PlateReadWithAnalyses(PlateRead):
    analyses: Optional[List[AnalysisReadWithSample]] = []


class SampleReadWithAnalysis(SampleRead):
    analyses: Optional[List[AnalysisRead]] = []


class AnalysisReadWithGenotype(AnalysisRead):
    genotypes: Optional[List[Genotype]] = []


class StatusDetail(BaseModel):
    sex: Optional[str]
    snps: Optional[str]
    nocalls: Optional[str]
