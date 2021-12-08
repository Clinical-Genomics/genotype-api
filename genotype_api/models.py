from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional
from constants import SEXES, TYPES, STATUS
from pydantic import constr
from sqlmodel import Field, Relationship, SQLModel


class Plate(SQLModel, table=True):
    """Describe a MAF plate of samples and it's status."""

    __tablename__ = "plates"
    id: Optional[str] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = datetime.now()
    plate_id: constr(max_length=16)
    signed_by: Optional[int] = Field(default=None, foreign_key="users.id")
    signed_at: Optional[datetime]
    method_document: Optional[int] = 1477
    method_version: Optional[int]
    analyses: Optional[List["Analysis"]] = Relationship(back_populates="plate")

    @property
    def percent_done(self) -> float:
        """Calculate percent of samples completed."""
        all_samples = self.analyses
        all_samples_count = len(all_samples)
        done_samples = [
            analysis for analysis in all_samples if analysis.sample.status in ("pass", "cancel")
        ]
        done_samples_count = len(done_samples)
        return done_samples_count / all_samples_count * 100


class Analysis(SQLModel, table=True):
    """Represent a SNP analysis"""

    # __table_args__ = (UniqueConstraint("sample_id", "type", name="_sample_type"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    type: TYPES
    source: Optional[str]
    sex: Optional[SEXES]
    created_at: Optional[datetime] = datetime.now()
    sample_id: Optional[constr(max_length=32)] = Field(default=None, foreign_key="samples.id")

    plate_id: Optional[str] = Field(default=None, foreign_key="plates.id")
    plate: Optional[List["Plate"]] = Relationship(back_populates="analyses")

    genotypes: Optional[List["Genotype"]] = Relationship(back_populates="analysis")

    def __str__(self):
        """Stringify genotypes."""
        genotypes = [str(genotype) for genotype in self.genotypes]
        parts = [self.sample_id, self.type, self.sex or "[sex]"] + genotypes
        return "\t".join(parts)

    def __repr__(self):
        return f"<Analysis {self.id}>"

    def check(self) -> Dict[str, int]:
        """Check that genotypes look okey."""
        calls = ["known" if genotype.is_ok else "unknown" for genotype in self.genotypes]
        return Counter(calls)


class Genotype(SQLModel, table=True):
    """Represent a genotype call for a position."""

    __tablename__ = "genotypes"
    #    __table_args__ = (UniqueConstraint("analysis_id", "rsnumber", name="_analysis_rsnumber"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    rsnumber: Optional[constr(max_length=10)]
    analysis_id: Optional[int] = Field(default=None, foreign_key="analysis.id")
    allele_1: Optional[constr(max_length=1)]
    allele_2: Optional[constr(max_length=1)]

    @property
    def alleles(self) -> List[str]:
        """Return sorted because we are not dealing with phased data."""
        return sorted([self.allele_1, self.allele_2])

    def __str__(self) -> str:
        """Stringify genotype."""
        return "{}{}".format(*self.alleles)

    def __repr__(self):
        return f"<Genotype {self.id}>"


class Sample(SQLModel, table=True):
    """Represent a sample.
    Attributes:
        id (str): unique sample id
        status (str): status of sample comparison
        comment (str): comments about pass/fail, also stores overwrites
    """

    __tablename__ = "samples"

    id: Optional[constr(max_length=32)] = Field(default=None, primary_key=True)
    status: Optional[STATUS]
    comment: Optional[str]
    sex: Optional[SEXES]
    created_at: Optional[datetime] = datetime.now()

    #analyses = Relationship(back_populates="sample")

    def __str__(self):
        """Stringify sample record."""
        parts = [self.id, self.status or "[status]", self.sex or "[sex]"]
        return "\t".join(parts)

    def __repr__(self):
        return f"<Sample {self.id}>"


class SNP(SQLModel, table=True):
    """Represent a SNP position under investigation."""

    __tablename__ = "snps"

    id: Optional[constr(max_length=32)] = Field(default=None, primary_key=True)
    ref: Optional[constr(max_length=1)]
    chrom: Optional[constr(max_length=5)]
    pos: Optional[int]

    def __str__(self):
        return f"{self.id}|{self.ref}|{self.chrom}|{self.pos}"

    def __repr__(self):
        return f"<SNP {self.id}>"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: Optional[str] = Field(index=True)
    hashed_password: Optional[str]
    is_active: Optional[bool] = True
