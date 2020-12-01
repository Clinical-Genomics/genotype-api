from collections import Counter
from datetime import datetime
from typing import Dict, List

from genotype_api.constants import SEXES, TYPES
from genotype_api.database import Base
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint


class Plate(Base):

    """Describe a MAF plate of samples and it's status."""

    __tablename__ = "plates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now())
    plate_id = Column(String(16), unique=True, nullable=False)

    signed_by = Column(ForeignKey("users.id"))
    signed_at = Column(DateTime)
    method_document = Column(Integer, default=1477)
    method_version = Column(Integer)

    analyses = relationship("Analysis", backref="plate")

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


class Analysis(Base):
    """Represent a SNP analysis

    The analysis can by any of (genotyping, sequencing).

    Attributes:
        type (str): 'sequence' or 'genotype'
        source (str): where the genotypes originated from
        sex (str): prediction of 'male', 'female', or 'unknown'
        sample (Sample): related sample object
        genotypes (List[Genotype]): related genotypes from the analysis
    """

    __tablename__ = "analysis"
    __table_args__ = (UniqueConstraint("sample_id", "type", name="_sample_type"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(*TYPES), nullable=False)
    source = Column(Text())
    sex = Column(Enum(*SEXES))
    created_at = Column(DateTime, default=datetime.now())

    sample_id = Column(String(32), ForeignKey("samples.id"))
    plate_id = Column(ForeignKey("plates.id"))

    genotypes = relationship(
        "Genotype", order_by="Genotype.rsnumber", cascade="all,delete", backref="analysis"
    )

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
        counter = Counter(calls)
        return counter


class Genotype(Base):

    """Represent a genotype call for a position.

    Attributes:
        rsnumber (str): SNP id
        analysis (Analysis): related Analysis model
        allele_1 (str): first allele base
        allele_2 (str): second allele base
    """

    __tablename__ = "genotypes"
    __table_args__ = (UniqueConstraint("analysis_id", "rsnumber", name="_analysis_rsnumber"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    rsnumber = Column(String(10))
    analysis_id = Column(Integer, ForeignKey("analysis.id"))
    allele_1 = Column(String(1))
    allele_2 = Column(String(1))

    @property
    def alleles(self) -> List[str]:
        """Return sorted because we are not dealing with phased data."""
        alleles = sorted([self.allele_1, self.allele_2])
        return alleles

    def __str__(self) -> str:
        """Stringify genotype."""
        return "{}{}".format(*self.alleles)

    def __repr__(self):
        return f"<Genotype {self.id}>"


class Sample(Base):

    """Represent a sample.

    Attributes:
        id (str): unique sample id
        status (str): status of sample comparison
        comment (str): comments about pass/fail, also stores overwrites
    """

    __tablename__ = "samples"

    id = Column(String(32), primary_key=True)
    status = Column(Enum("pass", "fail", "cancel"))
    comment = Column(Text(convert_unicode=True))
    sex = Column(Enum(*SEXES))
    created_at = Column(DateTime, default=datetime.now())

    analyses = relationship("Analysis", cascade="all,delete", backref="sample")

    def __str__(self):
        """Stringify sample record."""
        parts = [self.id, self.status or "[status]", self.sex or "[sex]"]
        return "\t".join(parts)

    def __repr__(self):
        return f"<Sample {self.id}>"


class SNP(Base):
    """Represent a SNP position under investigation."""

    __tablename__ = "snps"

    id = Column(String(32), primary_key=True)
    ref = Column(String(1))
    chrom = Column(String(5))
    pos = Column(Integer)

    def __str__(self):
        return f"{self.id}|{self.ref}|{self.chrom}|{self.pos}"

    def __repr__(self):
        return f"<SNP {self.id}>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
