from collections import Counter
from datetime import datetime

from pydantic import EmailStr, constr
from sqlalchemy import Index
from sqlmodel import Field, Relationship, SQLModel

from genotype_api.constants import SEXES, STATUS, TYPES


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


class SNPBase(SQLModel):
    ref: constr(max_length=1) | None
    chrom: constr(max_length=5) | None
    pos: int | None


class SNP(SNPBase, table=True):
    __tablename__ = "snp"
    """Represent a SNP position under investigation."""

    id: constr(max_length=32) | None = Field(default=None, primary_key=True)


class UserBase(SQLModel):
    email: EmailStr = Field(index=True, unique=True)
    name: str | None = ""


class User(UserBase, table=True):
    __tablename__ = "user"
    id: int | None = Field(default=None, primary_key=True)
    plates: list["Plate"] = Relationship(back_populates="user")


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
