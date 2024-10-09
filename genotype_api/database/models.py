from collections import Counter
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy_utils import EmailType


class Base(DeclarativeBase):
    pass


class Genotype(Base):
    __tablename__ = "genotype"

    id = Column(Integer, primary_key=True)
    rsnumber = Column(String(length=10))
    analysis_id = Column(Integer, ForeignKey("analysis.id"))
    allele_1 = Column(String(length=1))
    allele_2 = Column(String(length=1))

    analysis = relationship("Analysis", back_populates="genotypes")

    @property
    def alleles(self):
        return sorted([self.allele_1, self.allele_2])

    @property
    def is_ok(self):
        return "0" not in self.alleles


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True)
    type = Column(String)
    source = Column(String)
    sex = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    sample_id = Column(String(length=32), ForeignKey("sample.id"))
    plate_id = Column(Integer, ForeignKey("plate.id"))

    sample = relationship("Sample", back_populates="analyses")
    plate = relationship("Plate", back_populates="analyses")
    genotypes = relationship("Genotype", back_populates="analysis")

    def check_no_calls(self):
        calls = ["known" if genotype.is_ok else "unknown" for genotype in self.genotypes]
        return Counter(calls)


class Sample(Base):
    __tablename__ = "sample"

    id = Column(String(length=32), primary_key=True)
    status = Column(String)
    comment = Column(String)
    sex = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    analyses = relationship("Analysis", back_populates="sample")

    @property
    def genotype_analysis(self):
        for analysis in self.analyses:
            if analysis.type == "genotype":
                return analysis
        return None

    @property
    def sequence_analysis(self):
        for analysis in self.analyses:
            if analysis.type == "sequence":
                return analysis
        return None


class SNP(Base):
    __tablename__ = "snp"

    id = Column(String(length=32), primary_key=True)
    ref = Column(String(length=1))
    chrom = Column(String(length=5))
    pos = Column(Integer)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(EmailType, unique=True, index=True)
    name = Column(String, default="")

    plates = relationship("Plate", back_populates="user")


class Plate(Base):
    __tablename__ = "plate"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    plate_id = Column(String(length=16), unique=True, index=True)
    signed_by = Column(Integer, ForeignKey("user.id"))
    signed_at = Column(DateTime)
    method_document = Column(String)
    method_version = Column(String)

    user = relationship("User", back_populates="plates")
    analyses = relationship("Analysis", back_populates="plate")
