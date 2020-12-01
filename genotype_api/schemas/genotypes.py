"""Genotype schemas"""

from pydantic import BaseModel


class GenotypeBase(BaseModel):
    rsnumber: str
    allele_1: str
    allele_2: str


class GenotypeCreate(GenotypeBase):
    pass


class Genotype(GenotypeBase):
    id: int
    analysis_id: int

    class Config:
        orm_mode = True
